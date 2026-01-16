# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos para o PolyBench-ACC (Expert OpenMP)
CORE_DIR    = ../../core/PolyBench-ACC
UTILS_DIR   = ../../core/polybench-c-3.2/utilities
# No PolyBench-ACC, os kernels ficam em subpastas como OpenMP/Linear-Algebra/Kernels/2mm
ACC_KERNELS = $(CORE_DIR)/OpenMP/Linear-Algebra/Kernels
POLY_SRC    = $(UTILS_DIR)/polybench.c

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
all: 2mmopenmp 3mmopenmp ataxopenmp gemmopenmp syr2kopenmp

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

clean:
	rm -f *.exe