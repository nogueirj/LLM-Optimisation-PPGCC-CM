# =================================================================
# MASTER MAKEFILE - ORQUESTRADOR DE EXPERIMENTOS HPC
# Projeto: Comparativo de Otimização OpenMP (IA vs Expert vs Polly)
# =================================================================

# 1. DEFINIÇÕES DE DIRETÓRIOS
MODELS_DIR = models
SCRIPTS_DIR = scripts
RESULTS_DIR = results

# 2. LISTA OFICIAL DE MODELOS (Pastas em models/)
# Nota: Certifique-se de que a pasta deepseekcoder não tem espaços.
MODELS = sequential chatgpt codellama codestral deepseekcoder gemini qwen polly openmp openacc

# 3. PARÂMETROS PADRÃO (Podem ser sobrescritos via linha de comando)
# Exemplo: make all DATASET_SIZE=-DLARGE_DATASET
# Exemplo: make run N_THREADS=64
DATASET_SIZE ?= 
N_THREADS ?= 8

# 4. ALVOS VIRTUAIS (Não são arquivos)
.PHONY: all clean run analyze scale help $(MODELS)

# -----------------------------------------------------------------
# ALVOS DE COMPILAÇÃO
# -----------------------------------------------------------------

# Compila todos os modelos da lista
all: $(MODELS)

# Regra genérica para entrar em cada pasta e disparar o Makefile local
$(MODELS):
	@if [ -d $(MODELS_DIR)/$@ ]; then \
		echo "=========================================================="; \
		echo "🔨 COMPILANDO MODELO: $@"; \
		echo "=========================================================="; \
		$(MAKE) -C $(MODELS_DIR)/$@ DATASET_SIZE=$(DATASET_SIZE); \
	else \
		echo "⚠️  Aviso: Diretório $(MODELS_DIR)/$@ não encontrado."; \
	fi

# -----------------------------------------------------------------
# ALVOS DE EXECUÇÃO E ANÁLISE
# -----------------------------------------------------------------

# Executa a bateria de testes simples (usa N_THREADS padrão ou informada)
run:
	@echo "🏃 Iniciando execução dos benchmarks com $(N_THREADS) threads..."
	python3 $(SCRIPTS_DIR)/executor.py $(N_THREADS)

# Executa o script de escalabilidade completa (Strong Scaling: 1 a 64 threads)
scale:
	@echo "📈 Iniciando bateria de escalabilidade completa..."
	chmod +x $(SCRIPTS_DIR)/run_scaling.sh
	./$(SCRIPTS_DIR)/run_scaling.sh

# Gera gráficos e tabelas baseados no CSV de resultados
analyze:
	@echo "📊 Gerando métricas e visualizações estatísticas..."
	python3 $(SCRIPTS_DIR)/analyzer.py

# -----------------------------------------------------------------
# MANUTENÇÃO E LIMPEZA
# -----------------------------------------------------------------

# Limpa todos os binários .exe e arquivos de resultados
clean:
	@for dir in $(MODELS); do \
		if [ -d $(MODELS_DIR)/$$dir ]; then \
			echo "🧹 Limpando $$dir..."; \
			$(MAKE) -C $(MODELS_DIR)/$$dir clean; \
		fi; \
	done
	@echo "🗑️ Removendo arquivos de resultados..."
	rm -rf $(RESULTS_DIR)/*.csv $(RESULTS_DIR)/*.png $(RESULTS_DIR)/*.tex
	@echo "✨ Limpeza concluída."

# Ajuda rápida
help:
	@echo "Comandos disponíveis:"
	@echo "  make all          - Compila todos os modelos"
	@echo "  make run          - Executa benchmarks (N_THREADS=8 por padrão)"
	@echo "  make scale        - Executa bateria de escalabilidade (1 a 64 threads)"
	@echo "  make analyze      - Gera gráficos e tabelas LaTeX"
	@echo "  make clean        - Remove binários e resultados"