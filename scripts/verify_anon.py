#!/usr/bin/env python3
"""
Verificador Automatizado em 4 Níveis (Validation Gates) para o Experimento de Anonimização (op_x).

Executa os 4 Gates científicos sobre o método anonimizado `compute_pipeline` (`op_x.c`),
verificando tanto a equivalência numérica com a versão sequencial `op_x` quanto a equivalência
cruzada bit-a-bit com o kernel original `2mm` do PolyBench/C:
  [Gate 1] Imutabilidade Estrita do Código C (Zero-Mutation / C-Token Equivalence sem #pragma omp)
  [Gate 2] Presença Efetiva de Paralelismo em `compute_pipeline` (Pragmas no alvo vs. fora do alvo)
  [Gate 3] Compilabilidade Estrita Pass@1 (GCC -O3 -fopenmp)
  [Gate 4] Corretude Numérica Determinística (-DSMALL_DATASET -DPOLYBENCH_DUMP_ARRAYS, 4 threads)

Uso:
  python3 scripts/verify_anon.py
  python3 scripts/verify_anon.py --save results/verificacao_anon.csv
"""

import argparse
import csv
import math
import os
import platform
import re
import subprocess
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
POLY_UTILS_DIR = BASE_DIR / "core" / "polybench-c-3.2" / "utilities"
POLY_SRC = POLY_UTILS_DIR / "polybench.c"
ANON_DIR = BASE_DIR / "core" / "anonymized" / "op_x"
ANON_OPENMP_FILE = BASE_DIR / "core" / "anonymized" / "openmp" / "op_x" / "op_x.c"
ORIG_2MM_DIR = BASE_DIR / "core" / "polybench-c-3.2" / "linear-algebra" / "kernels" / "2mm"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

NON_QUANT_MODELS = [
    "codestral_22b",
    "granite-code-20b",
    "qwen-2.5-coder-14b",
    "starcode-2_15b",
    "deepseekcoder-coder-v2_16b",
    "codellama_13b",
]

QUANT_MODELS = [
    "codestral-openmp_16b",
    "codestral-openmp_8b",
    "codestral-openmp_4b",
    "codestral-openmp_3b",
]

DEFAULT_MODELS = ["openmp"] + NON_QUANT_MODELS + QUANT_MODELS
DEFAULT_OUTPUT_CSV = RESULTS_DIR / "verificacao_anon.csv"


def strip_omp_pragmas(code: str) -> str:
    lines = code.splitlines()
    out = []
    skip_continuation = False
    for line in lines:
        if skip_continuation:
            if not line.rstrip().endswith("\\"):
                skip_continuation = False
            continue
        if re.match(r"^\s*#\s*pragma\s+omp\b", line):
            if line.rstrip().endswith("\\"):
                skip_continuation = True
            continue
        out.append(line)
    return "\n".join(out)


def strip_c_comments(code: str) -> str:
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(
        pattern,
        lambda m: "" if m.group(0).startswith("/") else m.group(0),
        code,
    )


def tokenize_c_code(code: str) -> list[str]:
    no_omp = strip_omp_pragmas(code)
    no_comments = strip_c_comments(no_omp)

    tokens: list[str] = []
    for line in no_comments.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            norm_dir = re.sub(r"\s+", " ", stripped)
            tokens.append(norm_dir)
        else:
            line_tokens = re.findall(
                r'"(?:\\.|[^\\"])*"|\'(?:\\.|[^\\\'])*\'|[A-Za-z_]\w*|\d+\.\d*|\.\d+|\d+|==|!=|<=|>=|\+=|-=|\*=|/=|\+\+|--|&&|\|\||->|[+\-*/%=<>!&|^~?:;,(){}\[\]]',
                stripped,
            )
            tokens.extend(line_tokens)
    return tokens


def check_gate1_immutability(orig_code: str, gen_code: str) -> tuple[bool, str]:
    orig_tokens = tokenize_c_code(orig_code)
    gen_tokens = tokenize_c_code(gen_code)

    if orig_tokens == gen_tokens:
        return True, "100% preservado (0 mutacoes C)"

    min_len = min(len(orig_tokens), len(gen_tokens))
    for idx in range(min_len):
        if orig_tokens[idx] != gen_tokens[idx]:
            return (
                False,
                f"Mutacao no token #{idx}: esperado '{orig_tokens[idx]}', obtido '{gen_tokens[idx]}'",
            )
    return (
        False,
        f"Diferenca de tamanho lexico: orig={len(orig_tokens)} vs gen={len(gen_tokens)} tokens",
    )


def check_gate2_pragmas(gen_code: str) -> tuple[bool, int, int, str, str]:
    all_pragmas = re.findall(r"^\s*#\s*pragma\s+omp\b.*$", gen_code, flags=re.MULTILINE)
    total_count = len(all_pragmas)

    kernel_count = 0
    kernel_pragmas: list[str] = []
    fn_match = re.search(
        r"\bvoid\s+compute_pipeline\s*\(",
        gen_code,
    )
    if fn_match:
        start = gen_code.find("{", fn_match.end())
        if start != -1:
            depth = 0
            end = len(gen_code)
            for idx in range(start, len(gen_code)):
                if gen_code[idx] == "{":
                    depth += 1
                elif gen_code[idx] == "}":
                    depth -= 1
                    if depth == 0:
                        end = idx + 1
                        break
            kernel_body = gen_code[start:end]
            kernel_pragmas = [
                p.strip()
                for p in re.findall(r"^\s*#\s*pragma\s+omp\b.*$", kernel_body, flags=re.MULTILINE)
            ]
            kernel_count = len(kernel_pragmas)

    outside_count = max(0, total_count - kernel_count)
    passed = kernel_count >= 1
    detail = f"alvo={kernel_count}, fora={outside_count}"
    if not passed:
        detail += " (sem pragma em compute_pipeline!)"
    elif outside_count > 0:
        detail += " (aviso: pragma fora de compute_pipeline)"
    return passed, kernel_count, outside_count, detail, " ; ".join(kernel_pragmas)


def get_omp_flags() -> tuple[list[str], list[str]]:
    if platform.system() == "Darwin":
        return (
            ["-Xpreprocessor", "-fopenmp", "-I/opt/homebrew/opt/libomp/include"],
            ["-L/opt/homebrew/opt/libomp/lib", "-lomp"],
        )
    return (["-fopenmp"], ["-lgomp"])


def compile_c(
    c_file: Path,
    inc_dir: Path,
    out_exe: Path,
    use_openmp: bool = True,
    extra_defines: list[str] | None = None,
    opt_level: str = "-O3",
) -> tuple[bool, str]:
    extra_defines = extra_defines or ["-DPOLYBENCH_TIME"]
    omp_cflags, omp_ldflags = get_omp_flags() if use_openmp else ([], [])

    cmd = [
        "gcc",
        opt_level,
        "-I",
        str(POLY_UTILS_DIR),
        "-I",
        str(inc_dir),
        *extra_defines,
    ]
    if use_openmp:
        cmd.extend([*omp_cflags])
    cmd.extend([str(POLY_SRC), str(c_file), "-lm", *omp_ldflags, "-o", str(out_exe)])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return True, "OK"

    err_lines = [
        l.strip()
        for l in proc.stderr.splitlines()
        if "error:" in l or "fatal error:" in l or "Undefined symbols" in l or "undefined reference" in l
    ]
    first_err = err_lines[0] if err_lines else (proc.stderr.strip().splitlines()[0] if proc.stderr.strip() else "Erro de compilacao")
    if "error:" in first_err:
        first_err = first_err.split("error:", 1)[1].strip()
    return False, first_err


def parse_floats(stderr_text: str) -> list[float]:
    raw = re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|nan|inf|-inf", stderr_text, flags=re.IGNORECASE)
    return [float(x) for x in raw]


def _run_and_compare_dump(
    gen_c_file: Path,
    ref_vals: list[float],
    tmpdir: Path,
    model: str,
    opt_level: str,
) -> tuple[bool, float, float, str]:
    defines = ["-DSMALL_DATASET", "-DPOLYBENCH_DUMP_ARRAYS"]
    omp_exe = tmpdir / f"omp_op_x_{model}_{opt_level.lstrip('-')}.exe"
    ok, err = compile_c(gen_c_file, ANON_DIR, omp_exe, use_openmp=True, extra_defines=defines, opt_level=opt_level)
    if not ok:
        return False, float("inf"), float("inf"), f"Falha build dump ({opt_level}): {err}"

    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "4"
    try:
        res_omp = subprocess.run([str(omp_exe)], capture_output=True, text=True, env=env, timeout=60)
    except subprocess.TimeoutExpired:
        return False, float("inf"), float("inf"), f"Timeout na execucao ({opt_level}, 60s)"

    if res_omp.returncode != 0:
        return False, float("inf"), float("inf"), f"Crash em runtime ({opt_level}, exit={res_omp.returncode})"

    omp_vals = parse_floats(res_omp.stderr)
    if len(omp_vals) != len(ref_vals) or len(ref_vals) == 0:
        return False, float("inf"), float("inf"), f"Contagem divergente ({opt_level}: {len(omp_vals)} vs {len(ref_vals)})"

    max_abs = 0.0
    max_rel = 0.0
    for a, b in zip(ref_vals, omp_vals):
        if math.isnan(b) or math.isinf(b):
            return False, float("inf"), float("inf"), f"NaN/Inf detectado ({opt_level})"
        diff = abs(a - b)
        rel = diff / max(abs(a), 1e-12)
        if diff > max_abs:
            max_abs = diff
        if rel > max_rel:
            max_rel = rel

    if max_rel <= 1e-5:
        return True, max_rel, max_abs, "OK"
    return False, max_rel, max_abs, f"Divergencia ({opt_level}: erro_rel_max={max_rel:.2e}, erro_abs_max={max_abs:.2e})"


def check_gate4_numerical(
    gen_c_file: Path,
    ref_vals: list[float],
    tmpdir: Path,
    model: str,
) -> tuple[bool, str]:
    ok_o3, rel_o3, _, msg_o3 = _run_and_compare_dump(gen_c_file, ref_vals, tmpdir, model, "-O3")
    if not ok_o3:
        return False, msg_o3

    # Verifica também em -O0 para impedir que promocao em registradores do -O3 mascare
    # data races em variaveis C89 nao privatizadas (ex.: indice interno `v` compartilhado).
    ok_o0, rel_o0, _, msg_o0 = _run_and_compare_dump(gen_c_file, ref_vals, tmpdir, model, "-O0")
    if not ok_o0:
        return False, f"Data race mascarada em -O3, exposta em -O0! {msg_o0}"

    return True, f"Identico -O3/-O0 (erro_rel_max={max(rel_o3, rel_o0):.2e})"


def resolve_candidate_file(model: str) -> Path:
    if model == "openmp":
        return ANON_OPENMP_FILE
    return MODELS_DIR / model / "op_x" / "op_x.c"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica os 4 Gates no Experimento de Anonimização (op_x).")
    parser.add_argument("--models", nargs="+", default=None, help="Lista de modelos para verificar")
    parser.add_argument("--quantized-only", action="store_true", help="Verifica apenas as 4 variantes quantizadas")
    parser.add_argument("--output-csv", "--save", dest="output_csv", type=Path, default=DEFAULT_OUTPUT_CSV, help="CSV de saída")
    args = parser.parse_args()

    if args.models:
        active_models = args.models
    elif args.quantized_only:
        active_models = QUANT_MODELS
    else:
        active_models = DEFAULT_MODELS

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int]] = []
    orig_file = ANON_DIR / "op_x.c"
    orig_code = orig_file.read_text(encoding="utf-8", errors="ignore")

    print("=" * 124)
    print("RELATÓRIO DE VERIFICAÇÃO EM 4 NÍVEIS — EXPERIMENTO DE ANONIMIZAÇÃO (op_x / compute_pipeline)")
    print("=" * 124)
    header = (
        f"{'Modelo':<26} | {'Kernel':<6} | {'G1: Imutável':<12} | "
        f"{'G2: Pragmas':<13} | {'G3: Compila':<11} | {'G4: Numérico':<12} | Diagnóstico"
    )
    print(header)
    print("-" * 124)

    with tempfile.TemporaryDirectory() as tmp_str:
        tmpdir = Path(tmp_str)
        defines = ["-DSMALL_DATASET", "-DPOLYBENCH_DUMP_ARRAYS"]

        # Build sequential op_x reference + cross-check with original 2mm
        seq_exe = tmpdir / "seq_op_x.exe"
        ok, err = compile_c(orig_file, ANON_DIR, seq_exe, use_openmp=False, extra_defines=defines)
        if not ok:
            raise RuntimeError(f"Falha ao compilar op_x sequencial: {err}")
        ref_vals = parse_floats(subprocess.run([str(seq_exe)], capture_output=True, text=True, timeout=60).stderr)

        orig_2mm_c = ORIG_2MM_DIR / "2mm.c"
        if orig_2mm_c.exists():
            exe_2mm = tmpdir / "seq_2mm.exe"
            ok2, _ = compile_c(orig_2mm_c, ORIG_2MM_DIR, exe_2mm, use_openmp=False, extra_defines=defines)
            if ok2:
                vals_2mm = parse_floats(subprocess.run([str(exe_2mm)], capture_output=True, text=True, timeout=60).stderr)
                if vals_2mm != ref_vals:
                    raise RuntimeError("Divergencia entre op_x sequencial e 2mm original!")

        for model in active_models:
            gen_file = resolve_candidate_file(model)
            if not gen_file.exists():
                row = {
                    "Modelo": model,
                    "Kernel": "op_x",
                    "G1_Imutavel": "FAIL",
                    "G2_Pragmas_Kernel": 0,
                    "G2_Pragmas_Fora": 0,
                    "G2_Status": "FAIL",
                    "G3_Compila": "FAIL",
                    "G4_Numerico": "SKIP",
                    "Aprovado_4_Gates": "FAIL",
                    "Pragmas_Inseridos": "",
                    "Diagnostico": "Arquivo gerado ausente",
                }
                rows.append(row)
                print(f"{model:<26} | {'op_x':<6} | {'FAIL':<12} | {'FAIL (0/0)':<13} | {'FAIL':<11} | {'SKIP':<12} | Arquivo ausente")
                continue

            gen_code = gen_file.read_text(encoding="utf-8", errors="ignore")
            g1_ok, g1_msg = check_gate1_immutability(orig_code, gen_code)
            g2_ok, k_cnt, out_cnt, g2_msg, pragmas_str = check_gate2_pragmas(gen_code)

            test_exe = tmpdir / f"test_{model}_op_x.exe"
            g3_ok, g3_msg = compile_c(gen_file, ANON_DIR, test_exe, use_openmp=True)

            if g3_ok:
                g4_ok, g4_msg = check_gate4_numerical(gen_file, ref_vals, tmpdir, model)
                g4_str = "PASS" if g4_ok else "FAIL"
            else:
                g4_ok = False
                g4_str = "SKIP"
                g4_msg = "Nao compilou"

            all_ok = g1_ok and g2_ok and g3_ok and g4_ok
            diag_parts = []
            if not g3_ok:
                diag_parts.append(f"GCC: {g3_msg}")
            if not g1_ok:
                diag_parts.append(g1_msg)
            if not g2_ok or out_cnt > 0:
                diag_parts.append(g2_msg)
            if g3_ok and not g4_ok:
                diag_parts.append(g4_msg)
            if not diag_parts:
                diag_parts.append(f"100% valido ({k_cnt} pragmas em compute_pipeline, {g4_msg})")

            diag = " | ".join(diag_parts)
            row = {
                "Modelo": model,
                "Kernel": "op_x",
                "G1_Imutavel": "PASS" if g1_ok else "FAIL",
                "G2_Pragmas_Kernel": k_cnt,
                "G2_Pragmas_Fora": out_cnt,
                "G2_Status": "PASS" if g2_ok else "FAIL",
                "G3_Compila": "PASS" if g3_ok else "FAIL",
                "G4_Numerico": g4_str,
                "Aprovado_4_Gates": "PASS" if all_ok else "FAIL",
                "Pragmas_Inseridos": pragmas_str,
                "Diagnostico": diag,
            }
            rows.append(row)

            g1_disp = "PASS" if g1_ok else "FAIL"
            g2_disp = f"{'PASS' if g2_ok else 'FAIL'} ({k_cnt}k/{out_cnt}f)"
            g3_disp = "PASS" if g3_ok else "FAIL"
            print(f"{model:<26} | {'op_x':<6} | {g1_disp:<12} | {g2_disp:<13} | {g3_disp:<11} | {g4_str:<12} | {diag[:60]}")

    fieldnames = [
        "Modelo",
        "Kernel",
        "G1_Imutavel",
        "G2_Pragmas_Kernel",
        "G2_Pragmas_Fora",
        "G2_Status",
        "G3_Compila",
        "G4_Numerico",
        "Aprovado_4_Gates",
        "Pragmas_Inseridos",
        "Diagnostico",
    ]
    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    tot = len(rows)
    tot_g1 = sum(1 for r in rows if r["G1_Imutavel"] == "PASS")
    tot_g2 = sum(1 for r in rows if r["G2_Status"] == "PASS")
    tot_g3 = sum(1 for r in rows if r["G3_Compila"] == "PASS")
    tot_g4 = sum(1 for r in rows if r["G4_Numerico"] == "PASS")
    tot_all = sum(1 for r in rows if r["Aprovado_4_Gates"] == "PASS")
    print("-" * 124)
    print(
        f"RESUMO GLOBAL ({tot} modelos): G1={tot_g1}/{tot} | G2={tot_g2}/{tot} | "
        f"G3={tot_g3}/{tot} ({tot_g3/tot*100:.1f}%) | G4={tot_g4}/{tot} ({tot_g4/tot*100:.1f}%) | "
        f"4/4 Gates={tot_all}/{tot} ({tot_all/tot*100:.1f}%)"
    )
    print(f"Relatório CSV salvo em: {args.output_csv}")
    print("=" * 124)


if __name__ == "__main__":
    main()
