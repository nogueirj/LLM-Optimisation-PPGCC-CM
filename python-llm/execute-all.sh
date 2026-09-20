#!/bin/bash

# Exit on any error
set -e

# Change to the directory where the script is located
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

# Se modelos específicos foram passados na linha de comando, usa apenas eles;
# caso contrário, busca todos os modelos disponíveis no Ollama.
if [ $# -gt 0 ]; then
    models="$*"
    echo "Modelos especificados via argumento: $models"
else
    echo "Buscando modelos instalados no Ollama..."
    models=$(ollama list | awk 'NR>1 {print $1}')
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIPPED_COUNT=0

for model in $models; do
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
            OUT_FOLDER="codestral-openmp-3b"
            ;;
        *"codestral-openmp:4b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp-4b"
            ;;
        *"codestral-openmp:8b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp-8b"
            ;;
        *"codestral-openmp:16b"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral-openmp-16b"
            ;;
        *)
            echo "[-] Modelo '$model' não mapeado no case. Pulando..."
            ((SKIPPED_COUNT++))
            continue
            ;;
    esac

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

            # Executa com tolerância a falhas para não abortar todo o lote caso um kernel falhe
            if $PYTHON_CMD annotate-code-file-01.py "$model" "$bench_file" "$PROMPT" "$out_file"; then
                echo "[+] [SUCESSO] $model em $bench concluído."
                ((SUCCESS_COUNT++))
            else
                echo "[-] [FALHA] Erro ao processar $model em $bench. Continuando..."
                ((FAIL_COUNT++))
            fi
        else
            echo "[!] Aviso: Arquivo de benchmark '$bench_file' não encontrado. Pulando..."
            ((FAIL_COUNT++))
        fi
    done
done

echo ""
echo "========================================================================"
echo "EXECUÇÃO CONCLUÍDA COM SUCESSO!"
echo "Data/Hora de Término: $(date)"
echo "Sucessos:             $SUCCESS_COUNT"
echo "Falhas:               $FAIL_COUNT"
echo "Modelos Ignorados:    $SKIPPED_COUNT"
echo "Log Consolidado:      $LOG_FILE"
echo "Códigos Salvos em:    $MODELS_DIR/"
echo "========================================================================"
