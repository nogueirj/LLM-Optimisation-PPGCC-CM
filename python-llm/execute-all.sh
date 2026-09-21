#!/bin/bash

# NÃO use 'set -e' em scripts de lote/batch:
# 1. Se um kernel ou modelo falhar, queremos que o script continue para os outros.
# 2. No bash, comandos como ((count++)) retornam código de saída 1 quando count=0 (0 é avaliado como falsy),
#    o que faz o 'set -e' abortar imediatamente o script após o primeiro sucesso!
set +e

# Posiciona a execução no diretório onde o script reside
cd "$(dirname "$0")"

# ------------------------------------------------------------------------------
# Configurações de Diretórios e Logging
# ------------------------------------------------------------------------------
BENCHMARKS=("2mm" "3mm" "gemm" "atax" "syr2k")
BENCH_DIR="../core/polybench-c-3.2/linear-algebra/kernels"
PROMPTS_DIR="../prompts"
MODELS_DIR="../models"
LOGS_DIR="../logs"

mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOGS_DIR}/execute_all_${TIMESTAMP}.log"

# Grava toda a saída no arquivo de log E exibe em tempo real no terminal
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================================================"
echo "PIPELINE AUTOMATIZADO DE EXECUÇÃO MULTI-MODELOS (OLLAMA & POLYBENCH)"
echo "Data/Hora de Início: $(date)"
echo "Arquivo de Log:      $LOG_FILE"
echo "Kernels:             ${BENCHMARKS[*]}"
echo "========================================================================"

# Detecta o interpretador Python adequado (virtualenv ou sistema)
if [ -f "../.venv/bin/python" ]; then
    PYTHON_CMD="../.venv/bin/python"
elif [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    PYTHON_CMD="python3"
fi
echo "Interpretador Python: $PYTHON_CMD"

# Lista padrão e ordenada dos modelos que fazem parte do benchmark
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

# Se modelos específicos foram passados na linha de comando, usa apenas eles;
# caso contrário, usa a lista padrão de benchmark na ordem priorizada.
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

for model in "${models[@]}"; do
    # Mapeamento do modelo para o prompt e pasta de saída correspondentes
    case "$model" in
        *"granite-code:20b"*)
            PROMPT="${PROMPTS_DIR}/GraniteCode20BPrompt.md"
            OUT_FOLDER="granite-code-20b"
            ;;
        *"qwen2.5-coder:14"*)
            PROMPT="${PROMPTS_DIR}/Qwen2.5Coder14BPrompt.md"
            OUT_FOLDER="qwen-2.5-coder-14b"
            ;;
        *"starcoder2:15b"*)
            PROMPT="${PROMPTS_DIR}/StarCode215B.md"
            OUT_FOLDER="starcode-2_15b"
            ;;
        *"deepseek-coder-v2:16b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="deepseekcoder-coder-v2_16b"
            ;;
        *"codellama:13b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codellama_13b"
            ;;
        *"codestral:22b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral_22b"
            ;;
        *"codestral-openmp:3b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp_3b"
            ;;
        *"codestral-openmp:4b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp_4b"
            ;;
        *"codestral-openmp:8b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp_8b"
            ;;
        *"codestral-openmp:16b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp_16b"
            ;;
        *)
            echo "[-] Modelo '$model' não mapeado no case. Pulando..."
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
            ;;
    esac

    # Verifica se o modelo está realmente disponível no Ollama
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
            # Garante que o diretório de destino existe
            mkdir -p "${MODELS_DIR}/${OUT_FOLDER}/${bench}"
            out_file="${MODELS_DIR}/${OUT_FOLDER}/${bench}/${bench}.c"

            echo "--------------------------------------------------------"
            echo "Executando: $model no kernel $bench..."
            echo "Input:  $bench_file"
            echo "Output: $out_file"
            echo "--------------------------------------------------------"

            # Executa com tolerância a falhas para não abortar o lote caso um kernel falhe
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
done

echo ""
echo "========================================================================"
echo "EXECUÇÃO CONCLUÍDA!"
echo "Data/Hora de Término: $(date)"
echo "Sucessos:             $SUCCESS_COUNT"
echo "Falhas:               $FAIL_COUNT"
echo "Modelos Ignorados:    $SKIPPED_COUNT"
echo "Log Consolidado:      $LOG_FILE"
echo "Códigos Salvos em:    $MODELS_DIR/"
echo "========================================================================"
