# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos para o PolyBench-ACC (Expert OpenACC)
# Estrutura: OpenMP-Optimized/models/openacc
CORE_DIR    = ../../core/PolyBench-ACC
UTILS_DIR   = ../../core/polybench-c-3.2/utilities
ACC_KERNELS = $(CORE_DIR)/OpenACC/linear-algebra/kernels
POLY_SRC    = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação
# No Ubuntu com NVIDIA, o ideal é usar o GCC ou o compilador da NVIDIA (nvc)
CC = gcc
CFLAGS = -O3 -I $(UTILS_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm

# 4. Flags OpenACC por SO
ifeq ($(UNAME_S), Darwin)
    # macOS: OpenACC não é nativo. Usamos flags para tentar compilar via GCC do Homebrew
    # Nota: Geralmente rodará apenas em modo sequencial ou multicore no Mac.
    ACC_FLAGS = -fopenacc
    ACC_LIBS  = 
else
    # Ubuntu / Linux (Preparado para NVIDIA)
    # Se tiver os drivers NVIDIA instalados: -foffload=nvptx-none
    ACC_FLAGS = -fopenacc
    ACC_LIBS  = -lgomp
endif

# 5. Alvos
all: 2mmopenacc 3mmopenacc ataxopenacc gemmopenacc syr2kopenacc

# --- 2mm ---
2mmopenacc:
	$(CC) $(CFLAGS) $(ACC_FLAGS) -I $(ACC_KERNELS)/2mm $(POLY_SRC) $(ACC_KERNELS)/2mm/2mm.c $(LDFLAGS) $(ACC_LIBS) -o 2mm-openacc.exe

# --- 3mm ---
3mmopenacc:
	$(CC) $(CFLAGS) $(ACC_FLAGS) -I $(ACC_KERNELS)/3mm $(POLY_SRC) $(ACC_KERNELS)/3mm/3mm.c $(LDFLAGS) $(ACC_LIBS) -o 3mm-openacc.exe

# --- atax ---
ataxopenacc:
	$(CC) $(CFLAGS) $(ACC_FLAGS) -I $(ACC_KERNELS)/atax $(POLY_SRC) $(ACC_KERNELS)/atax/atax.c $(LDFLAGS) $(ACC_LIBS) -o atax-openacc.exe

# --- gemm ---
gemmopenacc:
	$(CC) $(CFLAGS) $(ACC_FLAGS) -I $(ACC_KERNELS)/gemm $(POLY_SRC) $(ACC_KERNELS)/gemm/gemm.c $(LDFLAGS) $(ACC_LIBS) -o gemm-openacc.exe

# --- syr2k ---
syr2kopenacc:
	$(CC) $(CFLAGS) $(ACC_FLAGS) -I $(ACC_KERNELS)/syr2k $(POLY_SRC) $(ACC_KERNELS)/syr2k/syr2k.c $(LDFLAGS) $(ACC_LIBS) -o syr2k-openacc.exe

# 6. Limpeza
clean:
	rm -f *.exe