# 1. Detecção do Sistema Operacional
UNAME_S := $(shell uname -s)

# 2. Caminhos RELATIVOS CORRETOS
CORE_DIR    = ../../core/polybench-c-3.2
UTILS_DIR   = $(CORE_DIR)/utilities
KERNELS_DIR = $(CORE_DIR)/linear-algebra/kernels
PARSEC_DIR  = ../../core/parsec/kernels
ANON_DIR    = ../../core/anonymized/op_x
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

# 5. Alvos (PolyBench e PARSEC)
.PHONY: all parsec anon clean 2mm 3mm atax gemm syr2k blackscholes swaptions fluidanimate streamcluster freqmine op_x
all: 2mm 3mm atax gemm syr2k
parsec: blackscholes swaptions fluidanimate streamcluster freqmine
anon: op_x

# --- PolyBench: 2mm ---
2mm: 2mm/2mm.c $(KERNELS_DIR)/2mm/2mm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/2mm $(POLY_SRC) 2mm/2mm.c $(LDFLAGS) $(OMP_LIBS) -o 2mm-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] 2mm-codestral-openmp_16b.exe" || echo "  [ERRO] 2mm-codestral-openmp_16b.exe falhou na compilacao"

# --- PolyBench: 3mm ---
3mm: 3mm/3mm.c $(KERNELS_DIR)/3mm/3mm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/3mm $(POLY_SRC) 3mm/3mm.c $(LDFLAGS) $(OMP_LIBS) -o 3mm-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] 3mm-codestral-openmp_16b.exe" || echo "  [ERRO] 3mm-codestral-openmp_16b.exe falhou na compilacao"

# --- PolyBench: atax ---
atax: atax/atax.c $(KERNELS_DIR)/atax/atax.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/atax $(POLY_SRC) atax/atax.c $(LDFLAGS) $(OMP_LIBS) -o atax-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] atax-codestral-openmp_16b.exe" || echo "  [ERRO] atax-codestral-openmp_16b.exe falhou na compilacao"

# --- PolyBench: gemm ---
gemm: gemm/gemm.c $(KERNELS_DIR)/gemm/gemm.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/gemm $(POLY_SRC) gemm/gemm.c $(LDFLAGS) $(OMP_LIBS) -o gemm-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] gemm-codestral-openmp_16b.exe" || echo "  [ERRO] gemm-codestral-openmp_16b.exe falhou na compilacao"

# --- PolyBench: syr2k ---
syr2k: syr2k/syr2k.c $(KERNELS_DIR)/syr2k/syr2k.h
	@$(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(KERNELS_DIR)/syr2k $(POLY_SRC) syr2k/syr2k.c $(LDFLAGS) $(OMP_LIBS) -o syr2k-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] syr2k-codestral-openmp_16b.exe" || echo "  [ERRO] syr2k-codestral-openmp_16b.exe falhou na compilacao"

# --- PARSEC: blackscholes ---
blackscholes:
	@if [ -f blackscholes/blackscholes.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_DIR)/blackscholes $(POLY_SRC) blackscholes/blackscholes.c $(LDFLAGS) $(OMP_LIBS) -o blackscholes-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] blackscholes-codestral-openmp_16b.exe" || echo "  [ERRO] blackscholes-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] blackscholes/blackscholes.c ausente"; fi

# --- PARSEC: swaptions ---
swaptions:
	@if [ -f swaptions/swaptions.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_DIR)/swaptions $(POLY_SRC) swaptions/swaptions.c $(LDFLAGS) $(OMP_LIBS) -o swaptions-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] swaptions-codestral-openmp_16b.exe" || echo "  [ERRO] swaptions-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] swaptions/swaptions.c ausente"; fi

# --- PARSEC: fluidanimate ---
fluidanimate:
	@if [ -f fluidanimate/fluidanimate.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_DIR)/fluidanimate $(POLY_SRC) fluidanimate/fluidanimate.c $(LDFLAGS) $(OMP_LIBS) -o fluidanimate-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] fluidanimate-codestral-openmp_16b.exe" || echo "  [ERRO] fluidanimate-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] fluidanimate/fluidanimate.c ausente"; fi

# --- PARSEC: streamcluster ---
streamcluster:
	@if [ -f streamcluster/streamcluster.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_DIR)/streamcluster $(POLY_SRC) streamcluster/streamcluster.c $(LDFLAGS) $(OMP_LIBS) -o streamcluster-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] streamcluster-codestral-openmp_16b.exe" || echo "  [ERRO] streamcluster-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] streamcluster/streamcluster.c ausente"; fi

# --- PARSEC: freqmine ---
freqmine:
	@if [ -f freqmine/freqmine.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(PARSEC_DIR)/freqmine $(POLY_SRC) freqmine/freqmine.c $(LDFLAGS) $(OMP_LIBS) -o freqmine-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] freqmine-codestral-openmp_16b.exe" || echo "  [ERRO] freqmine-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] freqmine/freqmine.c ausente"; fi

# --- ANONIMIZADO: op_x (compute_pipeline) ---
op_x:
	@if [ -f op_x/op_x.c ]; then $(CC) $(CFLAGS) $(OMP_INC) $(OMP_FLAGS) -I $(ANON_DIR) $(POLY_SRC) op_x/op_x.c $(LDFLAGS) $(OMP_LIBS) -o op_x-codestral-openmp_16b.exe 2>/dev/null && echo "  [OK] op_x-codestral-openmp_16b.exe" || echo "  [ERRO] op_x-codestral-openmp_16b.exe falhou na compilacao"; else echo "  [SKIP] op_x/op_x.c ausente"; fi

# 6. Limpeza
clean:
	rm -f *.exe
