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

check:
	python3 scripts/check_env.py

analyze:
	@echo "📊 Gerando métricas e visualizações estatísticas..."
	python3 $(SCRIPTS_DIR)/analyzer.py

analyze-speedup:
	@echo "📈 Gerando gráficos de speedup por dataset..."
	python3 analysis_scripts/speedup_grafico.py

analyze-stats:
	@echo "📉 Gerando gráficos estatísticos com desvio padrão..."
	python3 analysis_scripts/speedup_estatistico.py

analyze-data:
	@echo "📋 Analisando dados consolidados..."
	python3 analysis_scripts/analise_por_dataset.py

analyze-latex:
	@echo "📄 Gerando tabelas LaTeX..."
	python3 analysis_scripts/gerar_tabelas_latex.py

analyze-all: analyze-speedup analyze-stats analyze-data analyze-latex
	@echo "✅ Todas as análises foram executadas com sucesso!"
	@echo ""
	@echo "📁 Arquivos gerados em results/:"
	@echo "  • Gráficos: *.png"
	@echo "  • Dados: *.csv"
	@echo "  • Tabelas: *.tex"

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
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║          COMANDOS DISPONÍVEIS - OpenMP Optimized               ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🔨 COMPILAÇÃO:"
	@echo "  make all                - Compila todos os modelos"
	@echo ""
	@echo "🏃 EXECUÇÃO:"
	@echo "  make run                - Executa benchmarks (N_THREADS=8)"
	@echo "  make scale              - Executa bateria de escalabilidade"
	@echo ""
	@echo "📊 ANÁLISE DETALHADA:"
	@echo "  make analyze            - Análise básica (script analyzer.py)"
	@echo "  make analyze-speedup    - Gráficos de speedup por dataset"
	@echo "  make analyze-stats      - Gráficos com desvio padrão"
	@echo "  make analyze-data       - Análise consolidada de dados"
	@echo "  make analyze-latex      - Tabelas LaTeX para artigos"
	@echo "  make analyze-all        - Executa TODAS as análises ✨"
	@echo ""
	@echo "🧹 MANUTENÇÃO:"
	@echo "  make clean              - Remove binários e resultados"
	@echo "  make check              - Verifica o ambiente"
	@echo ""
	@echo "📁 ESTRUTURA:"
	@echo "  make help               - Mostra esta mensagem"
	@echo ""