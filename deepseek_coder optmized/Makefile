# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

DATASET_SIZE ?= -DSTANDARD_DATASET

# 2. Configurações Gerais
CC = gcc
CFLAGS = -O3 -I ../polybench-c-3.2/utilities -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm
POLY_SRC = ../polybench-c-3.2/utilities/polybench.c

# 3. Personalização de flags por SO (Mac vs Linux)
ifeq ($(UNAME_S), Darwin)
    # Configurações para macOS (M1 Pro + Homebrew libomp)
    OMP_FLAGS = -Xpreprocessor -fopenmp
    OMP_INC   = -I/opt/homebrew/opt/libomp/include
    OMP_LIBS  = -L/opt/homebrew/opt/libomp/lib -lomp
else
    # Configurações para Ubuntu/Linux
    OMP_FLAGS = -fopenmp
    OMP_INC   = 
    OMP_LIBS  = 
endif

# 4. Alvo Principal
all: 2mmseq 2mmdeepseekcoder 3mmseq 3mmdeepseekcoder ataxseq ataxdeepseekcoder gemmseq gemmdeepseekcoder syr2kseq syr2kdeepseekcoder 

# --- 2mm ---
2mmseq: 2mm/2mm.c 2mm/2mm.h
	$(CC) $(CFLAGS) -I 2mm $(POLY_SRC) 2mm/2mm.c $(LDFLAGS) -o 2mm-seq.exe

2mmdeepseekcoder: 2mm/2mm_openmp_deepseekcoder_optmized.c 2mm/2mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I 2mm $(POLY_SRC) 2mm/2mm_openmp_deepseekcoder_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-deepseekcoder.exe

# --- 3mm ---
3mmseq: 3mm/3mm.c 3mm/3mm.h
	$(CC) $(CFLAGS) -I 3mm $(POLY_SRC) 3mm/3mm.c $(LDFLAGS) -o 3mm-seq.exe

3mmdeepseekcoder: 3mm/3mm_openmp_deepseekcoder_optmized.c 3mm/3mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I 3mm $(POLY_SRC) 3mm/3mm_openmp_deepseekcoder_optmized.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-deepseekcoder.exe

# --- atax ---
ataxseq: atax/atax.c atax/atax.h
	$(CC) $(CFLAGS) -I atax $(POLY_SRC) atax/atax.c $(LDFLAGS) -o atax-seq.exe

ataxdeepseekcoder: atax/atax_openmp_deepseekcoder_optmized.c atax/atax.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I atax $(POLY_SRC) atax/atax_openmp_deepseekcoder_optmized.c $(LDFLAGS) $(OMP_LIBS) -o atax-deepseekcoder.exe

# --- gemm ---
gemmseq: gemm/gemm.c gemm/gemm.h
	$(CC) $(CFLAGS) -I gemm $(POLY_SRC) gemm/gemm.c $(LDFLAGS) -o gemm-seq.exe

gemmdeepseekcoder: gemm/gemm_openmp_deepseekcoder_optmized.c gemm/gemm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I gemm $(POLY_SRC) gemm/gemm_openmp_deepseekcoder_optmized.c $(LDFLAGS) $(OMP_LIBS) -o gemm-deepseekcoder.exe

# --- syr2k ---
syr2kseq: syr2k/syr2k.c syr2k/syr2k.h
	$(CC) $(CFLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k.c $(LDFLAGS) -o syr2k-seq.exe

syr2kdeepseekcoder: syr2k/syr2k_openmp_deepseekcoder_optmized.c syr2k/syr2k.h
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I syr2k $(POLY_SRC) syr2k/syr2k_openmp_deepseekcoder_optmized.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-deepseekcoder.exe

# 5. Limpeza
clean:
	rm -f *.exe