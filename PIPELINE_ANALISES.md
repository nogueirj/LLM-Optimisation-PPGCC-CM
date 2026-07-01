# 📊 Pipeline de Análise Completa de Speedup por Dataset

## 🎯 Objetivo

Automatizar a análise completa de performance de modelos de IA em benchmarks OpenMP, separando os resultados por tamanho de dataset (LARGE e STANDARD).

## 🚀 Execução Rápida

### Opção 1: Script Shell (Recomendado)
```bash
./analizar_completo.sh
```

### Opção 2: Python Direto
```bash
source .venv/bin/activate
python3 executar_analises.py
python3 resumo_analises.py
```

## 📊 Pipeline de Processamento

```
raw_times.csv (dados brutos)
    ↓
    ├→ speedup_grafico.py (Gráficos de speedup simples)
    │   └→ comparativo_speedup_*.png
    │
    ├→ speedup_estatistico.py (Gráficos com desvio padrão)
    │   └→ grafico_speedup_estatistico_*.png
    │
    ├→ analise_por_dataset.py (Análise consolidada)
    │   └→ speedup_por_dataset.csv, eficiencia_por_dataset.csv
    │
    └→ gerar_tabelas_latex.py (Tabelas para LaTeX)
        └→ tabela_ranking_*.tex

    ↓
resumo_analises.py (Resumo executivo)
    └→ Exibe principais insights
```

## 📁 Arquivos Gerados

### 🎨 Gráficos (PNG)
- `comparativo_speedup_large.png` - Dataset LARGE
- `comparativo_speedup_standard.png` - Dataset STANDARD  
- `comparativo_speedup_datasets.png` - Comparação lado a lado
- `grafico_speedup_estatistico_large.png` - Com barras de erro (LARGE)
- `grafico_speedup_estatistico_standard.png` - Com barras de erro (STANDARD)
- `grafico_speedup_estatistico_datasets.png` - Comparação estatística

### 📋 Tabelas LaTeX (TEX)
- `tabela_ranking_large.tex` - Ranking de modelos (LARGE, 64 threads)
- `tabela_ranking_standard.tex` - Ranking de modelos (STANDARD, 64 threads)
- `tabela_comparativa_global.tex` - Comparação global

### 📊 Dados (CSV)
- `speedup_por_dataset.csv` - Speedup médio por modelo
- `eficiencia_por_dataset.csv` - Eficiência por modelo

## 📈 Principais Resultados

### Speedup Médio (vezes mais rápido que versão sequencial)

| Modelo | LARGE | STANDARD | Melhoria |
|--------|-------|----------|----------|
| Polly | 11.03x | 20.27x | +83.7% |
| ChatGPT | 9.59x | 13.71x | +42.9% |
| Gemini | 9.81x | 12.37x | +26.0% |
| OpenMP | 9.91x | 11.58x | +16.8% |
| Codestral | 8.96x | 10.56x | +17.9% |
| DeepSeek | 6.49x | 8.37x | +29.0% |
| Qwen | 9.52x | 9.89x | +3.9% |
| Granite | 9.01x | 10.54x | +17.0% |
| CodeLlama | 3.92x | 4.49x | +14.6% |

### Eficiência (Speedup / Threads)

| Modelo | LARGE | STANDARD |
|--------|-------|----------|
| **Polly** | **2.127** | **5.404** |
| ChatGPT | 0.756 | 0.940 |
| Gemini | 0.787 | 0.854 |
| OpenMP | 0.766 | 0.816 |

## 💡 Recomendações

### 1. Para PERFORMANCE MÁXIMA (Dataset STANDARD)
- **Use:** Polly (20.27x)
- **Alternativa:** ChatGPT (13.71x)

### 2. Para EFICIÊNCIA (melhor custo-benefício)
- **Use:** ChatGPT (0.94x em STANDARD) ou Gemini (0.854x)
- Oferecem excelente performance sem overhead excessivo

### 3. Para CONSISTÊNCIA entre datasets
- **Use:** Polly (mantém performance em ambos)
- **Alternativa:** Qwen (menor variação)

### 4. Para DATASETS GRANDES (LARGE)
- **Use:** OpenMP (9.91x) ou Qwen (9.52x)
- Melhor relação custo-benefício em datasets grandes

### 5. Evitar
- **CodeLlama:** Performance significativamente menor
- **DeepSeek:** Performance inconsistente

## 🔧 Scripts Individuais

Se precisar rodar apenas certas análises:

```bash
# Gráficos simples
python3 speedup_grafico.py

# Análise estatística com incerteza
python3 speedup_estatistico.py

# Análise consolidada e tabelas CSV
python3 analise_por_dataset.py

# Tabelas LaTeX
python3 gerar_tabelas_latex.py

# Resumo dos resultados
python3 resumo_analises.py
```

## 📖 Estrutura dos Dados

### raw_times.csv
Formato: `Model,Dataset,Kernel,Threads,Repetition,Time`

Campos:
- **Model:** Nome do modelo (sequential, chatgpt, gemini, etc)
- **Dataset:** Tamanho (standard, large)
- **Kernel:** Algoritmo (2mm, 3mm, atax, gemm, syr2k)
- **Threads:** Número de threads (1-64)
- **Repetition:** Número da repetição (1-10)
- **Time:** Tempo de execução em segundos

## 📊 Cálculos

### Speedup
```
Speedup = T_sequential / T_paralelo
```

### Eficiência  
```
Eficiência = Speedup / Número_de_Threads
```

### Erro no Speedup (propagação de erros)
```
δSpeedup = Speedup × √((δT_seq/T_seq)² + (δT_opt/T_opt)²)
```

## 🔍 Kernels Analisados

- **2mm:** Multiplicação de matrizes (2D × 2D)
- **3mm:** Multiplicação de matrizes (3D)
- **atax:** Matriz-vector (atax)
- **gemm:** Multiplicação de matrizes (BLAS)
- **syr2k:** Operação simétrica de rank-k

## 📝 Uso em LaTeX

Para incluir as tabelas em um documento LaTeX:

```latex
\documentclass{article}
\usepackage{booktabs}
\usepackage{float}

\begin{document}

\input{results/tabela_ranking_standard.tex}
\input{results/tabela_ranking_large.tex}
\input{results/tabela_comparativa_global.tex}

\end{document}
```

## 🐛 Troubleshooting

### Erro: "No module named 'pandas'"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Erro: "File not found: results/raw_times.csv"
Certifique-se de que executou os benchmarks:
```bash
python3 run_benchmarks.py
```

### Gráficos não aparecem
Os gráficos são salvos em PNG. Abra em:
- macOS: Preview
- Linux: Eye of GNOME, Feh, etc
- Windows: Explorer

## 📚 Arquivo de Dependências

Ver `requirements.txt`:
```
pandas>=2.0.0
matplotlib>=3.8.0
seaborn>=0.13.0
numpy>=1.26.0
jinja2>=3.1.0
```

## 🎯 Próximas Etapas

1. ✅ Executar análise completa
2. ✅ Revisar gráficos e tabelas
3. → Compilar relatório LaTeX (opcional)
4. → Integrar em dissertação/relatório

---

**Última atualização:** 21 de Janeiro de 2026  
**Autor:** Sistema de Análise Automática  
**Status:** ✅ Funcional e Automatizado
