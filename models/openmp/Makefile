# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos para o PolyBench-ACC e PARSEC OpenMP (Expert OpenMP)
CORE_DIR       = ../../core/PolyBench-ACC
UTILS_DIR      = ../../core/polybench-c-3.2/utilities
ACC_KERNELS    = $(CORE_DIR)/OpenMP/linear-algebra/kernels
PARSEC_INC_DIR = ../../core/parsec/kernels
PARSEC_OMP_DIR = ../../core/parsec/openmp
POLY_SRC       = $(UTILS_DIR)/polybench.c

DATASET_SIZE ?= 

# 3. Configurações de Compilação
CC = gcc
CFLAGS = -O3 -I $(UTILS_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm

ifeq ($(UNAME_S), Darwin)
    OMP_FLAGS = -Xpreprocessor -fopenmp
    OMP_INC   = -I/opt/homebrew/opt/libomp/include
    OMP_LIBS  = -L/opt/homebrew/opt/libomp/lib -lomp
else
    OMP_FLAGS = -fopenmp
    OMP_LIBS  = -lgomp
endif

# 4. Alvos
.PHONY: all parsec clean
all: 2mmopenmp 3mmopenmp ataxopenmp gemmopenmp syr2kopenmp
parsec: blackscholesopenmp swaptionsopenmp fluidanimateopenmp streamclusteropenmp freqmineopenmp

# Nota: Buscamos o arquivo .c dentro da estrutura do PolyBench-ACC
2mmopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ACC_KERNELS)/2mm $(POLY_SRC) $(ACC_KERNELS)/2mm/2mm.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-openmp.exe

3mmopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ACC_KERNELS)/3mm $(POLY_SRC) $(ACC_KERNELS)/3mm/3mm.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-openmp.exe

ataxopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ACC_KERNELS)/atax $(POLY_SRC) $(ACC_KERNELS)/atax/atax.c $(LDFLAGS) $(OMP_LIBS) -o atax-openmp.exe

gemmopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ACC_KERNELS)/gemm $(POLY_SRC) $(ACC_KERNELS)/gemm/gemm.c $(LDFLAGS) $(OMP_LIBS) -o gemm-openmp.exe

syr2kopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ACC_KERNELS)/syr2k $(POLY_SRC) $(ACC_KERNELS)/syr2k/syr2k.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-openmp.exe

# Regras buscando os kernels OpenMP de referência do PARSEC (core/parsec/openmp)
blackscholesopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_INC_DIR)/blackscholes $(POLY_SRC) $(PARSEC_OMP_DIR)/blackscholes/blackscholes.c $(LDFLAGS) $(OMP_LIBS) -o blackscholes-openmp.exe

swaptionsopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_INC_DIR)/swaptions $(POLY_SRC) $(PARSEC_OMP_DIR)/swaptions/swaptions.c $(LDFLAGS) $(OMP_LIBS) -o swaptions-openmp.exe

fluidanimateopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_INC_DIR)/fluidanimate $(POLY_SRC) $(PARSEC_OMP_DIR)/fluidanimate/fluidanimate.c $(LDFLAGS) $(OMP_LIBS) -o fluidanimate-openmp.exe

streamclusteropenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_INC_DIR)/streamcluster $(POLY_SRC) $(PARSEC_OMP_DIR)/streamcluster/streamcluster.c $(LDFLAGS) $(OMP_LIBS) -o streamcluster-openmp.exe

freqmineopenmp:
	$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_INC_DIR)/freqmine $(POLY_SRC) $(PARSEC_OMP_DIR)/freqmine/freqmine.c $(LDFLAGS) $(OMP_LIBS) -o freqmine-openmp.exe

clean:
	rm -f *.exe