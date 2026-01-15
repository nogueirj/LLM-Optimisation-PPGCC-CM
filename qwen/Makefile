# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

DATASET_SIZE ?= -DSTANDARD_DATASET

# 2. Configurações Gerais
CC = gcc
CFLAGS = -O3 -I ../polybench-c-3.2/utilities -DPOLYBENCH_TIME $(DATASET_SIZE)
POLY_SRC = ../polybench-c-3.2/utilities/polybench.c
LDFLAGS = -lm

# 3. Personalização por SO
ifeq ($(UNAME_S), Darwin)
    # Configurações para macOS (Apple Silicon + Homebrew)
    OMP_FLAGS = -Xpreprocessor -fopenmp
    OMP_LIBS = -L/opt/homebrew/opt/libomp/lib -lomp
    INC_FLAGS = -I/opt/homebrew/opt/libomp/include
else
    # Configurações para Ubuntu/Linux
    OMP_FLAGS = -fopenmp
    OMP_LIBS = 
    INC_FLAGS = 
endif

# 4. Alvos de Compilação
ALL_TARGETS = 2mmseq 2mmqwen 3mmseq 3mmqwen ataxseq ataxqwen gemmseq gemmqwen syr2kseq syr2kqwen

all: $(ALL_TARGETS)

# Exemplo de regra para Sequencial
2mmseq: 2mm/2mm.c 2mm/2mm.h
	$(CC) $(CFLAGS) -I 2mm $(POLY_SRC) 2mm/2mm.c $(LDFLAGS) -o 2mm-seq.exe

# Exemplo de regra para OpenMP (Qwen Optimized)
2mmqwen: 2mm/2mm_openmp_qwen_optmized.c 2mm/2mm.h
	$(CC) $(CFLAGS) $(INC_FLAGS) $(OMP_FLAGS) -I 2mm $(POLY_SRC) 2mm/2mm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-qwen.exe

# --- Repita o padrão para os demais ou use regras genéricas ---

3mmseq: 3mm/3mm.c 3mm/3mm.h
	$(CC) $(CFLAGS) -I 3mm $(POLY_SRC) 3mm/3mm.c $(LDFLAGS) -o 3mm-seq.exe

3mmqwen: 3mm/3mm_openmp_qwen_optmized.c 3mm/3mm.h
	$(CC) $(CFLAGS) $(INC_FLAGS) $(OMP_FLAGS) -I 3mm $(POLY_SRC) 3mm/3mm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-qwen.exe

ataxseq: atax/atax.c atax/atax.h
	$(CC) $(CFLAGS) -I atax $(POLY_SRC) atax/atax.c $(LDFLAGS) -o atax-seq.exe

ataxqwen: atax/atax_openmp_qwen_optmized.c atax/atax.h
	$(CC) $(CFLAGS) $(INC_FLAGS) $(OMP_FLAGS) -I atax $(POLY_SRC) atax/atax_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o atax-qwen.exe

gemmseq: gemm/gemm.c gemm/gemm.h
	$(CC) $(CFLAGS) -I gemm $(POLY_SRC) gemm/gemm.c $(LDFLAGS) -o gemm-seq.exe

gemmqwen: gemm/gemm_openmp_qwen_optmized.c gemm/gemm.h
	$(CC) $(CFLAGS) $(INC_FLAGS) $(OMP_FLAGS) -I gemm $(POLY_SRC) gemm/gemm_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o gemm-qwen.exe

syr2kseq: syr2k/syr2k.c syr2k/syr2k.h
	$(CC) $(CFLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k.c $(LDFLAGS) -o syr2k-seq.exe

syr2kqwen: syr2k/syr2k_openmp_qwen_optmized.c syr2k/syr2k.h
	$(CC) $(CFLAGS) $(INC_FLAGS) $(OMP_FLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k_openmp_qwen_optmized.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-qwen.exe

clean:
	rm -f *.exe