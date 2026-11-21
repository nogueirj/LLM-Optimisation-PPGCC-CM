# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos RELATIVOS (Para chegar na raiz e entrar em core)
CORE_DIR       = ../../core/polybench-c-3.2
UTILS_DIR      = $(CORE_DIR)/utilities
KERNELS_DIR    = $(CORE_DIR)/linear-algebra/kernels
PARSEC_SEQ_DIR = ../../core/parsec/kernels
ANON_SEQ_DIR   = ../../core/anonymized/op_x
POLY_SRC       = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação (SEM OPENMP)
CC = gcc
CFLAGS = -O3 -I $(UTILS_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm

# 4. Alvos (Kernels Originais PolyBench, PARSEC e Anonimizado)
.PHONY: all parsec anon clean
all: 2mmseq 3mmseq ataxseq gemmseq syr2kseq
parsec: blackscholesseq swaptionsseq fluidanimateseq streamclusterseq freqmineseq
anon: opxseq

# Regras buscando o código original diretamente da pasta core (PolyBench)
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

# Regras buscando os kernels sequenciais do PARSEC (core/parsec/kernels)
blackscholesseq: $(PARSEC_SEQ_DIR)/blackscholes/blackscholes.c $(PARSEC_SEQ_DIR)/blackscholes/blackscholes.h
	$(CC) $(CFLAGS) -I $(PARSEC_SEQ_DIR)/blackscholes $(POLY_SRC) $(PARSEC_SEQ_DIR)/blackscholes/blackscholes.c $(LDFLAGS) -o blackscholes-seq.exe

swaptionsseq: $(PARSEC_SEQ_DIR)/swaptions/swaptions.c $(PARSEC_SEQ_DIR)/swaptions/swaptions.h
	$(CC) $(CFLAGS) -I $(PARSEC_SEQ_DIR)/swaptions $(POLY_SRC) $(PARSEC_SEQ_DIR)/swaptions/swaptions.c $(LDFLAGS) -o swaptions-seq.exe

fluidanimateseq: $(PARSEC_SEQ_DIR)/fluidanimate/fluidanimate.c $(PARSEC_SEQ_DIR)/fluidanimate/fluidanimate.h
	$(CC) $(CFLAGS) -I $(PARSEC_SEQ_DIR)/fluidanimate $(POLY_SRC) $(PARSEC_SEQ_DIR)/fluidanimate/fluidanimate.c $(LDFLAGS) -o fluidanimate-seq.exe

streamclusterseq: $(PARSEC_SEQ_DIR)/streamcluster/streamcluster.c $(PARSEC_SEQ_DIR)/streamcluster/streamcluster.h
	$(CC) $(CFLAGS) -I $(PARSEC_SEQ_DIR)/streamcluster $(POLY_SRC) $(PARSEC_SEQ_DIR)/streamcluster/streamcluster.c $(LDFLAGS) -o streamcluster-seq.exe

freqmineseq: $(PARSEC_SEQ_DIR)/freqmine/freqmine.c $(PARSEC_SEQ_DIR)/freqmine/freqmine.h
	$(CC) $(CFLAGS) -I $(PARSEC_SEQ_DIR)/freqmine $(POLY_SRC) $(PARSEC_SEQ_DIR)/freqmine/freqmine.c $(LDFLAGS) -o freqmine-seq.exe

# Regra para o método anonimizado (op_x / compute_pipeline)
opxseq: $(ANON_SEQ_DIR)/op_x.c $(ANON_SEQ_DIR)/op_x.h
	$(CC) $(CFLAGS) -I $(ANON_SEQ_DIR) $(POLY_SRC) $(ANON_SEQ_DIR)/op_x.c $(LDFLAGS) -o op_x-seq.exe

clean:
	rm -f *.exe