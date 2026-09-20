import os
import sys
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
from trl import SFTTrainer
from peft import LoraConfig, get_peft_model, TaskType

# ------------------------------------------------------------------------------
# 1. Configurações de Ambiente e Hardware
# ------------------------------------------------------------------------------
os.environ["UNSLOTH_SKIP_TORCHVISION_CHECK"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Token do Hugging Face (lê da variável de ambiente ou informe abaixo)
HF_TOKEN = os.environ.get("HF_TOKEN", None)

# Seletor de Backend:
# Na NVIDIA RTX PRO 6000 Blackwell (sm_120), o Unsloth e o bitsandbytes (4-bit)
# frequentemente falham por falta de kernels compilados para sm_120.
# Como a RTX 6000 tem ~96 GB de VRAM, o fine-tuning LoRA em bfloat16 nativo (USE_UNSLOTH=False)
# roda com máxima performance e estabilidade sem precisar de quantização 4-bit.
USE_UNSLOTH = os.environ.get("USE_UNSLOTH", "0") == "1"
LOAD_IN_4BIT = os.environ.get("LOAD_IN_4BIT", "0") == "1"

MODEL_ID = "mistralai/Codestral-22B-v0.1"
DATASET_ID = "LLMforParallelCode1/OMP-FT-Source"
MAX_SEQ_LENGTH = 2048
DTYPE = torch.bfloat16

print("=" * 60)
print(f"CUDA disponível: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo: {torch.cuda.get_device_name(0)}")
    print(f"Capacidade CUDA: {torch.cuda.get_device_capability(0)}")
    print(f"VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
print(f"Backend: {'Unsloth' if USE_UNSLOTH else 'HuggingFace PEFT + Transformers (Nativo)'}")
print(f"Precisão: {DTYPE} | 4-bit: {LOAD_IN_4BIT}")
print("=" * 60)

# ------------------------------------------------------------------------------
# 2. Carregamento do Modelo e Tokenizer
# ------------------------------------------------------------------------------
if USE_UNSLOTH:
    print(f"Carregando {MODEL_ID} via Unsloth...")
    from unsloth import FastLanguageModel
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = MODEL_ID,
        max_seq_length = MAX_SEQ_LENGTH,
        dtype = DTYPE,
        load_in_4bit = LOAD_IN_4BIT,
        token = HF_TOKEN,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r = 32,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 64,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
    )
else:
    print(f"Carregando {MODEL_ID} nativamente em {DTYPE}...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        token = HF_TOKEN,
        trust_remote_code = True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    if LOAD_IN_4BIT:
        from transformers import BitsAndBytesConfig
        quantization_config = BitsAndBytesConfig(
            load_in_4bit = True,
            bnb_4bit_quant_type = "nf4",
            bnb_4bit_compute_dtype = DTYPE,
            bnb_4bit_use_double_quant = True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype = DTYPE,
        device_map = "auto",
        quantization_config = quantization_config,
        token = HF_TOKEN,
        trust_remote_code = True,
    )

    # Configuração LoRA nativa via PEFT
    peft_config = LoraConfig(
        r = 32,
        lora_alpha = 64,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
        lora_dropout = 0.05,
        bias = "none",
        task_type = TaskType.CAUSAL_LM,
    )
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    model = get_peft_model(model, peft_config)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.print_trainable_parameters()

# ------------------------------------------------------------------------------
# 3. Formatação e Particionamento do Dataset
# ------------------------------------------------------------------------------
prompt_template = """Analise o código C/C++ abaixo. O loop a ser paralelizado está demarcado pelas tags <LOOP-START> e <LOOP-END>. 
Forneça exclusivamente a diretiva OpenMP correta para paralelizar este loop.

### Código:
{}

### Pragma OpenMP:
{}"""

EOS_TOKEN = tokenizer.eos_token or "<|endoftext|>"

def formatting_prompts_func(examples):
    texts = []
    for text_data, pragma in zip(examples["text"], examples["omp_pragma_line"]):
        if not text_data or not pragma:
            continue
        # Remove a diretiva já embutida ao final do snippet original
        if "<OMP-START>" in text_data:
            code_only = text_data.split("<OMP-START>")[0].strip()
        else:
            code_only = text_data.strip()
        text = prompt_template.format(code_only, pragma.strip()) + EOS_TOKEN
        texts.append(text)
    return { "text" : texts }

# Carrega do Hugging Face diretamente ou do arquivo local caso exista
if os.path.exists("OMP-FT-Source.jsonl"):
    print("Carregando dataset local: OMP-FT-Source.jsonl")
    dataset = load_dataset("json", data_files="OMP-FT-Source.jsonl", split="train")
elif os.path.exists("training/OMP-FT-Source.jsonl"):
    print("Carregando dataset local: training/OMP-FT-Source.jsonl")
    dataset = load_dataset("json", data_files="training/OMP-FT-Source.jsonl", split="train")
else:
    print(f"Baixando dataset diretamente do Hugging Face: {DATASET_ID}...")
    dataset = load_dataset(DATASET_ID, split="train", token=HF_TOKEN)

print(f"Total de amostras brutas: {len(dataset)}")
dataset = dataset.map(formatting_prompts_func, batched = True, remove_columns = dataset.column_names)

# Separa 10% para validação e 90% para treino
dataset_split = dataset.train_test_split(test_size=0.1, seed=3407)
train_data = dataset_split["train"]
eval_data = dataset_split["test"]

print(f"Amostras de Treino: {len(train_data)}")
print(f"Amostras de Validação: {len(eval_data)}")

# ------------------------------------------------------------------------------
# 4. Execução do Treinamento
# ------------------------------------------------------------------------------
import inspect

common_training_args = {
    "output_dir": "outputs",
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,  # batch efetivo = 16
    "warmup_steps": 20,
    "max_steps": 500,
    "learning_rate": 2e-4,
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
    "lr_scheduler_type": "linear",
    "seed": 3407,
    "report_to": "none",
}

# Suporte automático a qualquer versão do trl (SFTConfig vs TrainingArguments)
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

# Monta os argumentos do SFTTrainer dinamicamente de acordo com a versão instalada
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

print("Iniciando o fine-tuning...")
trainer.train()

# ------------------------------------------------------------------------------
# 5. Salvamento do Modelo e Adaptadores LoRA
# ------------------------------------------------------------------------------
output_lora_dir = "codestral_openmp_lora"
print(f"Treinamento concluído. Salvando adaptadores LoRA em '{output_lora_dir}'...")

if USE_UNSLOTH:
    model.save_pretrained_merged(output_lora_dir, tokenizer, save_method = "lora")
    # Para exportar para GGUF via unsloth (se suportado no ambiente):
    # model.save_pretrained_gguf("codestral_openmp_ft", tokenizer, quantization_method = "q4_k_m")
else:
    model.save_pretrained(output_lora_dir)
    tokenizer.save_pretrained(output_lora_dir)

print(f"Adaptadores salvos com sucesso em '{output_lora_dir}'!")
