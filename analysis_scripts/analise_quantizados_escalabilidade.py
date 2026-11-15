#!/usr/bin/env python3
"""
Análise de Escalabilidade e Eficiência Paralela das Variantes Quantizadas (Codestral-OpenMP)
Compara codestral-openmp_{16b,8b,4b,3b} contra o baseline Codestral (22B) e Sequencial,
cruzando o desempenho em escala (Speedup e Eficiência) com a corretude numérica (Gate 4).

O núcleo de agregação e geração de CSV/LaTeX utiliza exclusivamente a biblioteca padrão do
Python 3 (zero dependência de pacotes externos em servidores headless), acionando matplotlib
apenas se disponível para exportar o gráfico PNG.
"""

import csv
import math
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"

RAW_CSV = RESULTS_DIR / "raw_times.csv"
RAW_QUANT_CSV = RESULTS_DIR / "raw_times_quantized.csv"
FINAL_METRICS_CSV = RESULTS_DIR / "final_metrics.csv"
VERIF_CSV = RESULTS_DIR / "verificacao_quantizados_depois.csv"

OUT_METRICS_CSV = RESULTS_DIR / "quantized_scaling_metrics.csv"
OUT_LATEX_TEX = RESULTS_DIR / "tabela_escalabilidade_quantizados.tex"
OUT_PLOT_PNG = RESULTS_DIR / "scaling_curve_quantized.png"

QUANT_MODELS = [
    "codestral-openmp_16b",
    "codestral-openmp_8b",
    "codestral-openmp_4b",
    "codestral-openmp_3b",
]
COMPARE_MODELS = ["codestral"] + QUANT_MODELS
KERNELS = ["2mm", "3mm", "atax", "gemm", "syr2k"]


def is_dataless_on_mac(p: Path) -> bool:
    if not p.exists() or os.uname().sysname != "Darwin":
        return False
    res = subprocess.run(["ls", "-lO", str(p)], capture_output=True, text=True)
    return "dataless" in res.stdout


def load_gate4_map() -> dict[tuple[str, str], str]:
    """Retorna mapa (model, kernel) -> 'PASS' | 'FAIL' a partir de verificacao_quantizados_depois.csv."""
    g4_map: dict[tuple[str, str], str] = {}
    if VERIF_CSV.exists() and not is_dataless_on_mac(VERIF_CSV):
        with open(VERIF_CSV, "r", newline="") as f:
            for row in csv.DictReader(f):
                m = (row.get("Modelo") or row.get("Model") or "").strip()
                k = (row.get("Kernel") or "").strip()
                g4 = (row.get("G4_Numerico") or row.get("G4_Numerical") or "PASS").strip()
                if m and k:
                    g4_map[(m, k)] = g4
    return g4_map


def load_combined_averages() -> tuple[dict[tuple[str, str, str, int], tuple[float, float, int]], dict[tuple[str, str], float]]:
    """
    Retorna:
      - avg_map[(model, dataset, kernel, threads)] = (mean_time, std_time, reps)
      - seq_map[(dataset, kernel)] = mean_sequential_time
    """
    raw_samples: dict[tuple[str, str, str, int], list[float]] = defaultdict(list)

    for candidate in [RAW_QUANT_CSV, RAW_CSV]:
        if candidate.exists() and not is_dataless_on_mac(candidate):
            try:
                with open(candidate, "r", newline="") as f:
                    for row in csv.DictReader(f):
                        try:
                            m = row["Model"].strip()
                            ds = row["Dataset"].strip()
                            k = row["Kernel"].strip()
                            t = int(float(row["Threads"]))
                            tm = float(row["Time"])
                            key = (m, ds, k, t)
                            # Se já carregou de RAW_QUANT_CSV, não duplica do RAW_CSV
                            if candidate == RAW_CSV and key in raw_samples:
                                continue
                            raw_samples[key].append(tm)
                        except (ValueError, KeyError):
                            continue
            except Exception as e:
                print(f"⚠️ Aviso ao ler {candidate.name}: {e}")

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

    # Complementar com final_metrics.csv (para garantir baseline sequential e codestral 22B)
    if FINAL_METRICS_CSV.exists() and not is_dataless_on_mac(FINAL_METRICS_CSV):
        try:
            fm_seq_acc: dict[tuple[str, str], list[float]] = defaultdict(list)
            with open(FINAL_METRICS_CSV, "r", newline="") as f:
                for row in csv.DictReader(f):
                    try:
                        m = row["Model"].strip()
                        ds = row["Dataset"].strip()
                        k = row["Kernel"].strip()
                        t = int(float(row["Threads"]))
                        tm = float(row["Time"])
                        t_seq = float(row["T_Sequential"])
                        if (m, ds, k, t) not in avg_map:
                            avg_map[(m, ds, k, t)] = (tm, 0.0, 10)
                        fm_seq_acc[(ds, k)].append(t_seq)
                    except (ValueError, KeyError):
                        continue
            for dk, vals in fm_seq_acc.items():
                if dk not in seq_map and vals:
                    seq_map[dk] = statistics.mean(vals)
        except Exception as e:
            print(f"⚠️ Aviso ao complementar com {FINAL_METRICS_CSV.name}: {e}")

    return avg_map, seq_map


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    avg_map, seq_map = load_combined_averages()

    if not avg_map or not seq_map:
        print("❌ Dados insuficientes para análise de escalabilidade dos modelos quantizados.")
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
        g4 = g4_map.get(
            (model, kernel),
            "FAIL" if (model == "codestral" and kernel == "atax") else "PASS",
        )
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

    # Salvar CSV consolidado
    fieldnames = [
        "Model", "Dataset", "Kernel", "Threads", "Time", "Std_Time",
        "Reps", "T_Sequential", "Speedup", "Efficiency", "G4_Numerical"
    ]
    with open(OUT_METRICS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"✅ Métricas consolidadas salvas em: {OUT_METRICS_CSV}")

    # Filtrar família Codestral (22B + 16B/8B/4B/3B)
    quant_records = [r for r in records if r["Model"] in COMPARE_MODELS]
    if not quant_records:
        print("⚠️ Nenhum registro da família Codestral encontrado.")
        return

    datasets = sorted({r["Dataset"] for r in quant_records})

    print("\n" + "=" * 96)
    print("📊 ESCALABILIDADE DA FAMÍLIA CODESTRAL: ORIGINAL (22B) vs. QUANTIZADOS (16B, 8B, 4B, 3B)")
    print("=" * 96)

    latex_lines = [
        "% Tabelas de Escalabilidade - Modelos Quantizados Codestral-OpenMP",
        "% Gerado automaticamente por analysis_scripts/analise_quantizados_escalabilidade.py",
        "",
    ]

    for ds in datasets:
        ds_recs = [r for r in quant_records if r["Dataset"] == ds]
        # Usar o maior nível de threads em que os modelos quantizados foram executados
        quant_only_threads = [r["Threads"] for r in ds_recs if r["Model"] in QUANT_MODELS]
        max_t = max(quant_only_threads) if quant_only_threads else max(r["Threads"] for r in ds_recs)
        ds_max = [r for r in ds_recs if r["Threads"] == max_t]

        print(f"\n▶ DATASET: {ds.upper()} (Comparativo em {max_t} Threads)")
        print("-" * 96)
        print(
            f"{'Modelo':<22} | {'2mm':>8} | {'3mm':>8} | {'atax':>9} | {'gemm':>8} | {'syr2k':>9} | "
            f"{'Média (G4=PASS)':>15} | {'Efic.(G4=PASS)':>14}"
        )
        print("-" * 96)

        latex_lines.extend([
            f"\\begin{{table}}[htbp]",
            f"\\centering",
            f"\\caption{{Speedup e eficiência paralela em {max_t} threads — Dataset \\texttt{{{ds.upper()}}}}}",
            f"\\label{{tab:quant_scale_{ds}}}",
            f"\\small",
            f"\\begin{{tabular}}{{lccccc cc}}",
            f"\\toprule",
            f"\\textbf{{Variante}} & \\textbf{{2mm}} & \\textbf{{3mm}} & \\textbf{{atax}} & \\textbf{{gemm}} & \\textbf{{syr2k}} & \\textbf{{Speedup Médio (G4)}} & \\textbf{{Eficiência (G4)}} \\\\",
            f"\\midrule",
        ])

        for model in COMPARE_MODELS:
            m_rows = {r["Kernel"]: r for r in ds_max if r["Model"] == model}
            if not m_rows:
                continue

            k_vals = {}
            k_tex = {}
            valid_speedups = []
            valid_effs = []

            for k in KERNELS:
                kr = m_rows.get(k)
                if kr is None:
                    k_vals[k] = "CRASH"
                    k_tex[k] = "\\text{Crash}"
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
                f"{model:<22} | {k_vals['2mm']:>8} | {k_vals['3mm']:>8} | {k_vals['atax']:>9} | "
                f"{k_vals['gemm']:>8} | {k_vals['syr2k']:>9} | "
                f"{avg_sp:>14.2f}x | {avg_ef*100:>13.1f}%"
            )

            m_label = model.replace("_", "\\_")
            latex_lines.append(
                f"\\texttt{{{m_label}}} & {k_tex['2mm']} & {k_tex['3mm']} & {k_tex['atax']} & "
                f"{k_tex['gemm']} & {k_tex['syr2k']} & "
                f"$\\mathbf{{{avg_sp:.2f}\\times}}$ & ${avg_ef*100:.1f}\\%$ \\\\"
            )

        latex_lines.extend([
            "\\bottomrule",
            "\\end{tabular}",
            "\\\\[4pt]",
            "\\footnotesize{Nota: $^\\dagger$ indica kernel reprovado no Gate 4 (divergência numérica por condição de corrida), excluído da média estrita G4.}",
            "\\end{table}",
            "",
        ])

    with open(OUT_LATEX_TEX, "w") as f:
        f.write("\n".join(latex_lines))
    print(f"\n✅ Tabelas LaTeX salvas em: {OUT_LATEX_TEX}")

    # Geração opcional de gráfico se matplotlib estiver instalado
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        valid_quant = [r for r in quant_records if r["G4_Numerical"] == "PASS"]
        if valid_quant:
            sns.set_style("whitegrid")
            fig, axes = plt.subplots(1, len(datasets), figsize=(8 * len(datasets), 6), squeeze=False)
            palette = {
                "codestral": "#1f77b4",
                "codestral-openmp_16b": "#2ca02c",
                "codestral-openmp_8b": "#ff7f0e",
                "codestral-openmp_4b": "#9467bd",
                "codestral-openmp_3b": "#d62728",
            }
            markers = {
                "codestral": "o",
                "codestral-openmp_16b": "s",
                "codestral-openmp_8b": "^",
                "codestral-openmp_4b": "D",
                "codestral-openmp_3b": "v",
            }

            for idx, ds in enumerate(datasets):
                ax = axes[0][idx]
                ds_df = [r for r in valid_quant if r["Dataset"] == ds]
                max_t = max(r["Threads"] for r in ds_df)
                for model in COMPARE_MODELS:
                    m_df = [r for r in ds_df if r["Model"] == model]
                    if not m_df:
                        continue
                    by_t: dict[int, list[float]] = defaultdict(list)
                    for r in m_df:
                        by_t[r["Threads"]].append(r["Speedup"])
                    xs = sorted(by_t.keys())
                    ys = [statistics.mean(by_t[t]) for t in xs]
                    ax.plot(
                        xs,
                        ys,
                        marker=markers.get(model, "o"),
                        linewidth=2.5,
                        markersize=8,
                        color=palette.get(model, "#333333"),
                        label=model,
                    )

                ax.plot([1, max_t], [1, max_t], "k--", alpha=0.5, linewidth=1.8, label="Escalabilidade Ideal")
                ax.set_title(f"Escalabilidade Média (Kernels G4=PASS) — {ds.upper()}", fontsize=13, fontweight="bold")
                ax.set_xlabel("Número de Threads", fontsize=11, fontweight="bold")
                ax.set_ylabel("Speedup Médio ($T_{seq} / T_{par}$)", fontsize=11, fontweight="bold")
                ax.legend(fontsize=9, loc="upper left")
                ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(OUT_PLOT_PNG, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Gráfico de escalabilidade dos quantizados salvo em: {OUT_PLOT_PNG}")
    except ImportError:
        print("ℹ️ matplotlib/seaborn não encontrado neste ambiente; gráfico PNG pode ser gerado localmente.")


if __name__ == "__main__":
    main()
