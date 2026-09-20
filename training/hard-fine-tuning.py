import os
import sys
import re
import torch
import inspect
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
# pyrefly: ignore [missing-import]
from trl import SFTTrainer
from peft import PeftModel, LoraConfig, get_peft_model, TaskType

# ------------------------------------------------------------------------------
# 1. Configurações de Ambiente e Hardware
# ------------------------------------------------------------------------------
os.environ["UNSLOTH_SKIP_TORCHVISION_CHECK"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

HF_TOKEN = os.environ.get("HF_TOKEN", None)
MODEL_ID = "mistralai/Codestral-22B-v0.1"
DATASET_ID = "LLMforParallelCode1/OMP-FT-Source"

# Caminho do checkpoint da Fase 1 (se existir, faz continual learning sobre ele)
PHASE_1_LORA_PATH = os.environ.get("PHASE_1_LORA_PATH", "codestral_openmp_lora")
OUTPUT_HARD_LORA_DIR = "codestral_openmp_hard_lora"

MAX_SEQ_LENGTH = 2048
DTYPE = torch.bfloat16

print("=" * 70)
print("INICIANDO FASE 2: HARD FINE-TUNING (ALINHAMENTO ESTRUTURAL)")
print("=" * 70)
print(f"CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo: {torch.cuda.get_device_name(0)}")
    print(f"Capacidade CUDA: {torch.cuda.get_device_capability(0)}")
    print(f"VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
print(f"Modelo Base: {MODEL_ID}")
print(f"Checkpoint Fase 1 Base: {PHASE_1_LORA_PATH if os.path.exists(PHASE_1_LORA_PATH) else 'Treinando do zero'}")
print("=" * 70)

# ------------------------------------------------------------------------------
# 2. Template de Prompt (Baseado no Qwen2.5Coder14BPrompt / PolyBench)
# ------------------------------------------------------------------------------
PROMPT_TEMPLATE = """Task: Annotate an existing C kernel with OpenMP pragmas.

You are an expert in High-Performance Computing, C, and OpenMP.

Goal:
Insert OpenMP pragmas to parallelize the kernel for performance, WITHOUT modifying the original C code logic, loop structure, or statements.

Strict Rules (must follow exactly):
- DO NOT change, reorder, remove, or refactor any line of C code.
- DO NOT introduce temporary variables.
- DO NOT change loop bounds or nesting.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before existing loops.
- Numerical results must remain identical.

Instructions:
1. Briefly analyze the loop nest and data dependencies.
2. Decide which loops are safe to parallelize.
3. Add OpenMP pragmas with correct clauses:
   - private / shared
   - collapse (only if safe)
   - schedule (choose static unless clearly suboptimal)
4. Do NOT use reduction unless strictly necessary.
5. Assume compilation with: gcc -O3 -fopenmp.

Output format:
- Section: "Analysis"
- Section: "Optimized Kernel (OpenMP annotations only)"
- Section: "Rationale"

Kernel to annotate:

```c
{}
```"""

COMPLETION_TEMPLATE = """Analysis:
The loop exhibits data parallelism with independent iterations. Data dependencies allow safe execution with OpenMP thread-level parallelization.

Optimized Kernel (OpenMP annotations only):
```c
{}
```

Rationale:
Inserted `{}` immediately before the compute-intensive loop to distribute iterations across available threads with correct variable scoping and scheduling."""

# ------------------------------------------------------------------------------
# 3. Carregamento do Modelo e Tokenizer
# ------------------------------------------------------------------------------
print(f"Carregando tokenizer de {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    token = HF_TOKEN,
    trust_remote_code = True,
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

EOS_TOKEN = tokenizer.eos_token or "<|endoftext|>"

print(f"Carregando {MODEL_ID} em {DTYPE}...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype = DTYPE,
    device_map = "auto",
    token = HF_TOKEN,
    trust_remote_code = True,
)

# Se existir o checkpoint da Fase 1, carregamos os adaptadores e habilitamos treino sobre eles
if os.path.exists(PHASE_1_LORA_PATH):
    print(f"Continuando treinamento a partir dos adaptadores da Fase 1: '{PHASE_1_LORA_PATH}'...")
    model = PeftModel.from_pretrained(model, PHASE_1_LORA_PATH, is_trainable = True)
else:
    print("Iniciando nova configuração LoRA...")
    peft_config = LoraConfig(
        r = 32,
        lora_alpha = 64,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_dropout = 0.05,
        bias = "none",
        task_type = TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, peft_config)

if hasattr(model, "enable_input_require_grads"):
    model.enable_input_require_grads()
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.print_trainable_parameters()

# ------------------------------------------------------------------------------
# 4. Pré-processamento e Construção dos Exemplos Estruturados
# ------------------------------------------------------------------------------
def build_hard_examples(examples):
    texts = []
    for text_data, pragma in zip(examples["text"], examples["omp_pragma_line"]):
        if not text_data or not pragma:
            continue
        
        # Isola o bloco de código original
        code_section = text_data.split("<OMP-START>")[0].strip() if "<OMP-START>" in text_data else text_data.strip()
        
        # 1. Código C limpo (sem nenhuma tag de loop) para colocar no prompt
        clean_code = code_section.replace("<LOOP-START>", "").replace("<LOOP-END>", "").strip()
        
        # 2. Código C anotado com o pragma injetado exatamente onde estava a tag <LOOP-START>
        pragma_clean = pragma.strip()
        if "<LOOP-START>" in code_section:
            annotated_code = code_section.replace("<LOOP-START>", f"{pragma_clean}\n").replace("<LOOP-END>", "").strip()
        else:
            annotated_code = f"{pragma_clean}\n{clean_code}"
            
        prompt = PROMPT_TEMPLATE.format(clean_code)
        completion = COMPLETION_TEMPLATE.format(annotated_code, pragma_clean)
        
        # Texto consolidado para causal LM (Prompt + Resposta + EOS)
        full_text = f"{prompt}\n\n{completion}{EOS_TOKEN}"
        texts.append(full_text)
        
    return { "text": texts }

# Carrega dataset (local ou Hugging Face)
if os.path.exists("OMP-FT-Source.jsonl"):
    print("Carregando dataset local: OMP-FT-Source.jsonl")
    raw_dataset = load_dataset("json", data_files="OMP-FT-Source.jsonl", split="train")
elif os.path.exists("training/OMP-FT-Source.jsonl"):
    print("Carregando dataset local: training/OMP-FT-Source.jsonl")
    raw_dataset = load_dataset("json", data_files="training/OMP-FT-Source.jsonl", split="train")
else:
    print(f"Baixando dataset diretamente do Hugging Face: {DATASET_ID}...")
    raw_dataset = load_dataset(DATASET_ID, split="train", token=HF_TOKEN)

print(f"Processando {len(raw_dataset)} amostras no formato Hard Fine-Tuning...")
dataset = raw_dataset.map(build_hard_examples, batched=True, remove_columns=raw_dataset.column_names)

# Separa 10% para validação e 90% para treino
dataset_split = dataset.train_test_split(test_size=0.1, seed=3407)
train_data = dataset_split["train"]
eval_data = dataset_split["test"]

print(f"Amostras de Treino: {len(train_data)}")
print(f"Amostras de Validação: {len(eval_data)}")

# ------------------------------------------------------------------------------
# 5. Execução do Treinamento
# ------------------------------------------------------------------------------
common_training_args = {
    "output_dir": "outputs_hard",
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,  # batch efetivo = 16
    "warmup_steps": 20,
    "max_steps": 400,  # 400 passos para alinhamento de formato
    "learning_rate": 1e-4,  # lr ligeiramente menor para preservação de pesos
    "fp16": False,
    "bf16": True,
    "logging_steps": 10,
    "eval_strategy": "steps",
    "eval_steps": 50,
    "save_strategy": "steps",
    "save_steps": 100,
    "save_total_limit": 2,
    "optim": "adamw_torch",
    "weight_decay": 0.01,
    "lr_scheduler_type": "cosine",
    "seed": 3407,
    "report_to": "none",
}

try:
    from trl import SFTConfig
    sft_sig = inspect.signature(SFTConfig.__init__).parameters
    config_dict = dict(common_training_args)
    if "max_length" in sft_sig:
        config_dict["max_length"] = MAX_SEQ_LENGTH
    elif "max_seq_length" in sft_sig:
        config_dict["max_seq_length"] = MAX_SEQ_LENGTH
    if "dataset_text_field" in sft_sig:
        config_dict["dataset_text_field"] = "text"
    training_args = SFTConfig(**config_dict)
except ImportError:
    training_args = TrainingArguments(**common_training_args)

trainer_sig = inspect.signature(SFTTrainer.__init__).parameters
trainer_kwargs = {
    "model": model,
    "train_dataset": train_data,
    "eval_dataset": eval_data,
    "args": training_args,
}

if "processing_class" in trainer_sig:
    trainer_kwargs["processing_class"] = tokenizer
elif "tokenizer" in trainer_sig:
    trainer_kwargs["tokenizer"] = tokenizer

if "dataset_text_field" in trainer_sig:
    trainer_kwargs["dataset_text_field"] = "text"

if "max_length" in trainer_sig:
    trainer_kwargs["max_length"] = MAX_SEQ_LENGTH
elif "max_seq_length" in trainer_sig:
    trainer_kwargs["max_seq_length"] = MAX_SEQ_LENGTH

trainer = SFTTrainer(**trainer_kwargs)

print("Iniciando Hard Fine-Tuning...")
trainer.train()

# ------------------------------------------------------------------------------
# 6. Salvamento Final
# ------------------------------------------------------------------------------
print(f"Salvando adaptadores LoRA alinhados em '{OUTPUT_HARD_LORA_DIR}'...")
model.save_pretrained(OUTPUT_HARD_LORA_DIR)
tokenizer.save_pretrained(OUTPUT_HARD_LORA_DIR)
print(f"Hard Fine-Tuning concluído com sucesso! Adaptadores salvos em '{OUTPUT_HARD_LORA_DIR}'.")
