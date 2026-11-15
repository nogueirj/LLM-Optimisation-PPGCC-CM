#!/usr/bin/env python3
"""
Análise de Escalabilidade e Eficiência Paralela — Benchmark Suite PARSEC 3.0
Compara modelos não-quantizados (`codestral_22b`, `granite-code-20b`, `qwen-2.5-coder-14b`,
`starcode-2_15b`, `deepseekcoder-coder-v2_16b`, `codellama_13b`), variantes quantizadas
(`codestral-openmp_16b`, `8b`, `4b`, `3b`) e a referência manual (`openmp`) frente ao
baseline sequencial (`sequential`), cruzando o desempenho de 1 a 64 threads com a
corretude numérica (Gate 4).

O núcleo de agregação e geração de CSV/LaTeX utiliza exclusivamente a biblioteca padrão do
Python 3 (zero dependência de pacotes externos no servidor), acionando matplotlib apenas se
disponível para exportar o gráfico PNG.
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

RAW_PARSEC_CSV = RESULTS_DIR / "raw_times_parsec.csv"
VERIF_PARSEC_CSV = RESULTS_DIR / "verificacao_parsec.csv"

OUT_METRICS_CSV = RESULTS_DIR / "parsec_scaling_metrics.csv"
OUT_LATEX_TEX = RESULTS_DIR / "tabela_escalabilidade_parsec.tex"
OUT_PLOT_PNG = RESULTS_DIR / "scaling_curve_parsec.png"

KERNELS = ["blackscholes", "swaptions", "fluidanimate", "streamcluster", "freqmine"]

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


def is_dataless_on_mac(p: Path) -> bool:
    if not p.exists() or os.uname().sysname != "Darwin":
        return False
    res = subprocess.run(["ls", "-lO", str(p)], capture_output=True, text=True)
    return "dataless" in res.stdout


def load_gate4_map() -> dict[tuple[str, str], str]:
    g4_map: dict[tuple[str, str], str] = {}
    if VERIF_PARSEC_CSV.exists() and not is_dataless_on_mac(VERIF_PARSEC_CSV):
        with open(VERIF_PARSEC_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                m = (row.get("Modelo") or row.get("Model") or "").strip()
                k = (row.get("Kernel") or "").strip()
                g4 = (row.get("G4_Numerico") or row.get("G4_Numerical") or "PASS").strip()
                if m and k:
                    g4_map[(m, k)] = g4
    return g4_map


def load_parsec_averages() -> tuple[dict[tuple[str, str, str, int], tuple[float, float, int]], dict[tuple[str, str], float]]:
    raw_samples: dict[tuple[str, str, str, int], list[float]] = defaultdict(list)

    if RAW_PARSEC_CSV.exists() and not is_dataless_on_mac(RAW_PARSEC_CSV):
        with open(RAW_PARSEC_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                try:
                    m = row["Model"].strip()
                    ds = row["Dataset"].strip()
                    k = row["Kernel"].strip()
                    t = int(float(row["Threads"]))
                    tm = float(row["Time"])
                    raw_samples[(m, ds, k, t)].append(tm)
                except (ValueError, KeyError):
                    continue

    avg_map: dict[tuple[str, str, str, int], tuple[float, float, int]] = {}
    seq_acc: dict[tuple[str, str], list[float]] = defaultdict(list)

    for key, vals in raw_samples.items():
        if not vals:
            continue
        mean_v = statistics.mean(vals)
        std_v = statistics.stdev(vals) if len(vals) > 1 else 0.0
        avg_map[key] = (mean_v, std_v, len(vals))
        if key[0] == "sequential":
            seq_acc[(key[1], key[2])].append(mean_v)

    seq_map: dict[tuple[str, str], float] = {
        dk: statistics.mean(v) for dk, v in seq_acc.items() if v
    }
    return avg_map, seq_map


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    avg_map, seq_map = load_parsec_averages()

    if not avg_map or not seq_map:
        print("❌ Dados insuficientes em results/raw_times_parsec.csv para análise de escalabilidade do PARSEC.")
        return

    g4_map = load_gate4_map()
    records = []

    for (model, ds, kernel, threads), (mean_t, std_t, reps) in sorted(avg_map.items()):
        if model == "sequential":
            continue
        t_seq = seq_map.get((ds, kernel))
        if not t_seq or mean_t <= 0:
            continue
        speedup = t_seq / mean_t
        efficiency = speedup / threads
        g4 = g4_map.get((model, kernel), "PASS")
        records.append({
            "Model": model,
            "Dataset": ds,
            "Kernel": kernel,
            "Threads": threads,
            "Time": mean_t,
            "Std_Time": std_t,
            "Reps": reps,
            "T_Sequential": t_seq,
            "Speedup": speedup,
            "Efficiency": efficiency,
            "G4_Numerical": g4,
        })

    fieldnames = [
        "Model", "Dataset", "Kernel", "Threads", "Time", "Std_Time",
        "Reps", "T_Sequential", "Speedup", "Efficiency", "G4_Numerical"
    ]
    with open(OUT_METRICS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"✅ Métricas consolidadas do PARSEC salvas em: {OUT_METRICS_CSV}")

    datasets = sorted({r["Dataset"] for r in records})

    print("\n" + "=" * 116)
    print("📊 ESCALABILIDADE NOS BENCHMARKS PARSEC 3.0 — MODELOS NÃO-QUANTIZADOS, QUANTIZADOS E REFERÊNCIA")
    print("=" * 116)

    latex_lines = [
        "% Tabelas de Escalabilidade - Benchmark Suite PARSEC 3.0",
        "% Gerado automaticamente por analysis_scripts/analise_parsec_escalabilidade.py",
        "",
    ]

    for ds in datasets:
        ds_recs = [r for r in records if r["Dataset"] == ds]
        max_t = max(r["Threads"] for r in ds_recs)
        ds_max = [r for r in ds_recs if r["Threads"] == max_t]

        print(f"\n▶ DATASET: {ds.upper()} (Comparativo em {max_t} Threads)")
        print("-" * 116)
        print(
            f"{'Modelo':<26} | {'blacksch':>9} | {'swaptions':>9} | {'fluidanim':>9} | "
            f"{'streamcl':>9} | {'freqmine':>9} | {'Média (G4=PASS)':>15} | {'Efic.(G4=PASS)':>14}"
        )
        print("-" * 116)

        latex_lines.extend([
            f"\\begin{{table}}[htbp]",
            f"\\centering",
            f"\\caption{{Speedup e eficiência paralela nos benchmarks PARSEC 3.0 em {max_t} threads — Dataset \\texttt{{{ds.upper()}}}}}",
            f"\\label{{tab:parsec_scale_{ds}}}",
            f"\\small",
            f"\\begin{{tabular}}{{lccccc cc}}",
            f"\\toprule",
            f"\\textbf{{Modelo}} & \\textbf{{blackscholes}} & \\textbf{{swaptions}} & \\textbf{{fluidanimate}} & \\textbf{{streamcluster}} & \\textbf{{freqmine}} & \\textbf{{Speedup Médio (G4)}} & \\textbf{{Eficiência (G4)}} \\\\",
            f"\\midrule",
        ])

        present_models = [m for m in MODEL_ORDER if any(r["Model"] == m for r in ds_max)]
        for extra_m in sorted({r["Model"] for r in ds_max} - set(present_models)):
            present_models.append(extra_m)

        for model in present_models:
            m_rows = {r["Kernel"]: r for r in ds_max if r["Model"] == model}
            k_vals = {}
            k_tex = {}
            valid_speedups = []
            valid_effs = []

            for k in KERNELS:
                kr = m_rows.get(k)
                if kr is None:
                    k_vals[k] = "FAIL/SKIP"
                    k_tex[k] = "---"
                else:
                    sp = kr["Speedup"]
                    ef = kr["Efficiency"]
                    g4 = kr["G4_Numerical"]
                    mark = "*" if g4 != "PASS" else ""
                    k_vals[k] = f"{sp:.2f}x{mark}"
                    k_tex[k] = f"${sp:.2f}\\times{('^\\dagger' if g4 != 'PASS' else '')}$"
                    if g4 == "PASS":
                        valid_speedups.append(sp)
                        valid_effs.append(ef)

            avg_sp = statistics.mean(valid_speedups) if valid_speedups else float("nan")
            avg_ef = statistics.mean(valid_effs) if valid_effs else float("nan")

            print(
                f"{model:<26} | {k_vals['blackscholes']:>9} | {k_vals['swaptions']:>9} | "
                f"{k_vals['fluidanimate']:>9} | {k_vals['streamcluster']:>9} | {k_vals['freqmine']:>9} | "
                f"{avg_sp:>14.2f}x | {avg_ef*100:>13.1f}%"
            )

            m_label = model.replace("_", "\\_")
            latex_lines.append(
                f"\\texttt{{{m_label}}} & {k_tex['blackscholes']} & {k_tex['swaptions']} & "
                f"{k_tex['fluidanimate']} & {k_tex['streamcluster']} & {k_tex['freqmine']} & "
                f"$\\mathbf{{{avg_sp:.2f}\\times}}$ & ${avg_ef*100:.1f}\\%$ \\\\"
            )

        latex_lines.extend([
            "\\bottomrule",
            "\\end{tabular}",
            "\\\\[4pt]",
            "\\footnotesize{Nota: $^\\dagger$ indica kernel reprovado no Gate 4 (divergência numérica), excluído da média estrita G4.}",
            "\\end{table}",
            "",
        ])

    with open(OUT_LATEX_TEX, "w") as f:
        f.write("\n".join(latex_lines))
    print(f"\n✅ Tabelas LaTeX do PARSEC salvas em: {OUT_LATEX_TEX}")

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
                max_t = max(r["Threads"] for r in ds_df)
                present_models = [m for m in MODEL_ORDER if any(r["Model"] == m for r in ds_df)]
                for model in present_models:
                    m_df = [r for r in ds_df if r["Model"] == model]
                    by_t: dict[int, list[float]] = defaultdict(list)
                    for r in m_df:
                        by_t[r["Threads"]].append(r["Speedup"])
                    xs = sorted(by_t.keys())
                    ys = [statistics.mean(by_t[t]) for t in xs]
                    ax.plot(xs, ys, marker="o", linewidth=2.2, markersize=6, label=model)

                ax.plot([1, max_t], [1, max_t], "k--", alpha=0.5, linewidth=1.6, label="Escalabilidade Ideal")
                ax.set_title(f"PARSEC 3.0 — Escalabilidade Média (G4=PASS) — {ds.upper()}", fontsize=12, fontweight="bold")
                ax.set_xlabel("Número de Threads", fontsize=11, fontweight="bold")
                ax.set_ylabel("Speedup Médio ($T_{seq} / T_{par}$)", fontsize=11, fontweight="bold")
                ax.legend(fontsize=8, loc="upper left")
                ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(OUT_PLOT_PNG, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Gráfico de escalabilidade do PARSEC salvo em: {OUT_PLOT_PNG}")
    except ImportError:
        print("ℹ️ matplotlib/seaborn não encontrado neste ambiente; gráfico PNG pode ser gerado localmente.")


if __name__ == "__main__":
    main()

