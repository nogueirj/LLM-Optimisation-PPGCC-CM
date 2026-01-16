# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Configurações de Caminhos (Centralizados)
# Estrutura esperada: OpenMP-Optimized/models/qwen
CORE_DIR    = ../../core/polybench-c-3.2
UTILS_DIR   = $(CORE_DIR)/utilities
KERNELS_DIR = $(CORE_DIR)/linear-algebra/kernels
POLY_SRC    = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação
CC = gcc
# O CFLAGS aponta para UTILS_DIR para garantir que o polybench.h seja encontrado
CFLAGS = -O3 -I $(UTILS_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm

# 4. Personalização de flags por SO (Mac vs Linux)
ifeq ($(UNAME_S), Darwin)
    # macOS (M1 Pro + Homebrew libomp)
    OMP_FLAGS = -Xpreprocessor -fopenmp
    OMP_INC   = -I/opt/homebrew/opt/libomp/include
    OMP_LIBS  = -L/opt/homebrew/opt/libomp/lib -lomp
else
    # Ubuntu/Linux
    OMP_FLAGS = -fopenmp
    OMP_INC   = 
    OMP_LIBS  = -lgomp
endif

# 5. Alvo Principal (Focado nos kernels otimizados pelo Qwen)
all: 2mmqwen 3mmqwen ataxqwen gemmqwen syr2kqwen 

# --- 2mm ---
2mmqwen: 2mm/2mm_openmp_qwen_optmized.c $(KERNELS_DIR)/2mm/2mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) 2mm/2mm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-qwen.exe

# --- 3mm ---
3mmqwen: 3mm/3mm_openmp_qwen_optmized.c $(KERNELS_DIR)/3mm/3mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) 3mm/3mm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-qwen.exe

# --- atax ---
ataxqwen: atax/atax_openmp_qwen_optmized.c $(KERNELS_DIR)/atax/atax.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) atax/atax_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o atax-qwen.exe

# --- gemm ---
gemmqwen: gemm/gemm_openmp_qwen_optmized.c $(KERNELS_DIR)/gemm/gemm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) gemm/gemm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o gemm-qwen.exe

# --- syr2k ---
syr2kqwen: syr2k/syr2k_openmp_qwen_optmized.c $(KERNELS_DIR)/syr2k/syr2k.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) syr2k/syr2k_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-qwen.exe

# 6. Limpeza
clean:
	rm -f *.exe