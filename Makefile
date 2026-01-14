# Makefile Pai - Orquestrador de Experimentos

# 1. Definição das pastas dos modelos
# Nota: Usamos aspas na pasta do DeepSeek devido ao espaço no nome
MODELS = chatgpt codellama codestral qwen starcode "deepseek_coder optmized"

.PHONY: all clean $(MODELS)

# O alvo 'all' tentará compilar todos os modelos
all: $(MODELS)

# 2. Regras individuais para cada diretório
# O comando $(MAKE) -C entra na pasta e executa o Makefile de lá
chatgpt:
	$(MAKE) -C chatgpt

codellama:
	$(MAKE) -C codellama

codestral:
	$(MAKE) -C codestral

qwen:
	$(MAKE) -C qwen

# Regra especial para a pasta com espaço
deepseek:
	$(MAKE) -C "deepseek_coder optmized"

# 3. Regra para limpar todos os binários de todas as pastas
clean:
	$(MAKE) -C chatgpt clean
	$(MAKE) -C codellama clean
	$(MAKE) -C codestral clean
	$(MAKE) -C qwen clean
	$(MAKE) -C "deepseek_coder optmized" clean