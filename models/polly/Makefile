# Makefile para Polly - Otimizado para Ubuntu (LLVM 18)
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S), Darwin)
    # Configuração para macOS (Homebrew LLVM)
    CC = /opt/homebrew/opt/llvm/bin/clang
    OMP_INC   = -I/opt/homebrew/opt/llvm/include
    OMP_LIBS  = -L/opt/homebrew/opt/llvm/lib -lomp -Wl,-rpath,/opt/homebrew/opt/llvm/lib
else
    # Configuração para Ubuntu com LLVM 18
    CC = clang-18
    OMP_INC   = 
    # No Linux/Clang, -fopenmp lida com a linkagem da libomp automaticamente
    OMP_LIBS  = -fopenmp
endif

# Flags de Otimização Poliedral (Polly)
POLLY_FLAGS = -mllvm -polly \
              -mllvm -polly-parallel \
              -mllvm -polly-tiling \
              -mllvm -polly-invariant-load-hoisting \
              -mllvm -polly-process-unprofitable

DATASET_SIZE ?=
CFLAGS = -O3 -I ../../core/polybench-c-3.2/utilities -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS = -lm
POLY_SRC = ../../core/polybench-c-3.2/utilities/polybench.c
# Variável para simplificar os caminhos dos kernels
KERNELS_DIR = ../../core/polybench-c-3.2/linear-algebra/kernels

all: 2mmpolly 3mmpolly ataxpolly gemmpolly syr2kpolly

2mmpolly: $(KERNELS_DIR)/2mm/2mm.c $(KERNELS_DIR)/2mm/2mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(POLLY_FLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) $(KERNELS_DIR)/2mm/2mm.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-polly.exe

3mmpolly: $(KERNELS_DIR)/3mm/3mm.c $(KERNELS_DIR)/3mm/3mm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(POLLY_FLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) $(KERNELS_DIR)/3mm/3mm.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-polly.exe

ataxpolly: $(KERNELS_DIR)/atax/atax.c $(KERNELS_DIR)/atax/atax.h
	$(CC) $(CFLAGS) $(OMP_INC) $(POLLY_FLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) $(KERNELS_DIR)/atax/atax.c $(LDFLAGS) $(OMP_LIBS) -o atax-polly.exe
    
gemmpolly: $(KERNELS_DIR)/gemm/gemm.c $(KERNELS_DIR)/gemm/gemm.h
	$(CC) $(CFLAGS) $(OMP_INC) $(POLLY_FLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) $(KERNELS_DIR)/gemm/gemm.c $(LDFLAGS) $(OMP_LIBS) -o gemm-polly.exe

syr2kpolly: $(KERNELS_DIR)/syr2k/syr2k.c $(KERNELS_DIR)/syr2k/syr2k.h
	$(CC) $(CFLAGS) $(OMP_INC) $(POLLY_FLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) $(KERNELS_DIR)/syr2k/syr2k.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-polly.exe

clean:
	rm -f *.exe
