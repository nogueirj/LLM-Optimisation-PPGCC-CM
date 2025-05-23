#!/usr/bin/env python3
"""
plot_polybench.py <stats.csv>

Gera um gráfico de barras por kernel mostrando média ± desvio‑padrão
para cada tamanho de dataset. Salva como PNG e exibe na tela.
"""
import pandas as pd, sys, math
from pathlib import Path


if __name__ == "__main__":
    if len(sys.argv) != 3: # Expecting the script name + 2 arguments
        print("Usage: python", sys.argv[0], "<file.csv> <out.csv>")
        print("Example: python", sys.argv[0], "raw.csv", "stats.csv")
        sys.exit(1) # Exit with an error code

    csv = Path(sys.argv[1])
    csv_final = Path(sys.argv[2])
    df = pd.read_csv(csv)


    df = pd.read_csv(csv)
    stats = df.groupby(["kernel","size"])["seconds"].agg(["mean","std"]).reset_index()
    stats.to_csv(csv_final, index=False, float_format="%.6f")
