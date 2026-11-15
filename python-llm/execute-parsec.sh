#!/bin/bash

# Pipeline automatizado para anotação OpenMP dos 5 benchmarks do PARSEC
# Suporta tanto os modelos quantizados (codestral-openmp:3b/4b/8b/16b)
# quanto os modelos não-quantizados via Ollama.
set +e

cd "$(dirname "$0")"

BENCHMARKS=("blackscholes" "swaptions" "fluidanimate" "streamcluster" "freqmine")
BENCH_DIR="../core/parsec/kernels"
PROMPTS_DIR="../prompts"
MODELS_DIR="../models"
LOGS_DIR="../logs"

mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOGS_DIR}/execute_parsec_${TIMESTAMP}.log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================================================"
echo "PIPELINE AUTOMATIZADO DE ANOTAÇÃO OPENMP — BENCHMARK PARSEC (OLLAMA)"
echo "Data/Hora de Início: $(date)"
echo "Arquivo de Log:      $LOG_FILE"
echo "Kernels PARSEC:      ${BENCHMARKS[*]}"
echo "========================================================================"

if [ -f "../.venv/bin/python" ]; then
    PYTHON_CMD="../.venv/bin/python"
elif [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    PYTHON_CMD="python3"
fi
echo "Interpretador Python: $PYTHON_CMD"

DEFAULT_MODELS=(
    "codestral-openmp:3b"
    "codestral-openmp:4b"
    "codestral-openmp:8b"
    "codestral-openmp:16b"
    "codestral:22b"
    "granite-code:20b"
    "qwen2.5-coder:14b"
    "starcoder2:15b"
    "deepseek-coder-v2:16b"
    "codellama:13b"
)

if [ $# -gt 0 ]; then
    models=("$@")
    echo "Modelos especificados via argumento: ${models[*]}"
else
    echo "Executando lista padrão de benchmark (${#DEFAULT_MODELS[@]} modelos)..."
    models=("${DEFAULT_MODELS[@]}")
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIPPED_COUNT=0

PROMPT="${PROMPTS_DIR}/ParsecPrompt.md"

for model in "${models[@]}"; do
    case "$model" in
        *"granite-code:20b"*)
            OUT_FOLDER="granite-code-20b"
            ;;
        *"qwen2.5-coder:14"*)
            OUT_FOLDER="qwen-2.5-coder-14b"
            ;;
        *"starcoder2:15b"*)
            OUT_FOLDER="starcode-2_15b"
            ;;
        *"deepseek-coder-v2:16b"*)
            OUT_FOLDER="deepseekcoder-coder-v2_16b"
            ;;
        *"codellama:13b"*)
            OUT_FOLDER="codellama_13b"
            ;;
        *"codestral:22b"*)
            OUT_FOLDER="codestral_22b"
            ;;
        *"codestral-openmp:3b"*)
            OUT_FOLDER="codestral-openmp_3b"
            ;;
        *"codestral-openmp:4b"*)
            OUT_FOLDER="codestral-openmp_4b"
            ;;
        *"codestral-openmp:8b"*)
            OUT_FOLDER="codestral-openmp_8b"
            ;;
        *"codestral-openmp:16b"*)
            OUT_FOLDER="codestral-openmp_16b"
            ;;
        *)
            echo "[-] Modelo '$model' não mapeado no case. Pulando..."
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
            ;;
    esac

    if ! ollama list | awk 'NR>1 {print $1}' | grep -Fxq "$model"; then
        echo ""
        echo "[!] AVISO: Modelo '$model' não encontrado no Ollama ('ollama list'). Pulando..."
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        continue
    fi

    echo ""
    echo "========================================================================"
    echo ">> MODELO ALVO: $model"
    echo "   Prompt: $PROMPT"
    echo "   Saída:  ${MODELS_DIR}/${OUT_FOLDER}/"
    echo "========================================================================"

    for bench in "${BENCHMARKS[@]}"; do
        bench_file="${BENCH_DIR}/${bench}/${bench}.c"
        if [ -f "$bench_file" ]; then
            mkdir -p "${MODELS_DIR}/${OUT_FOLDER}/${bench}"
            out_file="${MODELS_DIR}/${OUT_FOLDER}/${bench}/${bench}.c"

            echo "--------------------------------------------------------"
            echo "Executando: $model no kernel PARSEC $bench..."
            echo "Input:  $bench_file"
            echo "Output: $out_file"
            echo "--------------------------------------------------------"

            if $PYTHON_CMD annotate-code-file-01.py "$model" "$bench_file" "$PROMPT" "$out_file"; then
                echo "[+] [SUCESSO] $model em $bench concluído."
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            else
                echo "[-] [FALHA] Erro ao processar $model em $bench. Continuando..."
                FAIL_COUNT=$((FAIL_COUNT + 1))
            fi
        else
            echo "[!] Aviso: Arquivo de benchmark '$bench_file' não encontrado. Pulando..."
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done

    echo "[*] Descarregando '$model' da VRAM (ollama stop)..."
    ollama stop "$model" >/dev/null 2>&1 || true
done

echo ""
echo "========================================================================"
echo "EXECUÇÃO PARSEC CONCLUÍDA!"
echo "Data/Hora de Término: $(date)"
echo "Sucessos:             $SUCCESS_COUNT"
echo "Falhas:               $FAIL_COUNT"
echo "Modelos Ignorados:    $SKIPPED_COUNT"
echo "Log Consolidado:      $LOG_FILE"
echo "Códigos Salvos em:    $MODELS_DIR/"
echo "========================================================================"

