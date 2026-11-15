#!/usr/bin/env python3
"""
Verificador Automatizado em 4 Níveis (Validation Gates) para os Benchmarks PARSEC 3.0.

Executa os 4 testes científicos sobre os modelos não-quantizados e quantizados para os 5
benchmarks representativos do PARSEC (`blackscholes`, `swaptions`, `fluidanimate`,
`streamcluster`, `freqmine`):
  [Gate 1] Imutabilidade Estrita do Código C (Zero-Mutation / C-Token Equivalence sem #pragma omp)
  [Gate 2] Presença Efetiva de Paralelismo no Kernel (Pragmas dentro de kernel_*)
  [Gate 3] Compilabilidade Estrita Pass@1 (GCC -O3 -fopenmp)
  [Gate 4] Corretude Numérica Determinística (Comparação com referência sequencial via -DPOLYBENCH_DUMP_ARRAYS)

Uso:
  python3 scripts/verify_parsec.py
  python3 scripts/verify_parsec.py --save results/verificacao_parsec.csv
  python3 scripts/verify_parsec.py --quantized-only
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
PARSEC_KERNELS_DIR = BASE_DIR / "core" / "parsec" / "kernels"
PARSEC_OPENMP_DIR = BASE_DIR / "core" / "parsec" / "openmp"
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
DEFAULT_KERNELS = ["blackscholes", "swaptions", "fluidanimate", "streamcluster", "freqmine"]
DEFAULT_OUTPUT_CSV = RESULTS_DIR / "verificacao_parsec.csv"


def strip_omp_pragmas(code: str) -> str:
    """Remove apenas diretivas #pragma omp (incluindo continuações de linha com \\)."""
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
    """Remove comentários /* ... */ e // ... preservando strings literais."""
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
    """
    Extrai a sequência canônica de diretivas de pré-processador e tokens léxicos C
    (após remoção de #pragma omp e comentários) para verificar imutabilidade semântica/sintática.
    """
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
    """Gate 1: Verifica se NENHUM código C foi alterado além da inserção de #pragma omp."""
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


def check_gate2_pragmas(gen_code: str, kernel_name: str) -> tuple[bool, int, int, str]:
    """Gate 2: Conta quantas diretivas #pragma omp existem dentro de kernel_<name> e fora dele."""
    all_pragmas = re.findall(r"^\s*#\s*pragma\s+omp\b.*$", gen_code, flags=re.MULTILINE)
    total_count = len(all_pragmas)

    kernel_count = 0
    fn_match = re.search(
        rf"\bvoid\s+kernel_{re.escape(kernel_name)}\s*\([^)]*\)\s*\{{",
        gen_code,
        flags=re.DOTALL,
    )
    if fn_match:
        start = fn_match.end() - 1
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
        kernel_pragmas = re.findall(
            r"^\s*#\s*pragma\s+omp\b.*$", kernel_body, flags=re.MULTILINE
        )
        kernel_count = len(kernel_pragmas)
    elif "#pragma scop" in gen_code and "#pragma endscop" in gen_code:
        scop_body = gen_code.split("#pragma scop", 1)[1].split("#pragma endscop", 1)[0]
        kernel_count = len(
            re.findall(r"^\s*#\s*pragma\s+omp\b.*$", scop_body, flags=re.MULTILINE)
        )

    outside_count = max(0, total_count - kernel_count)
    passed = kernel_count >= 1
    detail = f"kernel={kernel_count}, fora={outside_count}"
    if not passed:
        detail += " (sem pragma no kernel!)"
    elif outside_count > 0:
        detail += " (aviso: pragma fora do kernel)"
    return passed, kernel_count, outside_count, detail


def get_omp_flags() -> tuple[list[str], list[str]]:
    if platform.system() == "Darwin":
        return (
            ["-Xpreprocessor", "-fopenmp", "-I/opt/homebrew/opt/libomp/include"],
            ["-L/opt/homebrew/opt/libomp/lib", "-lomp"],
        )
    return (["-fopenmp"], ["-lgomp"])


def compile_parsec(
    c_file: Path,
    kernel_name: str,
    out_exe: Path,
    use_openmp: bool = True,
    extra_defines: list[str] | None = None,
) -> tuple[bool, str]:
    """Compila um arquivo C PARSEC com GCC."""
    extra_defines = extra_defines or ["-DPOLYBENCH_TIME"]
    omp_cflags, omp_ldflags = get_omp_flags() if use_openmp else ([], [])

    cmd = [
        "gcc",
        "-O3",
        "-I",
        str(POLY_UTILS_DIR),
        "-I",
        str(PARSEC_KERNELS_DIR / kernel_name),
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


def check_gate4_numerical(
    gen_c_file: Path,
    kernel_name: str,
    seq_dump_cache: dict[str, list[float]],
    tmpdir: Path,
) -> tuple[bool, str]:
    """
    Gate 4: Compila com -DSMALL_DATASET -DPOLYBENCH_DUMP_ARRAYS, executa com 4 threads
    e compara os valores de saída contra a referência sequencial.
    """
    orig_c = PARSEC_KERNELS_DIR / kernel_name / f"{kernel_name}.c"
    defines = ["-DSMALL_DATASET", "-DPOLYBENCH_DUMP_ARRAYS"]

    if kernel_name not in seq_dump_cache:
        seq_exe = tmpdir / f"seq_{kernel_name}.exe"
        ok, err = compile_parsec(orig_c, kernel_name, seq_exe, use_openmp=False, extra_defines=defines)
        if not ok:
            return False, f"Falha ao compilar ref sequencial: {err}"
        res_seq = subprocess.run([str(seq_exe)], capture_output=True, text=True, timeout=60)
        seq_dump_cache[kernel_name] = parse_floats(res_seq.stderr)

    ref_vals = seq_dump_cache[kernel_name]
    omp_exe = tmpdir / f"omp_{kernel_name}_{gen_c_file.parent.parent.name}.exe"
    ok, err = compile_parsec(gen_c_file, kernel_name, omp_exe, use_openmp=True, extra_defines=defines)
    if not ok:
        return False, f"Falha build dump: {err}"

    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "4"
    try:
        res_omp = subprocess.run([str(omp_exe)], capture_output=True, text=True, env=env, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "Timeout na execucao (60s)"

    if res_omp.returncode != 0:
        return False, f"Crash em runtime (exit={res_omp.returncode})"

    omp_vals = parse_floats(res_omp.stderr)
    if len(omp_vals) != len(ref_vals) or len(ref_vals) == 0:
        return False, f"Contagem divergente de elementos ({len(omp_vals)} vs {len(ref_vals)})"

    max_abs = 0.0
    max_rel = 0.0
    for a, b in zip(ref_vals, omp_vals):
        if math.isnan(b) or math.isinf(b):
            return False, "NaN/Inf detectado na saida"
        diff = abs(a - b)
        rel = diff / max(abs(a), 1e-12)
        if diff > max_abs:
            max_abs = diff
        if rel > max_rel:
            max_rel = rel

    if max_rel <= 1e-5:
        return True, f"Identico (erro_rel_max={max_rel:.2e})"
    return False, f"Divergencia numerica! erro_rel_max={max_rel:.2e}, erro_abs_max={max_abs:.2e}"


def resolve_candidate_file(model: str, kernel: str) -> Path:
    if model == "openmp":
        return PARSEC_OPENMP_DIR / kernel / f"{kernel}.c"
    return MODELS_DIR / model / kernel / f"{kernel}.c"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica os 4 Gates dos códigos OpenMP gerados para o PARSEC.")
    parser.add_argument("--models", nargs="+", default=None, help="Lista de modelos para verificar")
    parser.add_argument("--quantized-only", action="store_true", help="Verifica apenas as 4 variantes quantizadas")
    parser.add_argument("--kernels", nargs="+", default=DEFAULT_KERNELS, help="Kernels do PARSEC")
    parser.add_argument("--output-csv", "--save", dest="output_csv", type=Path, default=DEFAULT_OUTPUT_CSV, help="Arquivo CSV de saída")
    args = parser.parse_args()

    if args.models:
        active_models = args.models
    elif args.quantized_only:
        active_models = QUANT_MODELS
    else:
        active_models = DEFAULT_MODELS

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int]] = []
    seq_dump_cache: dict[str, list[float]] = {}

    print("=" * 124)
    print("RELATÓRIO DE VERIFICAÇÃO EM 4 NÍVEIS — BENCHMARK SUITE PARSEC 3.0")
    print("=" * 124)
    header = (
        f"{'Modelo':<26} | {'Kernel':<13} | {'G1: Imutável':<12} | "
        f"{'G2: Pragmas':<13} | {'G3: Compila':<11} | {'G4: Numérico':<12} | Diagnóstico"
    )
    print(header)
    print("-" * 124)

    with tempfile.TemporaryDirectory() as tmp_str:
        tmpdir = Path(tmp_str)
        for model in active_models:
            for kernel in args.kernels:
                orig_file = PARSEC_KERNELS_DIR / kernel / f"{kernel}.c"
                gen_file = resolve_candidate_file(model, kernel)

                if not gen_file.exists():
                    row = {
                        "Modelo": model,
                        "Kernel": kernel,
                        "G1_Imutavel": "FAIL",
                        "G2_Pragmas_Kernel": 0,
                        "G2_Pragmas_Fora": 0,
                        "G2_Status": "FAIL",
                        "G3_Compila": "FAIL",
                        "G4_Numerico": "SKIP",
                        "Aprovado_4_Gates": "FAIL",
                        "Diagnostico": "Arquivo gerado ausente",
                    }
                    rows.append(row)
                    print(f"{model:<26} | {kernel:<13} | {'FAIL':<12} | {'FAIL (0/0)':<13} | {'FAIL':<11} | {'SKIP':<12} | Arquivo ausente")
                    continue

                orig_code = orig_file.read_text(encoding="utf-8", errors="ignore")
                gen_code = gen_file.read_text(encoding="utf-8", errors="ignore")

                g1_ok, g1_msg = check_gate1_immutability(orig_code, gen_code)
                g2_ok, k_cnt, out_cnt, g2_msg = check_gate2_pragmas(gen_code, kernel)

                test_exe = tmpdir / f"test_{model}_{kernel}.exe"
                g3_ok, g3_msg = compile_parsec(gen_file, kernel, test_exe, use_openmp=True)

                if g3_ok:
                    g4_ok, g4_msg = check_gate4_numerical(gen_file, kernel, seq_dump_cache, tmpdir)
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
                    diag_parts.append(f"100% valido ({k_cnt} pragmas no kernel, {g4_msg})")

                diag = " | ".join(diag_parts)

                row = {
                    "Modelo": model,
                    "Kernel": kernel,
                    "G1_Imutavel": "PASS" if g1_ok else "FAIL",
                    "G2_Pragmas_Kernel": k_cnt,
                    "G2_Pragmas_Fora": out_cnt,
                    "G2_Status": "PASS" if g2_ok else "FAIL",
                    "G3_Compila": "PASS" if g3_ok else "FAIL",
                    "G4_Numerico": g4_str,
                    "Aprovado_4_Gates": "PASS" if all_ok else "FAIL",
                    "Diagnostico": diag,
                }
                rows.append(row)

                g1_disp = "PASS" if g1_ok else "FAIL"
                g2_disp = f"{'PASS' if g2_ok else 'FAIL'} ({k_cnt}k/{out_cnt}f)"
                g3_disp = "PASS" if g3_ok else "FAIL"
                print(f"{model:<26} | {kernel:<13} | {g1_disp:<12} | {g2_disp:<13} | {g3_disp:<11} | {g4_str:<12} | {diag[:58]}")

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
        "Diagnostico",
    ]

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 124)
    print("SÍNTESE POR MODELO — BENCHMARKS PARSEC 3.0")
    print("=" * 124)
    print(
        f"{'Modelo':<26} | {'G1 Imutável':<14} | {'G2 Paralelismo':<15} | "
        f"{'G3 Compilação':<16} | {'G4 Numérico':<14} | {'Aprovação Total (4/4)'}"
    )
    print("-" * 124)

    for model in active_models:
        m_rows = [r for r in rows if r["Modelo"] == model]
        n = len(m_rows)
        if n == 0:
            continue
        g1_c = sum(1 for r in m_rows if r["G1_Imutavel"] == "PASS")
        g2_c = sum(1 for r in m_rows if r["G2_Status"] == "PASS")
        g3_c = sum(1 for r in m_rows if r["G3_Compila"] == "PASS")
        g4_c = sum(1 for r in m_rows if r["G4_Numerico"] == "PASS")
        all_c = sum(1 for r in m_rows if r["Aprovado_4_Gates"] == "PASS")

        print(
            f"{model:<26} | {f'{g1_c}/{n}':<14} | {f'{g2_c}/{n}':<15} | "
            f"{f'{g3_c}/{n} ({g3_c/n*100:.0f}%)':<16} | {f'{g4_c}/{n}':<14} | "
            f"{all_c}/{n} ({all_c/n*100:.0f}%)"
        )

    tot = len(rows)
    tot_g3 = sum(1 for r in rows if r["G3_Compila"] == "PASS")
    tot_g4 = sum(1 for r in rows if r["G4_Numerico"] == "PASS")
    tot_all = sum(1 for r in rows if r["Aprovado_4_Gates"] == "PASS")
    print("-" * 124)
    print(
        f"TOTAL GLOBAL ({tot} casos): Compiláveis (G3) = {tot_g3}/{tot} ({tot_g3/tot*100:.1f}%) | "
        f"Numericamente Corretos (G4) = {tot_g4}/{tot} ({tot_g4/tot*100:.1f}%) | "
        f"Aprovados nos 4 Gates = {tot_all}/{tot} ({tot_all/tot*100:.1f}%)"
    )
    print(f"Relatório CSV salvo em: {args.output_csv}")
    print("=" * 124)


if __name__ == "__main__":
    main()

