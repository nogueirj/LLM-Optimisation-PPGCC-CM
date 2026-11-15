#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE ESCALABILIDADE - BENCHMARK SUITE PARSEC 3.0 (1 A 64 THREADS)
# ==============================================================================
# Compila e executa os 5 benchmarks representativos do PARSEC 3.0
# (`blackscholes`, `swaptions`, `fluidanimate`, `streamcluster`, `freqmine`)
# desde o baseline sequencial (1T) até 64 threads (1, 2, 4, 8, 16, 32, 64)
# nos datasets STANDARD (`simlarge`) e LARGE (`native`), avaliando:
#   • Referência Manual (openmp)
#   • Modelos Não-Quantizados (codestral_22b, granite-code-20b, qwen-2.5-coder-14b,
#     starcode-2_15b, deepseekcoder-coder-v2_16b, codellama_13b)
#   • Variantes Quantizadas (codestral-openmp_16b, 8b, 4b, 3b)
#
# Uso:
#   ./scripts/run_scale_parsec.sh                  # Executa standard + large (todos os modelos)
#   ./scripts/run_scale_parsec.sh standard         # Executa apenas standard (simlarge)
#   ./scripts/run_scale_parsec.sh large            # Executa apenas large (native)
#   ./scripts/run_scale_parsec.sh both quantized   # Executa apenas openmp + quantizados
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

PARSEC_KERNELS_CSV="blackscholes,swaptions,fluidanimate,streamcluster,freqmine"

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
RAW_PARSEC_CSV="${RAW_PARSEC_CSV_PATH:-results/raw_times_parsec.csv}"

mkdir -p results logs

# ------------------------------------------------------------------------------
# 1. Verificação em 4 Gates antes da execução em escala
# ------------------------------------------------------------------------------
echo "======================================================================"
echo "🔍 EXECUTANDO VERIFICAÇÃO EM 4 NÍVEIS (PARSEC 3.0)"
echo "======================================================================"
python3 scripts/verify_parsec.py --models "${ACTIVE_PARALLEL_MODELS[@]}" --save results/verificacao_parsec.csv

# ------------------------------------------------------------------------------
# Função para executar um dataset completo (standard=simlarge ou large=native)
# ------------------------------------------------------------------------------
run_parsec_dataset() {
    local ds_label="$1"
    local ds_flag="$2"
    local ds_upper
    ds_upper="$(echo "$ds_label" | tr '[:lower:]' '[:upper:]')"

    echo ""
    echo "======================================================================"
    echo "📦 PREPARANDO PARSEC DATASET: ${ds_upper} (${ds_flag})"
    echo "======================================================================"

    # Limpar registros anteriores dos modelos ativos neste dataset para idempotência
    python3 - "$ds_label" "$RAW_PARSEC_CSV" "sequential,${ONLY_MODELS_CSV}" <<'PYEOF'
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

    # 1) Compilar e executar baseline sequential (1T)
    echo "----------------------------------------------------------------------"
    echo "🔨 Compilando baseline sequential (PARSEC) para ${ds_upper} (${ds_flag})..."
    make -C "models/sequential" clean parsec DATASET_SIZE="$ds_flag"
    echo "🚀 Executando baseline sequential (1T) | DATASET: ${ds_upper}..."
    RAW_CSV_PATH="$RAW_PARSEC_CSV" \
    ONLY_MODELS="sequential" \
    ONLY_KERNELS="$PARSEC_KERNELS_CSV" \
    EXEC_TIMEOUT="${EXEC_TIMEOUT:-60}" \
    python3 scripts/executor.py 1 "$ds_label"

    # 2) Compilar todos os modelos paralelos ativos
    for m in "${ACTIVE_PARALLEL_MODELS[@]}"; do
        echo "----------------------------------------------------------------------"
        echo "🔨 Compilando $m (PARSEC) para dataset ${ds_upper} (${ds_flag})..."
        make -C "models/$m" clean parsec DATASET_SIZE="$ds_flag"
    done

    # 3) Loop de escalabilidade por número de threads (1..64T)
    for t in "${THREADS_SEQUENCE[@]}"; do
        echo "======================================================================"
        echo "🚀 EXECUTANDO PARSEC | DATASET: ${ds_upper} | THREADS: ${t}T"
        echo "======================================================================"
        RAW_CSV_PATH="$RAW_PARSEC_CSV" \
        ONLY_MODELS="$ONLY_MODELS_CSV" \
        ONLY_KERNELS="$PARSEC_KERNELS_CSV" \
        EXEC_TIMEOUT="${EXEC_TIMEOUT:-45}" \
        python3 scripts/executor.py "$t" "$ds_label"
    done
}

# ------------------------------------------------------------------------------
# 2. Execução conforme o modo escolhido (standard, large ou both)
# ------------------------------------------------------------------------------
case "$TARGET_MODE" in
    standard|-DSTANDARD_DATASET)
        run_parsec_dataset "standard" "-DSTANDARD_DATASET"
        ;;
    large|-DLARGE_DATASET)
        run_parsec_dataset "large" "-DLARGE_DATASET"
        ;;
    both|"")
        run_parsec_dataset "standard" "-DSTANDARD_DATASET"
        run_parsec_dataset "large" "-DLARGE_DATASET"
        ;;
    *)
        echo "❌ Uso inválido: $TARGET_MODE (use: standard, large ou both)"
        exit 1
        ;;
esac

# ------------------------------------------------------------------------------
# 3. Consolidação e Análise de Escalabilidade do PARSEC
# ------------------------------------------------------------------------------
echo ""
echo "======================================================================"
echo "📊 GERANDO MÉTRICAS, TABELAS LATEX E GRÁFICOS DO PARSEC 3.0"
echo "======================================================================"
python3 analysis_scripts/analise_parsec_escalabilidade.py

echo ""
echo "======================================================================"
echo "✨ BENCHMARK DE ESCALABILIDADE DO PARSEC 3.0 FINALIZADO!"
echo "📁 Arquivos gerados para versionamento e análise:"
echo "  • results/verificacao_parsec.csv             (relatório dos 4 Gates no PARSEC)"
echo "  • results/raw_times_parsec.csv               (tempos brutos de 1 a 64 threads)"
echo "  • results/parsec_scaling_metrics.csv         (speedup e eficiência consolidados)"
echo "  • results/tabela_escalabilidade_parsec.tex   (tabelas LaTeX para o novo capítulo)"
echo "  • results/scaling_curve_parsec.png           (curvas de escalabilidade)"
echo "======================================================================"

