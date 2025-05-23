#!/usr/bin/env python3
"""
plot_polybench.py <stats.csv>

Gera um gráfico de barras por kernel mostrando média ± desvio‑padrão
para cada tamanho de dataset. Salva como PNG e exibe na tela.
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) != 3: # Expecting the script name + 2 arguments
        print("Usage: python", sys.argv[0], "<file.csv> <output_dir>")
        print("Example: python", sys.argv[0], "times.csv", "graficos")
        sys.exit(1) # Exit with an error code

    csv = Path(sys.argv[1])
    df = pd.read_csv(csv)

    # -------- Gráfico 1: barras empilhadas por kernel --------
    #pivot = df.pivot(index="kernel", columns="size", values="seconds")
    #pivot.plot(kind="bar", figsize=(12,5))
    #plt.ylabel("Tempo (s)")
    #plt.title("PolyBench 4.1 – tempo por kernel e tamanho")
    #plt.xticks(rotation=45, ha="right")
    #plt.tight_layout()
    # plt.show()

    sizes = ["mini","small","medium","large","extralarge"]  # ordem fixa
    df["size"] = pd.Categorical(df["size"], categories=sizes, ordered=True)
    pivot = df.pivot_table(index="kernel", columns="size", values="mean")
    err   = df.pivot_table(index="kernel", columns="size", values="std")

    ax = pivot.plot(kind="bar", yerr=err, capsize=3, figsize=(12,6))
    ax.set_ylabel("Tempo (s)")
    ax.set_title("PolyBench 4.1 – média ± 1σ(N execuções)")
    ax.legend(title="Tamanho")
    plt.xticks(rotation=45, ha="right")
    plt.yscale("log")
    plt.tight_layout()
    
    # Salva em arquivo.
    png = csv.with_suffix(".png")
    plt.savefig(png, dpi=600)
    print(f"Gráfico salvo em {png}")
    # plt.show()

    
    #base = os.path.basename(sys.argv[1])
    #graph_file_name = os.path.splitext(base)[0]

    #plt.savefig(sys.argv[2] + "/" + graph_file_name + ".png", dpi=600)  # Higher resolution

    # -------- Gráfico 2: linhas por tamanho (todos os kernels) --------
    #for size, grp in df.groupby("size"):
    #    grp.sort_values("kernel").plot(x="kernel", y="seconds", label=size, marker="o")
    #plt.xticks(rotation=90)
    #plt.ylabel("Tempo (s)")
    #plt.title("Escalabilidade entre datasets")
    #plt.tight_layout()
    #plt.show()








