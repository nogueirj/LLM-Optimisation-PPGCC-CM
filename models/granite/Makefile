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

# 3. Personalização de flags por SO
ifeq ($(UNAME_S), Darwin)
    OMP_FLAGS = -Xpreprocessor -fopenmp
    OMP_INC   = -I/opt/homebrew/opt/libomp/include
    OMP_LIBS  = -L/opt/homebrew/opt/libomp/lib -lomp
else
    OMP_FLAGS = -fopenmp
    OMP_INC   = 
    OMP_LIBS  = 
endif

# 4. Alvo Principal
all: 2mmseq 2mmgranite 3mmseq 3mmgranite ataxseq ataxgranite gemmseq gemmgranite syr2kseq syr2kgranite 

# --- 2mm ---
2mmseq: 2mm/2mm.c 2mm/2mm.h
	$(CC) $(CFLAGS) -I 2mm $(POLY_SRC) 2mm/2mm.c $(LDFLAGS) -o 2mm-seq.exe

2mmgranite: 2mm/2mm_openmp_granite_optmized.c 2mm/2mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I 2mm $(POLY_SRC) 2mm/2mm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-granite.exe

# --- 3mm ---
3mmseq: 3mm/3mm.c 3mm/3mm.h
	$(CC) $(CFLAGS) -I 3mm $(POLY_SRC) 3mm/3mm.c $(LDFLAGS) -o 3mm-seq.exe

3mmgranite: 3mm/3mm_openmp_granite_optmized.c 3mm/3mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I 3mm $(POLY_SRC) 3mm/3mm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-granite.exe

# --- atax ---
ataxseq: atax/atax.c atax/atax.h
	$(CC) $(CFLAGS) -I atax $(POLY_SRC) atax/atax.c $(LDFLAGS) -o atax-seq.exe

ataxgranite: atax/atax_openmp_granite_optmized.c atax/atax.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I atax $(POLY_SRC) atax/atax_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o atax-granite.exe

# --- gemm ---
gemmseq: gemm/gemm.c gemm/gemm.h
	$(CC) $(CFLAGS) -I gemm $(POLY_SRC) gemm/gemm.c $(LDFLAGS) -o gemm-seq.exe

gemmgranite: gemm/gemm_openmp_granite_optmized.c gemm/gemm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I gemm $(POLY_SRC) gemm/gemm_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o gemm-granite.exe

# --- syr2k ---
syr2kseq: syr2k/syr2k.c syr2k/syr2k.h
	$(CC) $(CFLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k.c $(LDFLAGS) -o syr2k-seq.exe

syr2kgranite: syr2k/syr2k_openmp_granite_optmized.c syr2k/syr2k.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k_openmp_granite_optmized.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-granite.exe

clean:
	rm -f *.exe