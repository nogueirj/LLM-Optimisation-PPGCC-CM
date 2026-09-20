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
        *"granite"*)
            PROMPT="${PROMPTS_DIR}/GraniteCode20BPrompt.md"
            OUT_FOLDER="granite"
            ;;
        *"qwen2.5-coder"*)
            PROMPT="${PROMPTS_DIR}/Qwen2.5Coder14BPrompt.md"
            OUT_FOLDER="qwen"
            ;;
        *"qwen2.5"*)
            PROMPT="${PROMPTS_DIR}/QwenPrompt.md"
            OUT_FOLDER="qwen"
            ;;
        *"starcoder2"*)
            PROMPT="${PROMPTS_DIR}/StarCode215B.md"
            OUT_FOLDER="starcode"
            ;;
        *"starcoder"*)
            PROMPT="${PROMPTS_DIR}/StarCode215B.md"
            OUT_FOLDER="starcode"
            ;;
        *"deepseek-coder"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="deepseekcoder"
            ;;
        *"codellama"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codellama"
            ;;
        *"codestral"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="codestral"
            ;;
        *"llama3.2"*)
            PROMPT="${PROMPTS_DIR}/DefaultPrompt.md"
            OUT_FOLDER="llama3.2"
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
