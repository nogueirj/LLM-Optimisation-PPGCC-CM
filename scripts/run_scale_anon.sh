#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE ESCALABILIDADE — EXPERIMENTO DE ANONIMIZAÇÃO (op_x / compute_pipeline)
# ==============================================================================
# Executa a verificação em 4 Gates (`scripts/verify_anon.py`), compila e executa
# o método anonimizado `op_x` (semanticamente idêntico ao `2mm`) desde o baseline
# sequencial (1T) até 64 threads (1, 2, 4, 8, 16, 32, 64) nos datasets STANDARD
# (1024^3) e LARGE (2000^3), confrontando modelos não-quantizados, quantizados
# (`codestral-openmp` 16b/8b/4b/3b) e a referência manual (`openmp`).
#
# Uso:
#   ./scripts/run_scale_anon.sh                # standard + large (todos os modelos)
#   ./scripts/run_scale_anon.sh standard       # apenas standard
#   ./scripts/run_scale_anon.sh large          # apenas large
#   ./scripts/run_scale_anon.sh both quantized # apenas openmp + quantizados
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

TARGET_MODE="${1:-both}"
MODEL_SCOPE="${2:-all}"

if [ -n "${THREADS_LIST:-}" ]; then
    read -r -a THREADS_SEQUENCE <<< "$THREADS_LIST"
else
    THREADS_SEQUENCE=(1 2 4 8 16 32 64)
fi

NON_QUANT_MODELS=(
    "codestral_22b"
    "granite-code-20b"
    "qwen-2.5-coder-14b"
    "starcode-2_15b"
    "deepseekcoder-coder-v2_16b"
    "codellama_13b"
)

QUANT_MODELS=(
    "codestral-openmp_16b"
    "codestral-openmp_8b"
    "codestral-openmp_4b"
    "codestral-openmp_3b"
)

if [ "$MODEL_SCOPE" = "quantized" ]; then
    ACTIVE_PARALLEL_MODELS=("openmp" "${QUANT_MODELS[@]}")
elif [ "$MODEL_SCOPE" = "non-quantized" ]; then
    ACTIVE_PARALLEL_MODELS=("openmp" "${NON_QUANT_MODELS[@]}")
else
    ACTIVE_PARALLEL_MODELS=("openmp" "${NON_QUANT_MODELS[@]}" "${QUANT_MODELS[@]}")
fi

ONLY_MODELS_CSV=$(IFS=, ; echo "${ACTIVE_PARALLEL_MODELS[*]}")
RAW_ANON_CSV="${RAW_ANON_CSV_PATH:-results/raw_times_anon.csv}"

mkdir -p results logs

echo "======================================================================"
echo "🔍 EXECUTANDO VERIFICAÇÃO EM 4 NÍVEIS — ANONIMIZAÇÃO (op_x)"
echo "======================================================================"
python3 scripts/verify_anon.py --models "${ACTIVE_PARALLEL_MODELS[@]}" --save results/verificacao_anon.csv

run_anon_dataset() {
    local ds_label="$1"
    local ds_flag="$2"
    local ds_upper
    ds_upper="$(echo "$ds_label" | tr '[:lower:]' '[:upper:]')"

    echo ""
    echo "======================================================================"
    echo "📦 PREPARANDO DATASET ANONIMIZADO (op_x): ${ds_upper} (${ds_flag})"
    echo "======================================================================"

    python3 - "$ds_label" "$RAW_ANON_CSV" "sequential,${ONLY_MODELS_CSV}" <<'PYEOF'
import csv
import sys
from pathlib import Path

ds = sys.argv[1]
p = Path(sys.argv[2])
active_set = {m.strip() for m in sys.argv[3].split(",") if m.strip()}

if p.exists() and p.stat().st_size > 0:
    kept = []
    removed = 0
    with open(p, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            kept.append(header)
        for row in reader:
            if len(row) >= 2 and row[1].strip() == ds and row[0].strip() in active_set:
                removed += 1
            else:
                kept.append(row)
    with open(p, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(kept)
    if removed > 0:
        print(f"🧹 Removidos {removed} registros anteriores do dataset '{ds}' em {p}")
PYEOF

    echo "----------------------------------------------------------------------"
    echo "🔨 Compilando baseline sequential (op_x) para ${ds_upper} (${ds_flag})..."
    make -C "models/sequential" clean anon DATASET_SIZE="$ds_flag"
    echo "🚀 Executando baseline sequential (1T) | DATASET: ${ds_upper}..."
    RAW_CSV_PATH="$RAW_ANON_CSV" \
    ONLY_MODELS="sequential" \
    ONLY_KERNELS="op_x" \
    EXEC_TIMEOUT="${EXEC_TIMEOUT:-90}" \
    python3 scripts/executor.py 1 "$ds_label"

    for m in "${ACTIVE_PARALLEL_MODELS[@]}"; do
        echo "----------------------------------------------------------------------"
        echo "🔨 Compilando $m (op_x) para dataset ${ds_upper} (${ds_flag})..."
        make -C "models/$m" clean anon DATASET_SIZE="$ds_flag"
    done

    for t in "${THREADS_SEQUENCE[@]}"; do
        echo "======================================================================"
        echo "🚀 EXECUTANDO ANONIMIZADO (op_x) | DATASET: ${ds_upper} | THREADS: ${t}T"
        echo "======================================================================"
        RAW_CSV_PATH="$RAW_ANON_CSV" \
        ONLY_MODELS="$ONLY_MODELS_CSV" \
        ONLY_KERNELS="op_x" \
        EXEC_TIMEOUT="${EXEC_TIMEOUT:-60}" \
        python3 scripts/executor.py "$t" "$ds_label"
    done
}

case "$TARGET_MODE" in
    standard|-DSTANDARD_DATASET)
        run_anon_dataset "standard" "-DSTANDARD_DATASET"
        ;;
    large|-DLARGE_DATASET)
        run_anon_dataset "large" "-DLARGE_DATASET"
        ;;
    both|"")
        run_anon_dataset "standard" "-DSTANDARD_DATASET"
        run_anon_dataset "large" "-DLARGE_DATASET"
        ;;
    *)
        echo "❌ Uso inválido: $TARGET_MODE (use: standard, large ou both)"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "📊 GERANDO MÉTRICAS, TABELAS LATEX E GRÁFICOS — ANONIMIZAÇÃO (op_x)"
echo "======================================================================"
python3 analysis_scripts/analise_anon_escalabilidade.py

echo ""
echo "======================================================================"
echo "✨ BENCHMARK DE ANONIMIZAÇÃO (op_x) FINALIZADO!"
echo "📁 Arquivos gerados:"
echo "  • results/verificacao_anon.csv               (relatório dos 4 Gates no op_x)"
echo "  • results/raw_times_anon.csv                 (tempos brutos de 1 a 64 threads)"
echo "  • results/anon_scaling_metrics.csv           (speedup e eficiência consolidados)"
echo "  • results/tabela_escalabilidade_anon.tex     (tabelas LaTeX para anonimizacao.tex)"
echo "  • results/scaling_curve_anon.png             (curvas de escalabilidade op_x vs 2mm)"
echo "======================================================================"
