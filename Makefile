# =================================================================
# MASTER MAKEFILE - ORQUESTRADOR DE EXPERIMENTOS HPC (CORRIGIDO)
# =================================================================

# 1. DEFINIÇÕES DE DIRETÓRIOS
MODELS_DIR  = models
SCRIPTS_DIR = scripts
RESULTS_DIR = results

# 2. LISTA OFICIAL DE MODELOS
MODELS = sequential chatgpt codellama codestral deepseekcoder granite gemini qwen polly openmp

# 3. PARÂMETROS DE AMBIENTE
DATASET_SIZE ?= 
N_THREADS    ?= 8

# 4. ALVOS VIRTUAIS
.PHONY: all clean run analyze scale help check $(MODELS)

# -----------------------------------------------------------------
# ALVOS DE COMPILAÇÃO
# -----------------------------------------------------------------

# Alvo principal: compila todos os modelos
all: $(MODELS)

$(MODELS):
	@if [ -d $(MODELS_DIR)/$@ ]; then \
		echo "=========================================================="; \
		echo "🔨 COMPILANDO MODELO: $@"; \
		echo "=========================================================="; \
		$(MAKE) -C $(MODELS_DIR)/$@ DATASET_SIZE=$(DATASET_SIZE) || true; \
	else \
		echo "⚠️  Aviso: Diretório $(MODELS_DIR)/$@ não encontrado."; \
	fi

# -----------------------------------------------------------------
# ALVOS DE EXECUÇÃO E ANÁLISE
# -----------------------------------------------------------------

run:
	@echo "🏃 Iniciando benchmarks com $(N_THREADS) threads..."
	python3 $(SCRIPTS_DIR)/executor.py $(N_THREADS)

# Alvo de escalabilidade: Builda tudo uma vez e depois só executa
scale:
	@echo "🔨 Fase 1: Compilando todos os modelos (Single Build)..."
	$(MAKE) all DATASET_SIZE=$(DATASET_SIZE)
	@echo "🏃 Fase 2: Iniciando bateria de execução (No-Build Mode)..."
	chmod +x scripts/run_scale.sh
	./scripts/run_scale.sh $(DATASET_SIZE)

# Alvo run simples (apenas para uma execução manual)
run:
	python3 scripts/executor.py $(N_THREADS)

check:
	python3 scripts/check_env.py

analyze:
	@echo "📊 Gerando métricas e visualizações estatísticas..."
	python3 $(SCRIPTS_DIR)/analyzer.py

# -----------------------------------------------------------------
# MANUTENÇÃO E LIMPEZA
# -----------------------------------------------------------------

clean:
	@for dir in $(MODELS); do \
		if [ -d $(MODELS_DIR)/$$dir ]; then \
			echo "🧹 Limpando $$dir..."; \
			$(MAKE) -C $(MODELS_DIR)/$$dir clean || true; \
		fi; \
	done
	@echo "🗑️ Removendo arquivos de resultados..."
	rm -rf $(RESULTS_DIR)/*.csv $(RESULTS_DIR)/*.png $(RESULTS_DIR)/*.tex
	@echo "✨ Limpeza concluída."

help:
	@echo "Comandos disponíveis:"
	@echo "  make all          - Compila todos os modelos (ignora falhas individuais)"
	@echo "  make run          - Executa benchmarks (N_THREADS=8 por padrão)"
	@echo "  make scale        - Executa bateria de escalabilidade total"
	@echo "  make analyze      - Gera gráficos e tabelas LaTeX"
	@echo "  make clean        - Remove binários e resultados antigos"
	@echo "  make check        - Verifica o ambiente de execução"