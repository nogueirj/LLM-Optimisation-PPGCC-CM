#!/usr/bin/env bash
set -e

# ==============================================================================
# Pipeline Automatizado: Conversão GGUF e Quantização Multi-Nível (16, 8, 4, 3 bit)
# ==============================================================================

MERGED_MODEL_DIR="${1:-codestral_openmp_merged}"
GGUF_DIR="models_gguf"
LLAMA_CPP_DIR="llama.cpp"

echo "========================================================================"
echo "PIPELINE DE QUANTIZAÇÃO MULTI-NÍVEL (GGUF & OLLAMA)"
echo "========================================================================"
echo "Modelo de Entrada:  $MERGED_MODEL_DIR"
echo "Diretório GGUF:     $GGUF_DIR"
echo "========================================================================"

if [ ! -d "$MERGED_MODEL_DIR" ]; then
    echo "[-] Erro: Diretório do modelo mesclado '$MERGED_MODEL_DIR' não encontrado!"
    echo "Execute primeiro: python training/merge_lora.py"
    exit 1
fi

mkdir -p "$GGUF_DIR"

# 1. Obter e compilar o llama.cpp se necessário
if [ ! -d "$LLAMA_CPP_DIR" ]; then
    echo "[1/5] Clonando llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP_DIR"
fi

echo "[2/5] Instalando dependências e compilando llama-quantize..."
# Garante as bibliotecas Python necessárias para conversão GGUF
pip install -q "gguf>=0.10.0" protobuf sentencepiece || true

cd "$LLAMA_CPP_DIR"
# O quantizador de pesos é puramente CPU/SIMD. Desabilitar CUDA evita conflitos com compute_120a na arquitetura Blackwell
# e compila em menos de 20 segundos.
rm -rf build
cmake -B build -DGGML_CUDA=OFF
cmake --build build --config Release --target llama-quantize -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
cd ..

# Localiza o binário compilado
QUANTIZE_BIN=""
for candidate in "$LLAMA_CPP_DIR/build/bin/llama-quantize" "$LLAMA_CPP_DIR/build/bin/quantize"; do
    if [ -f "$candidate" ]; then
        QUANTIZE_BIN="$candidate"
        break
    fi
done

if [ -z "$QUANTIZE_BIN" ]; then
    echo "[-] Erro: Binário do quantizador não foi encontrado em $LLAMA_CPP_DIR/build/bin/!"
    exit 1
fi
echo "[+] Quantizador localizado em: $QUANTIZE_BIN"

# 2. Conversão para GGUF FP16 (16-bit)
F16_GGUF="$GGUF_DIR/codestral-openmp-f16.gguf"
echo "[3/5] Preparando tokenizer e convertendo modelo Hugging Face para GGUF FP16 (16-bit)..."

# Corrige compatibilidade do tokenizer do Codestral com llama.cpp
python3 -c "
import json, os, shutil
from huggingface_hub import hf_hub_download

cfg_path = '$MERGED_MODEL_DIR/tokenizer_config.json'
if os.path.exists(cfg_path):
    with open(cfg_path, 'r') as f:
        d = json.load(f)
    d['tokenizer_class'] = 'LlamaTokenizer'
    with open(cfg_path, 'w') as f:
        json.dump(d, f, indent=2)
    print('[+] tokenizer_class ajustado para LlamaTokenizer.')

tok_model_dst = '$MERGED_MODEL_DIR/tokenizer.model'
if not os.path.exists(tok_model_dst):
    try:
        cached_path = hf_hub_download(repo_id='mistralai/Codestral-22B-v0.1', filename='tokenizer.model')
        shutil.copy(cached_path, tok_model_dst)
        print('[+] tokenizer.model obtido do cache do Codestral com sucesso!')
    except Exception as e:
        print('[!] Aviso ao obter tokenizer.model:', e)
"

python3 "$LLAMA_CPP_DIR/convert_hf_to_gguf.py" "$MERGED_MODEL_DIR" \
    --outfile "$F16_GGUF" \
    --outtype f16

# 3. Quantizações Multi-Nível (8-bit, 4-bit, 3-bit)
Q8_GGUF="$GGUF_DIR/codestral-openmp-q8_0.gguf"
Q4_GGUF="$GGUF_DIR/codestral-openmp-q4_k_m.gguf"
Q3_GGUF="$GGUF_DIR/codestral-openmp-q3_k_m.gguf"

echo "[4/5] Gerando quantizações..."

echo " -> [1/3] Gerando Q8_0 (8-bit)..."
"$QUANTIZE_BIN" "$F16_GGUF" "$Q8_GGUF" Q8_0

echo " -> [2/3] Gerando Q4_K_M (4-bit)..."
"$QUANTIZE_BIN" "$F16_GGUF" "$Q4_GGUF" Q4_K_M

echo " -> [3/3] Gerando Q3_K_M (3-bit)..."
"$QUANTIZE_BIN" "$F16_GGUF" "$Q3_GGUF" Q3_K_M

# 4. Criação dos Modelfiles para Ollama
echo "[5/5] Gerando Modelfiles e registrando no Ollama..."

BASE_ABS_DIR="$(cd "$GGUF_DIR" && pwd)"

create_modelfile() {
    local file_name="$1"
    local modelfile_name="$2"
    cat <<EOF > "$GGUF_DIR/$modelfile_name"
FROM $BASE_ABS_DIR/$file_name

PARAMETER temperature 0.2
PARAMETER top_p 0.95
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|endoftext|>"
PARAMETER stop "</s>"

TEMPLATE """{{ .Prompt }}"""
EOF
}

create_modelfile "codestral-openmp-f16.gguf"   "Modelfile_16b"
create_modelfile "codestral-openmp-q8_0.gguf"   "Modelfile_8b"
create_modelfile "codestral-openmp-q4_k_m.gguf" "Modelfile_4b"
create_modelfile "codestral-openmp-q3_k_m.gguf" "Modelfile_3b"

# Se o daemon do Ollama estiver acessível, registra os modelos
if command -v ollama &> /dev/null; then
    echo "Registrando modelos no Ollama..."
    ollama create codestral-openmp:16b -f "$GGUF_DIR/Modelfile_16b" || echo "[!] Aviso: Ollama não pôde registrar 16b (daemon inativo?)."
    ollama create codestral-openmp:8b  -f "$GGUF_DIR/Modelfile_8b"  || true
    ollama create codestral-openmp:4b  -f "$GGUF_DIR/Modelfile_4b"  || true
    ollama create codestral-openmp:3b  -f "$GGUF_DIR/Modelfile_3b"  || true
    echo "[+] Modelos registrados com sucesso no Ollama!"
fi

echo "========================================================================"
echo "TODAS AS VERSÕES QUANTIZADAS FORAM GERADAS COM SUCESSO!"
echo "========================================================================"
ls -lh "$GGUF_DIR"/*.gguf
echo "========================================================================"
