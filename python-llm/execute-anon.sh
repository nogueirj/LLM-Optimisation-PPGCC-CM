#!/bin/bash

# Pipeline automatizado para o Experimento de Anonimização (op_x / compute_pipeline)
# Avalia se os LLMs (quantizados e não-quantizados) dependem da assinatura do método (kernel_2mm)
# ou realizam raciocínio estrutural sobre os laços e dependências de dados.
set +e

cd "$(dirname "$0")"

BENCH_FILE="../core/anonymized/op_x/op_x.c"
PROMPT="../prompts/AnonPrompt.md"
MODELS_DIR="../models"
LOGS_DIR="../logs"

mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOGS_DIR}/execute_anon_${TIMESTAMP}.log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================================================"
echo "PIPELINE DE ANONIMIZAÇÃO — MÉTODO ANONIMIZADO op_x (compute_pipeline)"
echo "Data/Hora de Início: $(date)"
echo "Arquivo de Log:      $LOG_FILE"
echo "Código de Entrada:   $BENCH_FILE"
echo "Prompt Neutro:       $PROMPT"
echo "========================================================================"

if [ -f "../.venv/bin/python" ]; then
    PYTHON_CMD="../.venv/bin/python"
elif [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    PYTHON_CMD="python3"
fi
echo "Interpretador Python: $PYTHON_CMD"

QUANT_MODELS=(
    "codestral-openmp:3b"
    "codestral-openmp:4b"
    "codestral-openmp:8b"
    "codestral-openmp:16b"
)

NON_QUANT_MODELS=(
    "codestral:22b"
    "granite-code:20b"
    "qwen2.5-coder:14b"
    "starcoder2:15b"
    "deepseek-coder-v2:16b"
    "codellama:13b"
)

DEFAULT_MODELS=("${QUANT_MODELS[@]}" "${NON_QUANT_MODELS[@]}")

if [ $# -eq 0 ] || [ "$1" = "all" ]; then
    echo "Executando lista completa (${#DEFAULT_MODELS[@]} modelos: quantizados + não-quantizados)..."
    models=("${DEFAULT_MODELS[@]}")
elif [ "$1" = "quantized" ]; then
    echo "Executando apenas as variantes quantizadas (${#QUANT_MODELS[@]} modelos)..."
    models=("${QUANT_MODELS[@]}")
elif [ "$1" = "non-quantized" ]; then
    echo "Executando apenas os modelos não-quantizados (${#NON_QUANT_MODELS[@]} modelos)..."
    models=("${NON_QUANT_MODELS[@]}")
else
    models=("$@")
    echo "Modelos especificados via argumento: ${models[*]}"
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIPPED_COUNT=0

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
    echo "   Saída:  ${MODELS_DIR}/${OUT_FOLDER}/op_x/op_x.c"
    echo "========================================================================"

    mkdir -p "${MODELS_DIR}/${OUT_FOLDER}/op_x"
    out_file="${MODELS_DIR}/${OUT_FOLDER}/op_x/op_x.c"

    if $PYTHON_CMD annotate-code-file-01.py "$model" "$BENCH_FILE" "$PROMPT" "$out_file"; then
        echo "[+] [SUCESSO] $model em op_x concluído."
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "[-] [FALHA] Erro ao processar $model em op_x. Continuando..."
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo "[*] Descarregando '$model' da VRAM (ollama stop)..."
    ollama stop "$model" >/dev/null 2>&1 || true
done

echo ""
echo "========================================================================"
echo "EXECUÇÃO DE ANONIMIZAÇÃO (op_x) CONCLUÍDA!"
echo "Data/Hora de Término: $(date)"
echo "Sucessos:             $SUCCESS_COUNT"
echo "Falhas:               $FAIL_COUNT"
echo "Modelos Ignorados:    $SKIPPED_COUNT"
echo "Log Consolidado:      $LOG_FILE"
echo "========================================================================"
