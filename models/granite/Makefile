# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos RELATIVOS CORRETOS
# Estrutura: OpenMP-Optimized/models/seu_modelo
# Para chegar na raiz: ../../
CORE_DIR    = ../../core/polybench-c-3.2
UTILS_DIR   = $(CORE_DIR)/utilities
KERNELS_DIR = $(CORE_DIR)/linear-algebra/kernels
POLY_SRC    = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação
CC = gcc
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
    OMP_LIBS  = 
endif

# 5. Alvo Principal
all: 2mmgranite 3mmgranite ataxgranite gemmgranite syr2kgranite 

# --- 2mm ---
2mmgranite: 2mm/2mm_openmp_granite_optmized.c $(KERNELS_DIR)/2mm/2mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) 2mm/2mm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-granite.exe

# --- 3mm ---
3mmgranite: 3mm/3mm_openmp_granite_optmized.c $(KERNELS_DIR)/3mm/3mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) 3mm/3mm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-granite.exe

# --- atax ---
ataxgranite: atax/atax_openmp_granite_optmized.c $(KERNELS_DIR)/atax/atax.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) atax/atax_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o atax-granite.exe

# --- gemm ---
gemmgranite: gemm/gemm_openmp_granite_optmized.c $(KERNELS_DIR)/gemm/gemm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) gemm/gemm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o gemm-granite.exe

# --- syr2k ---
syr2kgranite: syr2k/syr2k_openmp_granite_optmized.c $(KERNELS_DIR)/syr2k/syr2k.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) syr2k/syr2k_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-granite.exe

# 6. Limpeza
clean:
	rm -f *.exe