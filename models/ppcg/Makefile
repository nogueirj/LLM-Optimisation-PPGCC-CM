# =============================================================
#  Makefile PPCG
#  Local deste arquivo: models/ppcg/
#
#  Estrutura do projeto:
#    ../../core/polybench-c-3.2/       → fontes originais
#    ./                                → .ppcg.c gerados + .exe
#
#  Fluxo por kernel:
#    core/.../2mm/2mm.c
#      → [Docker/PPCG]  → models/ppcg/2mm/2mm.ppcg.c
#        → [GCC -fopenmp] → models/ppcg/2mm-ppcg.exe
# =============================================================

# ── Raiz do projeto (OpenMP Optimized/) ──────────────────────
OMP_ROOT := $(abspath ../..)

# ── Fontes do PolyBench ──────────────────────────────────────
POLYBENCH_ROOT = ../../core/polybench-c-3.2
KERNELS_DIR    = $(POLYBENCH_ROOT)/linear-algebra/kernels
UTILITIES_DIR  = $(POLYBENCH_ROOT)/utilities
POLY_SRC       = $(UTILITIES_DIR)/polybench.c

# ── Destino dos .ppcg.c = aqui mesmo (.) ─────────────────────
PPCG_MODELS = .

# ── Compilador ───────────────────────────────────────────────
CC           = gcc
DATASET_SIZE ?=
CFLAGS       = -O3 -fopenmp -I$(UTILITIES_DIR) -DPOLYBENCH_TIME $(DATASET_SIZE)
LDFLAGS      = -lm

# ── Docker + PPCG ────────────────────────────────────────────
# Monta OpenMP Optimized/ inteiro como /omp.
# Dentro do container:
#   /omp/core/polybench-c-3.2/utilities/               → headers
#   /omp/core/polybench-c-3.2/linear-algebra/kernels/  → fontes
#   /omp/models/ppcg/                                   → saída (aqui)
PPCG = docker run --rm \
           -v "$(OMP_ROOT):/omp" \
           ppcg:openmp \
           ppcg --target=c \
                --openmp \
                -I /omp/core/polybench-c-3.2/utilities

# ── Macro de geração ─────────────────────────────────────────
# $(call ppcg_gen, <kernel>)
define ppcg_gen
	mkdir -p $(PPCG_MODELS)/$(1)
	$(PPCG) \
	    -I /omp/core/polybench-c-3.2/linear-algebra/kernels/$(1) \
	    /omp/core/polybench-c-3.2/linear-algebra/kernels/$(1)/$(1).c \
	    -o /omp/models/ppcg/$(1)/$(1).ppcg.c
endef

# =============================================================
#  ALVOS
# =============================================================
all: 2mm-ppcg.exe 3mm-ppcg.exe atax-ppcg.exe gemm-ppcg.exe syr2k-ppcg.exe

# ── 2mm ──────────────────────────────────────────────────────
$(PPCG_MODELS)/2mm/2mm.ppcg.c: $(KERNELS_DIR)/2mm/2mm.c
	$(call ppcg_gen,2mm)

2mm-ppcg.exe: $(PPCG_MODELS)/2mm/2mm.ppcg.c
	$(CC) $(CFLAGS) -I$(KERNELS_DIR)/2mm \
	    $(POLY_SRC) $< $(LDFLAGS) -o $@

# ── 3mm ──────────────────────────────────────────────────────
$(PPCG_MODELS)/3mm/3mm.ppcg.c: $(KERNELS_DIR)/3mm/3mm.c
	$(call ppcg_gen,3mm)

3mm-ppcg.exe: $(PPCG_MODELS)/3mm/3mm.ppcg.c
	$(CC) $(CFLAGS) -I$(KERNELS_DIR)/3mm \
	    $(POLY_SRC) $< $(LDFLAGS) -o $@

# ── atax ─────────────────────────────────────────────────────
$(PPCG_MODELS)/atax/atax.ppcg.c: $(KERNELS_DIR)/atax/atax.c
	$(call ppcg_gen,atax)

atax-ppcg.exe: $(PPCG_MODELS)/atax/atax.ppcg.c
	$(CC) $(CFLAGS) -I$(KERNELS_DIR)/atax \
	    $(POLY_SRC) $< $(LDFLAGS) -o $@

# ── gemm ─────────────────────────────────────────────────────
$(PPCG_MODELS)/gemm/gemm.ppcg.c: $(KERNELS_DIR)/gemm/gemm.c
	$(call ppcg_gen,gemm)

gemm-ppcg.exe: $(PPCG_MODELS)/gemm/gemm.ppcg.c
	$(CC) $(CFLAGS) -I$(KERNELS_DIR)/gemm \
	    $(POLY_SRC) $< $(LDFLAGS) -o $@

# ── syr2k ────────────────────────────────────────────────────
$(PPCG_MODELS)/syr2k/syr2k.ppcg.c: $(KERNELS_DIR)/syr2k/syr2k.c
	$(call ppcg_gen,syr2k)

syr2k-ppcg.exe: $(PPCG_MODELS)/syr2k/syr2k.ppcg.c
	$(CC) $(CFLAGS) -I$(KERNELS_DIR)/syr2k \
	    $(POLY_SRC) $< $(LDFLAGS) -o $@

# =============================================================
#  ALVOS AUXILIARES
# =============================================================

# Só gera os .ppcg.c sem compilar — para revisar o código anotado
generate: \
    $(PPCG_MODELS)/2mm/2mm.ppcg.c \
    $(PPCG_MODELS)/3mm/3mm.ppcg.c \
    $(PPCG_MODELS)/atax/atax.ppcg.c \
    $(PPCG_MODELS)/gemm/gemm.ppcg.c \
    $(PPCG_MODELS)/syr2k/syr2k.ppcg.c

# Remove só os executáveis
clean:
	rm -f *.exe

# Remove executáveis + subpastas com os .ppcg.c gerados
clean-all: clean
	rm -rf ./2mm ./3mm ./atax ./gemm ./syr2k

.PHONY: all generate clean clean-all