#!/usr/bin/env bash
################################################################################
# run_polybench.sh – compila, executa e coleta tempos do PolyBench 4.1
# Uso: ./run_polybench.sh /caminho/para/PolyBench-4.1 gcc "-O3 -march=native -lm"
# ./run_polybench.sh ../PolyBenchC-4.2.1 gcc "-O3 -march=native -lm"
################################################################################
set -euo pipefail

POLYBENCH_DIR=$(realpath "$1")        # Ex.: ./PolyBench-4.1
COMPILER=${2:-gcc}                     # gcc, clang, icc…
CFLAGS=${3:-"-O3"}                     # flags extras

OUTDIR="results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

CSV="$OUTDIR/times.csv"
echo "kernel,size,seconds" > "$CSV"

echo "→ Início: `date`."

echo "→ Etapa 1: compilando kernels."
for kernel_src in $(find "$POLYBENCH_DIR" -name "*.c" -path "*/utilities/*" -prune -o -name "*.c" -print); do
  kernel_dir=$(dirname "$kernel_src")
  kernel_name=$(basename "$kernel_src" .c)

  # Skip the common utility files
  [[ "$kernel_name" == "polybench" || "$kernel_name" == "polybench.c" ]] && continue

  obj="$kernel_dir/$kernel_name.exe"
  echo "  • $kernel_name"
  $COMPILER $CFLAGS \
    -I"$POLYBENCH_DIR/utilities" \
    "$kernel_src" "$POLYBENCH_DIR/utilities/polybench.c" \
    -DPOLYBENCH_TIME \
    -o "$obj"
done

echo "→ Etapa 2: executando e coletando tempos."
for exe in $(find "$POLYBENCH_DIR" -name "*.exe"); do
  kernel_name=$(basename "$exe" .exe)
  for size in "mini" "small" "medium" "large" "extralarge"; do
    # PolyBench usa -DMINI_DATASET, SMALL_DATASET, etc.
    size_define=$(tr '[:lower:]' '[:upper:]' <<< "${size}_DATASET")
    echo -n "  • $kernel_name ($size)… "
    seconds=$("$exe" -D"$size_define" 2>&1 | grep -Eo '[0-9]+\.[0-9]+') || seconds="NA"
    echo "$seconds s"
    echo "$kernel_name,$size,$seconds" >> "$CSV"
  done
done

echo "→ Resultados em: $CSV"

echo "→ Etapa 3: Gerando Gráficos."

python gerar_grafico.py $CSV $OUTDIR

echo "→ Fim: `date`."
