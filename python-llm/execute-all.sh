#!/bin/bash

# Exit on any error
set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

BENCHMARKS=("2mm" "3mm" "gemm" "atax" "syr2k")
BENCH_DIR="../core/polybench-c-3.2/linear-algebra/kernels"
PROMPTS_DIR="../prompts"
MODELS_DIR="../models"

echo "Fetching models from Ollama..."
models=$(ollama list | awk 'NR>1 {print $1}')

for model in $models; do
    # Map model to prompt and output directory
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
            echo "Unknown model mapping for $model, skipping..."
            continue
            ;;
    esac

    for bench in "${BENCHMARKS[@]}"; do
        bench_file="${BENCH_DIR}/${bench}/${bench}.c"
        if [ -f "$bench_file" ]; then
            # Ensure the output directory exists
            mkdir -p "${MODELS_DIR}/${OUT_FOLDER}/${bench}"
            out_file="${MODELS_DIR}/${OUT_FOLDER}/${bench}/${bench}.c"
            
            # Use .venv python if available, otherwise python3
            if [ -f "../.venv/bin/python" ]; then
                PYTHON_CMD="../.venv/bin/python"
            else
                PYTHON_CMD="python3"
            fi

            echo "----------------------------------------"
            echo "Executing $model on $bench..."
            echo "Prompt: $PROMPT"
            echo "Input: $bench_file"
            echo "Output: $out_file"
            $PYTHON_CMD annotate-code-file-01.py "$model" "$bench_file" "$PROMPT" "$out_file"
        else
            echo "Warning: Benchmark file $bench_file not found. Skipping..."
        fi
    done
done

echo "Done mapping and executing models!"
