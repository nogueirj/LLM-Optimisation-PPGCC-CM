import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ------------------------------------------------------------------------------
# Script de Fusão dos Pesos LoRA (Merge & Unload)
# ------------------------------------------------------------------------------
# Este script funde as matrizes Delta LoRA com o modelo base Codestral 22B
# gerando um único modelo completo em bfloat16 pronto para exportação para GGUF.

BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "mistralai/Codestral-22B-v0.1")

# Prioriza o modelo da Fase 2 (Hard LoRA) se existir; senão usa o da Fase 1
if os.path.exists("codestral_openmp_hard_lora"):
    LORA_DIR = "codestral_openmp_hard_lora"
elif os.path.exists("codestral_openmp_lora"):
    LORA_DIR = "codestral_openmp_lora"
else:
    LORA_DIR = os.environ.get("LORA_DIR", "codestral_openmp_lora")

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "codestral_openmp_merged")
HF_TOKEN = os.environ.get("HF_TOKEN", None)

print("=" * 70)
print("FUSÃO DE PESOS LORA (WEIGHT MERGING)")
print("=" * 70)
print(f"Modelo Base:         {BASE_MODEL_ID}")
print(f"Diretório LoRA:      {LORA_DIR}")
print(f"Diretório de Saída:  {OUTPUT_DIR}")
print(f"CUDA Disponível:     {torch.cuda.is_available()}")
print("=" * 70)

if not os.path.exists(LORA_DIR):
    print(f"[-] Erro: Diretório com os adaptadores LoRA '{LORA_DIR}' não foi encontrado!")
    sys.exit(1)

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16

print(f"1. Carregando modelo base em {dtype} no dispositivo '{device}'...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    dtype = dtype,
    device_map = "auto",
    token = HF_TOKEN,
    trust_remote_code = True,
)

print(f"2. Carregando tokenizer de '{LORA_DIR}'...")
tokenizer = AutoTokenizer.from_pretrained(
    LORA_DIR,
    token = HF_TOKEN,
    trust_remote_code = True,
)

print(f"3. Anexando adaptadores LoRA de '{LORA_DIR}'...")
model = PeftModel.from_pretrained(model, LORA_DIR)

print("4. Mesclando pesos LoRA ao modelo base (merge_and_unload)...")
# Combina as matrizes W = W0 + (B * A) * (alpha / r)
model = model.merge_and_unload()

print(f"5. Salvando modelo consolidado em '{OUTPUT_DIR}'...")
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR, safe_serialization=True)
tokenizer.save_pretrained(OUTPUT_DIR)

print("=" * 70)
print(f"[+] SUCESSO! Modelo consolidado salvo em: '{OUTPUT_DIR}'")
print("O modelo está pronto para ser convertido em GGUF e quantizado.")
print("=" * 70)
