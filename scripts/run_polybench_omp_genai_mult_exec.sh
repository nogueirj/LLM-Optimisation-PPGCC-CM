#!/usr/bin/env bash
###############################################################################
# run_polybench.sh – compila, executa PolyBench‑4.1 R vezes e agrega estatísticas
# Uso: ./run_polybench.sh /caminho/PolyBench-4.1 repeticoes gcc "flags"
# [rag@backporting scripts]$ ./run_polybench_acc_mult_exec.sh ../PolyBench-ACC/OpenMP 1 gcc "-O3 -march=native -lm -fopenmp"
###############################################################################
set -euo pipefail

echo "→ Início: `date`."

# ./run_polybench_acc_mult_exec.sh ../PolyBench-OpenMP-GenAI/OpenMP 1 gcc "-O3 -march=native -lm -fopenmp"

if [ "$#" -eq 0 ]; then
  echo "No arguments provided."
  echo "Uso: ./run_polybench_omp_genai_mult_exec.sh ../PolyBench-OpenMP-GenAI/OpenMP <reps> <compiler> \"-O3 -march=native -lm -fopenmp\""
  exit 1
elif [ "$#" -ne 4 ]; then
  echo "Incorrect number of arguments. Expected 4, but received $#."
  exit 1
else
  echo "Received $# arguments."
  echo "Argument 1: $1"
  echo "Argument 2: $2"
  echo "Argument 3: $3"
  echo "Argument 4: $4"
fi

POLYBENCH_DIR=$(realpath "$1")
REPS=${2:-5}                          # Nº de repetições (default 5)
COMPILER=${3:-gcc}
CFLAGS=${4:-"-O3 -lm -fopenmp"}
VERSION=OMP-GENAI

OUTDIR="results_$(date +%Y%m%d_%H%M%S)_$(hostname)_${USER}_${VERSION}"
mkdir -p "$OUTDIR"
RAW="$OUTDIR/raw.csv"                 # 1 linha = 1 execução
STATS="$OUTDIR/stats.csv"             # média e desvio

echo "kernel,size,run,seconds,version" > "$RAW"

sizes=(mini small medium)

echo "== Etapa 1: Compilando kernels para todos os tamanhos =="
for src in $(find "$POLYBENCH_DIR" -type f -name "*.c" ! -path "*/utilities/*"); do
  kernel_name=$(basename "$src" .c)
  # Skip the common utility files
  [[ "$kernel_name" == "polybench" || "$kernel_name" == "polybench.c" ]] && continue

  for size in "${sizes[@]}"; do
    define=$(tr '[:lower:]' '[:upper:]' <<< "${size}_DATASET")
    exe="$OUTDIR/${kernel_name}_${size}_${VERSION}.exe"

    echo "  • ${kernel_name}_${size}_${VERSION}"

    $COMPILER -I"$POLYBENCH_DIR/utilities" \
      "$src" "$POLYBENCH_DIR/utilities/polybench.c" \
      -D$define -DPOLYBENCH_TIME -o "$exe" $CFLAGS
  done
done

echo "== Etapa 2: Executando (${REPS}× por kernel/tamanho) e coletando tempos. =="
for exe in $(find "$OUTDIR" -type f -name "*.exe" | sort); do
  base=$(basename "$exe" .exe)
  #kernel_name="${base%_*}"
  #size_exe="${base##*_}"
  IFS='_' read -r kernel_name size_exe version <<< "$base"
  #echo "Kernel: $kernel"
  #echo "Size: $size"
  #echo "Variant: $variant"
  echo "[$kernel_name, $version]"
  for size in "${sizes[@]}"; do
    [[ "$size_exe" != "$size" ]] && continue # saltar os repetidos.

    exe="$OUTDIR/${kernel_name}_${size}_${version}.exe"
    for run in $(seq 1 "$REPS"); do
      printf " • %-20s %-10s run %d/%d\r" "$kernel_name" "$size" "$run" "$REPS"
      # sec=$("$exe" 2>&1 | grep -Eo '[0-9]+\.[0-9]+')
      seconds=$("$exe" 2>&1 | grep -Eo '[0-9]+\.[0-9]+') || seconds="NA"
      echo " $seconds s"
      echo "$kernel_name,$size,$run,$seconds,$version" >> "$RAW"
    done
  done
done

echo "→ Resultados em: $RAW"

#-----
#echo "== Executando (${REPS}× por tamanho) =="
#sizes=(mini small medium large extralarge)
#for exe in "$OUTDIR"/*.exe; do
#  kname=$(basename "$exe" .exe)
#  for size in "${sizes[@]}"; do
#    define=$(tr '[:lower:]' '[:upper:]' <<< "${size}_DATASET")
#    for run in $(seq 1 "$REPS"); do
#      printf " • %-20s %-10s run %d/%d\r" "$kname" "$size" "$run" "$REPS"
#      sec=$("$exe" -D"$define" 2>&1 | grep -Eo '[0-9]+\.[0-9]+')
#      echo "$kname,$size,$run,$sec" >> "$RAW"
#    done
#  done
#done
#----
echo ""

echo "== Etapa 3: Agregando estatísticas =="

#python prepare_data_results.py "$RAW" "$STATS"

echo "→ Resultados CSV final: $STATS"

echo "→ Etapa 4: Gerando Gráficos."

#python plot_polybench.py "$STATS" $OUTDIR

echo "→ Fim: `date`."
