# Variáveis de ambiente
DOCKER_IMAGE = dawncc
POLYBENCH_DIR = ../../core/polybench-c-3.2
OUTDIR = ./output

# Caminhos dos kernels dentro do PolyBench 3.2
2mm_DIR   = linear-algebra/kernels/2mm
3mm_DIR   = linear-algebra/kernels/3mm
gemm_DIR  = linear-algebra/kernels/gemm
atax_DIR  = linear-algebra/kernels/atax
syr2k_DIR = linear-algebra/kernels/syr2k

.PHONY: all 2mm 3mm gemm atax syr2k clean

all: 2mm 3mm gemm atax syr2k

# Macro para criar as regras de cada kernel
define make_kernel
$(1):
	@echo "[DawnCC] ── $(1) ──"
	@mkdir -p $(OUTDIR)
	@docker run --rm -v "$$(abspath $$(POLYBENCH_DIR)):/data" -w /data $(DOCKER_IMAGE) /bin/bash -c '\
		export PATH=$$PATH:/opt/dawncc/llvm-build/bin; \
		export C_INCLUDE_PATH=/data/utilities; \
		/opt/dawncc/DawnCC/run.sh -d /opt/dawncc -f $$($(1)_DIR)/$(1).c -ps 2 -pd false; \
	'
	@if [ -f "$$(POLYBENCH_DIR)/$$($(1)_DIR)/$(1)_AI.c" ]; then \
		mv "$$(POLYBENCH_DIR)/$$($(1)_DIR)/$(1)_AI.c" "$(OUTDIR)/$(1)_omp.c"; \
		echo "  ✅ Sucesso: $(OUTDIR)/$(1)_omp.c gerado com pragmas."; \
	else \
		cp "$$(POLYBENCH_DIR)/$$($(1)_DIR)/$(1).c" "$(OUTDIR)/$(1)_omp.c"; \
		echo "  ⚠️  Nenhum pragma OpenMP foi inserido (arquivo _AI.c não gerado ou falhou)."; \
	fi
endef

$(eval $(call make_kernel,2mm))
$(eval $(call make_kernel,3mm))
$(eval $(call make_kernel,gemm))
$(eval $(call make_kernel,atax))
$(eval $(call make_kernel,syr2k))

clean:
	@echo "Limpando arquivos gerados..."
	rm -rf $(OUTDIR)
