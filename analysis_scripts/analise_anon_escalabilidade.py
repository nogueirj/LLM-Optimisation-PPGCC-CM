#!/usr/bin/env python3
"""
Análise de Escalabilidade e Eficiência Paralela — Experimento de Anonimização (`op_x` vs. `2mm`)

Consolida tempos brutos de `results/raw_times_anon.csv`, cruza com a verificação em 4 Gates
(`results/verificacao_anon.csv`), confronta o Speedup e a Eficiência Paralela do método
anonimizado (`op_x` / `compute_pipeline`) frente ao kernel original `2mm` (de `results/final_metrics.csv`
e `results/quantized_scaling_metrics.csv`), exportando CSV, tabelas LaTeX e gráfico PNG.

Usa apenas a biblioteca padrão do Python 3 no servidor headless (matplotlib/seaborn opcionais).
"""

import csv
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"

RAW_ANON_CSV = RESULTS_DIR / "raw_times_anon.csv"
VERIF_ANON_CSV = RESULTS_DIR / "verificacao_anon.csv"
QUANT_METRICS_CSV = RESULTS_DIR / "quantized_scaling_metrics.csv"
FINAL_METRICS_CSV = RESULTS_DIR / "final_metrics.csv"

OUT_METRICS_CSV = RESULTS_DIR / "anon_scaling_metrics.csv"
OUT_LATEX_TEX = RESULTS_DIR / "tabela_escalabilidade_anon.tex"
OUT_PLOT_PNG = RESULTS_DIR / "scaling_curve_anon.png"

MODEL_ORDER = [
    "openmp",
    "codestral_22b",
    "granite-code-20b",
    "qwen-2.5-coder-14b",
    "starcode-2_15b",
    "deepseekcoder-coder-v2_16b",
    "codellama_13b",
    "codestral-openmp_16b",
    "codestral-openmp_8b",
    "codestral-openmp_4b",
    "codestral-openmp_3b",
]

ORIG_2MM_ALIAS = {
    "openmp": "openmp",
    "codestral_22b": "codestral",
    "granite-code-20b": "granite",
    "qwen-2.5-coder-14b": "qwen",
    "deepseekcoder-coder-v2_16b": "deepseekcoder",
    "codellama_13b": "codellama",
    "codestral-openmp_16b": "codestral-openmp_16b",
    "codestral-openmp_8b": "codestral-openmp_8b",
    "codestral-openmp_4b": "codestral-openmp_4b",
    "codestral-openmp_3b": "codestral-openmp_3b",
}


def is_dataless_on_mac(p: Path) -> bool:
    if not p.exists() or os.uname().sysname != "Darwin":
        return False
    res = subprocess.run(["ls", "-lO", str(p)], capture_output=True, text=True)
    return "dataless" in res.stdout


def load_gate4_map() -> dict[str, dict[str, str]]:
    g_map: dict[str, dict[str, str]] = {}
    if VERIF_ANON_CSV.exists() and not is_dataless_on_mac(VERIF_ANON_CSV):
        with open(VERIF_ANON_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                m = (row.get("Modelo") or "").strip()
                if m:
                    g_map[m] = row
    return g_map


def load_orig_2mm_speedup() -> dict[tuple[str, str, int], float]:
    """Carrega Speedup histórico do 2mm original em (model_alias, dataset, threads)."""
    orig_map: dict[tuple[str, str, int], float] = {}
    for candidate in [QUANT_METRICS_CSV, FINAL_METRICS_CSV]:
        if candidate.exists() and not is_dataless_on_mac(candidate):
            try:
                with open(candidate, "r", newline="") as f:
                    for row in csv.DictReader(f):
                        if row.get("Kernel", "").strip() != "2mm":
                            continue
                        m = row["Model"].strip()
                        ds = row["Dataset"].strip()
                        t = int(float(row["Threads"]))
                        sp = float(row["Speedup"])
                        orig_map.setdefault((m, ds, t), sp)
            except Exception:
                continue
    return orig_map


def load_anon_averages() -> tuple[dict[tuple[str, str, int], tuple[float, float, int]], dict[str, float]]:
    raw_samples: dict[tuple[str, str, int], list[float]] = defaultdict(list)

    if RAW_ANON_CSV.exists() and not is_dataless_on_mac(RAW_ANON_CSV):
        with open(RAW_ANON_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                try:
                    m = row["Model"].strip()
                    ds = row["Dataset"].strip()
                    t = int(float(row["Threads"]))
                    tm = float(row["Time"])
                    raw_samples[(m, ds, t)].append(tm)
                except (ValueError, KeyError):
                    continue

    avg_map: dict[tuple[str, str, int], tuple[float, float, int]] = {}
    seq_acc: dict[str, list[float]] = defaultdict(list)
    for key, vals in raw_samples.items():
        if not vals:
            continue
        mean_v = statistics.mean(vals)
        std_v = statistics.stdev(vals) if len(vals) > 1 else 0.0
        avg_map[key] = (mean_v, std_v, len(vals))
        if key[0] == "sequential":
            seq_acc[key[1]].append(mean_v)

    seq_map = {ds: statistics.mean(v) for ds, v in seq_acc.items() if v}
    return avg_map, seq_map


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    avg_map, seq_map = load_anon_averages()
    if not avg_map or not seq_map:
        print("❌ Dados insuficientes em results/raw_times_anon.csv.")
        return

    g_map = load_gate4_map()
    orig_2mm = load_orig_2mm_speedup()
    records = []

    for (model, ds, threads), (mean_t, std_t, reps) in sorted(avg_map.items()):
        if model == "sequential":
            continue
        t_seq = seq_map.get(ds)
        if not t_seq or mean_t <= 0:
            continue
        speedup = t_seq / mean_t
        efficiency = speedup / threads
        g_row = g_map.get(model, {})
        g4 = (g_row.get("G4_Numerico") or "PASS").strip()
        all_gates = (g_row.get("Aprovado_4_Gates") or "PASS").strip()
        alias = ORIG_2MM_ALIAS.get(model, model)
        sp_2mm = orig_2mm.get((alias, ds, threads))
        records.append({
            "Model": model,
            "Dataset": ds,
            "Kernel": "op_x",
            "Threads": threads,
            "Time": mean_t,
            "Std_Time": std_t,
            "Reps": reps,
            "T_Sequential": t_seq,
            "Speedup": speedup,
            "Efficiency": efficiency,
            "Speedup_Orig_2mm": f"{sp_2mm:.4f}" if sp_2mm is not None else "",
            "G4_Numerical": g4,
            "All_4_Gates": all_gates,
        })

    fieldnames = [
        "Model", "Dataset", "Kernel", "Threads", "Time", "Std_Time", "Reps",
        "T_Sequential", "Speedup", "Efficiency", "Speedup_Orig_2mm",
        "G4_Numerical", "All_4_Gates",
    ]
    with open(OUT_METRICS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"✅ Métricas consolidadas salvas em: {OUT_METRICS_CSV}")

    datasets = sorted({r["Dataset"] for r in records})
    print("\n" + "=" * 114)
    print("📊 EXPERIMENTO DE ANONIMIZAÇÃO — op_x (compute_pipeline) vs. 2mm ORIGINAL")
    print("=" * 114)

    latex_lines = [
        "% Tabelas de Escalabilidade — Experimento de Anonimização (op_x vs 2mm)",
        "% Gerado automaticamente por analysis_scripts/analise_anon_escalabilidade.py",
        "",
    ]

    for ds in datasets:
        ds_recs = [r for r in records if r["Dataset"] == ds]
        avail_threads = sorted({r["Threads"] for r in ds_recs})
        target_threads = [t for t in [32, 64] if t in avail_threads] or [max(avail_threads)]

        for t_eval in target_threads:
            ds_t = {r["Model"]: r for r in ds_recs if r["Threads"] == t_eval}
            print(f"\n▶ DATASET: {ds.upper()} | {t_eval} THREADS")
            print("-" * 114)
            print(
                f"{'Modelo':<26} | {'4 Gates':<8} | {'Tempo (s)':>10} | {'Speedup op_x':>13} | "
                f"{'Efic. op_x':>10} | {'Speedup 2mm':>12} | {'Razão (op_x/2mm)':>16}"
            )
            print("-" * 114)

            latex_lines.extend([
                f"\\begin{{table}}[htbp]",
                f"\\centering",
                f"\\caption{{Desempenho e eficiência do método anonimizado (\\texttt{{op\\_x}}) frente ao \\texttt{{2mm}} original em {t_eval} threads — Dataset \\texttt{{{ds.upper()}}}}}",
                f"\\label{{tab:anon_scale_{ds}_{t_eval}t}}",
                f"\\small",
                f"\\begin{{tabular}}{{lcccccc}}",
                f"\\toprule",
                f"\\textbf{{Modelo}} & \\textbf{{4 Gates}} & \\textbf{{Tempo (s)}} & \\textbf{{Speedup \\texttt{{op\\_x}}}} & \\textbf{{Eficiência}} & \\textbf{{Speedup \\texttt{{2mm}}}} & \\textbf{{Retenção}} \\\\",
                f"\\midrule",
            ])

            for model in MODEL_ORDER:
                r = ds_t.get(model)
                if not r:
                    continue
                sp = r["Speedup"]
                ef = r["Efficiency"]
                tm = r["Time"]
                g4 = r["G4_Numerical"]
                ag = r["All_4_Gates"]
                sp2_str = r["Speedup_Orig_2mm"]
                if sp2_str:
                    sp2 = float(sp2_str)
                    ratio_txt = f"{(sp / sp2) * 100:.1f}%"
                    sp2_disp = f"{sp2:.2f}x"
                    sp2_tex = f"${sp2:.2f}\\times$"
                    ratio_tex = f"${(sp / sp2) * 100:.1f}\\%$"
                else:
                    ratio_txt = "---"
                    sp2_disp = "---"
                    sp2_tex = "---"
                    ratio_tex = "---"

                mark = "*" if g4 != "PASS" else ""
                print(
                    f"{model:<26} | {ag:<8} | {tm:>10.4f} | {f'{sp:.2f}x{mark}':>13} | "
                    f"{ef*100:>9.1f}% | {sp2_disp:>12} | {ratio_txt:>16}"
                )
                m_lbl = model.replace("_", "\\_")
                sp_tex = f"${sp:.2f}\\times{('^\\dagger' if g4 != 'PASS' else '')}$"
                latex_lines.append(
                    f"\\texttt{{{m_lbl}}} & {ag} & ${tm:.4f}$ & {sp_tex} & ${ef*100:.1f}\\%$ & {sp2_tex} & {ratio_tex} \\\\"
                )

            latex_lines.extend([
                "\\bottomrule",
                "\\end{tabular}",
                "\\end{table}",
                "",
            ])

    with open(OUT_LATEX_TEX, "w") as f:
        f.write("\n".join(latex_lines))
    print(f"\n✅ Tabelas LaTeX salvas em: {OUT_LATEX_TEX}")

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        valid_recs = [r for r in records if r["G4_Numerical"] == "PASS"]
        if valid_recs:
            sns.set_style("whitegrid")
            fig, axes = plt.subplots(1, len(datasets), figsize=(8 * len(datasets), 6), squeeze=False)
            for idx, ds in enumerate(datasets):
                ax = axes[0][idx]
                ds_df = [r for r in valid_recs if r["Dataset"] == ds]
                for model in MODEL_ORDER:
                    m_df = [r for r in ds_df if r["Model"] == model]
                    if not m_df:
                        continue
                    xs = [r["Threads"] for r in sorted(m_df, key=lambda x: x["Threads"])]
                    ys = [r["Speedup"] for r in sorted(m_df, key=lambda x: x["Threads"])]
                    ls = "--" if model == "openmp" else "-"
                    lw = 2.6 if model in ("openmp", "codestral-openmp_8b", "codestral-openmp_16b") else 1.8
                    ax.plot(xs, ys, marker="o", linestyle=ls, linewidth=lw, markersize=6, label=model)

                ax.axvline(32, color="gray", linestyle=":", alpha=0.7, label="32 Núcleos Físicos")
                ax.set_title(f"Método Anonimizado (op_x) — {ds.upper()}", fontsize=12, fontweight="bold")
                ax.set_xlabel("Número de Threads", fontsize=11, fontweight="bold")
                ax.set_ylabel("Speedup ($T_{seq}/T_{par}$)", fontsize=11, fontweight="bold")
                ax.set_xticks([1, 2, 4, 8, 16, 32, 64])
                ax.legend(fontsize=8.5, loc="upper left")
                ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(OUT_PLOT_PNG, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Gráfico salvo em: {OUT_PLOT_PNG}")
    except ImportError:
        print("ℹ️ matplotlib/seaborn não encontrado neste ambiente; gráfico PNG pode ser gerado localmente.")


if __name__ == "__main__":
    main()
