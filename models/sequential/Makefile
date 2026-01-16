# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos RELATIVOS (Para chegar na raiz e entrar em core)
CORE_DIR    = ../../core/polybench-c-3.2
UTILS_DIR   = $(CORE_DIR)/utilities
KERNELS_DIR = $(CORE_DIR)/linear-algebra/kernels
POLY_SRC    = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação (SEM OPENMP)
CC = gcc
CFLAGS = -O3 -I $(UTILS_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm

# 4. Alvos (Kernels Originais)
all: 2mmseq 3mmseq ataxseq gemmseq syr2kseq

# Regras buscando o código original diretamente da pasta core
2mmseq: $(KERNELS_DIR)/2mm/2mm.c $(KERNELS_DIR)/2mm/2mm.h
	$(CC) $(CFLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) $(KERNELS_DIR)/2mm/2mm.c $(LDFLAGS) -o 2mm-seq.exe

3mmseq: $(KERNELS_DIR)/3mm/3mm.c $(KERNELS_DIR)/3mm/3mm.h
	$(CC) $(CFLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) $(KERNELS_DIR)/3mm/3mm.c $(LDFLAGS) -o 3mm-seq.exe

ataxseq: $(KERNELS_DIR)/atax/atax.c $(KERNELS_DIR)/atax/atax.h
	$(CC) $(CFLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) $(KERNELS_DIR)/atax/atax.c $(LDFLAGS) -o atax-seq.exe

gemmseq: $(KERNELS_DIR)/gemm/gemm.c $(KERNELS_DIR)/gemm/gemm.h
	$(CC) $(CFLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) $(KERNELS_DIR)/gemm/gemm.c $(LDFLAGS) -o gemm-seq.exe

syr2kseq: $(KERNELS_DIR)/syr2k/syr2k.c $(KERNELS_DIR)/syr2k/syr2k.h
	$(CC) $(CFLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) $(KERNELS_DIR)/syr2k/syr2k.c $(LDFLAGS) -o syr2k-seq.exe

clean:
	rm -f *.exe