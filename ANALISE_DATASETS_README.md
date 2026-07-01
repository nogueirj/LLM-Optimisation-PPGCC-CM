## 📊 Análise de Speedup por Dataset

Este sistema automatiza a geração completa de análises de performance separadas por tamanho de dataset.

### 🚀 Execução Rápida

Para executar **todas as análises de uma vez**:

```bash
source .venv/bin/activate
python3 executar_analises.py
```

### 📁 O que é Gerado?

#### 📈 Gráficos PNG (em `results/`)
- **Gráficos por Dataset Individual:**
  - `comparativo_speedup_large.png` - Gráfico de barras do dataset LARGE
  - `comparativo_speedup_standard.png` - Gráfico de barras do dataset STANDARD
  - `comparativo_speedup_datasets.png` - Comparação lado a lado

- **Gráficos com Desvio Padrão (Análise Estatística):**
  - `grafico_speedup_estatistico_large.png` - Com barras de erro
  - `grafico_speedup_estatistico_standard.png` - Com barras de erro
  - `grafico_speedup_estatistico_datasets.png` - Comparação com incerteza

#### 📊 Tabelas CSV (em `results/`)
- `speedup_por_dataset.csv` - Speedup médio por modelo e dataset
- `eficiencia_por_dataset.csv` - Eficiência (Speedup/Threads) por modelo e dataset

#### 📋 Tabelas LaTeX (em `results/`)
- `tabela_ranking_large.tex` - Ranking completo para dataset LARGE
- `tabela_ranking_standard.tex` - Ranking completo para dataset STANDARD
- `tabela_comparativa_global.tex` - Tabela comparativa global

### 📑 Scripts Individuais

Se preferir executar análises específicas:

```bash
# Apenas gráficos de speedup
python3 speedup_grafico.py

# Apenas análise estatística (com barras de erro)
python3 speedup_estatistico.py

# Apenas análise consolidada por dataset
python3 analise_por_dataset.py

# Apenas tabelas LaTeX
python3 gerar_tabelas_latex.py
```

### 📊 Principais Resultados

**Speedup Médio por Dataset:**

| Modelo | LARGE | STANDARD |
|--------|-------|----------|
| Polly | 11.03x | 20.27x |
| ChatGPT | 9.59x | 13.71x |
| Gemini | 9.81x | 12.37x |
| OpenMP | 9.91x | 11.58x |
| Codestral | 8.96x | 10.56x |

**Eficiência por Dataset:**

| Modelo | LARGE | STANDARD |
|--------|-------|----------|
| Polly | 2.127 | 5.404 |
| ChatGPT | 0.756 | 0.940 |
| Gemini | 0.787 | 0.854 |

### 📌 Insights Importantes

1. **Dataset STANDARD** apresenta melhor escalabilidade que LARGE
2. **Polly** domina em speedup absoluto, especialmente em STANDARD
3. **ChatGPT** tem excelente eficiência relativa
4. **CodeLlama** tem performance mais modesta em ambos os datasets
5. Kernel **atax** tem menor speedup (kernel pequeno)
6. Kernel **syr2k** tem maior variabilidade

### 🔧 Dependências

Certifique-se de que tem instalado:
```bash
pip install -r requirements.txt
```

Dependências:
- pandas>=2.0.0
- matplotlib>=3.8.0
- seaborn>=0.13.0
- numpy>=1.26.0
- jinja2>=3.1.0

---

*Última atualização: 21 de Janeiro de 2026*
