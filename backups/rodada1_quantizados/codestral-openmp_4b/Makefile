# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos RELATIVOS CORRETOS
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
    OMP_LIBS  = -lgomp
endif

# 5. Alvos
.PHONY: all clean 2mm 3mm atax gemm syr2k
all: 2mm 3mm atax gemm syr2k

# --- 2mm ---
2mm: 2mm/2mm.c $(KERNELS_DIR)/2mm/2mm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) 2mm/2mm.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-codestral-openmp_4b.exe 2>/dev/null && echo "  [OK] 2mm-codestral-openmp_4b.exe" || echo "  [ERRO] 2mm-codestral-openmp_4b.exe falhou na compilacao"

# --- 3mm ---
3mm: 3mm/3mm.c $(KERNELS_DIR)/3mm/3mm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) 3mm/3mm.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-codestral-openmp_4b.exe 2>/dev/null && echo "  [OK] 3mm-codestral-openmp_4b.exe" || echo "  [ERRO] 3mm-codestral-openmp_4b.exe falhou na compilacao"

# --- atax ---
atax: atax/atax.c $(KERNELS_DIR)/atax/atax.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) atax/atax.c $(LDFLAGS) $(OMP_LIBS) -o atax-codestral-openmp_4b.exe 2>/dev/null && echo "  [OK] atax-codestral-openmp_4b.exe" || echo "  [ERRO] atax-codestral-openmp_4b.exe falhou na compilacao"

# --- gemm ---
gemm: gemm/gemm.c $(KERNELS_DIR)/gemm/gemm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) gemm/gemm.c $(LDFLAGS) $(OMP_LIBS) -o gemm-codestral-openmp_4b.exe 2>/dev/null && echo "  [OK] gemm-codestral-openmp_4b.exe" || echo "  [ERRO] gemm-codestral-openmp_4b.exe falhou na compilacao"

# --- syr2k ---
syr2k: syr2k/syr2k.c $(KERNELS_DIR)/syr2k/syr2k.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) syr2k/syr2k.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-codestral-openmp_4b.exe 2>/dev/null && echo "  [OK] syr2k-codestral-openmp_4b.exe" || echo "  [ERRO] syr2k-codestral-openmp_4b.exe falhou na compilacao"

# 6. Limpeza
clean:
	rm -f *.exe
