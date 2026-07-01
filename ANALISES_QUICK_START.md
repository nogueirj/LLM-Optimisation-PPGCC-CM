# 🚀 QUICK START - Análises

## Forma Mais Simples (Makefile)

```bash
make analyze-all
```

## Alternativas

### Executar análise específica:
```bash
make analyze-speedup    # Apenas gráficos de speedup
make analyze-stats      # Apenas gráficos estatísticos
make analyze-data       # Apenas dados consolidados
make analyze-latex      # Apenas tabelas LaTeX
```

### Ver todos os comandos:
```bash
make help
```

### Usar Python diretamente:
```bash
python3 executar_analises.py
```

## 📊 O que é Gerado?

Após executar, você terá em `results/`:

- **7 Gráficos PNG**: Visualizações de speedup
- **4 Arquivos CSV**: Dados consolidados
- **4 Tabelas LaTeX**: Prontas para artigos

## ⏱️ Tempo de Execução

- `make analyze-speedup`: ~2-3 segundos
- `make analyze-stats`: ~2-3 segundos
- `make analyze-data`: ~1 segundo
- `make analyze-latex`: ~3-5 segundos
- **Total `make analyze-all`: ~8-15 segundos**

## 🎯 Fluxo Recomendado

```bash
# 1. Rodar benchmarks
make run N_THREADS=8

# 2. Executar TODAS as análises
make analyze-all

# 3. Revisar resultados em results/
```

---

**É isso! Simples e rápido! ⚡**
