# 📊 Estrutura de Análise do Projeto

## 📁 Organização de Pastas

```
OpenMP Optimized/
├── analysis_scripts/           # ✨ SCRIPTS DE ANÁLISE
│   ├── speedup_grafico.py
│   ├── speedup_estatistico.py
│   ├── analise_por_dataset.py
│   ├── gerar_tabelas_latex.py
│   └── README.md
├── results/                    # 📊 RESULTADOS
│   ├── raw_times.csv
│   ├── *.png (gráficos)
│   ├── *.csv (dados)
│   └── *.tex (tabelas LaTeX)
├── executar_analises.py        # 🚀 SCRIPT MASTER
├── requirements.txt
└── ... (outros arquivos)
```

## 🚀 Como Usar

### Comando Principal com Make (RECOMENDADO ✨)
```bash
make analyze-all
```

Ou individualmente:
```bash
make analyze-speedup        # Gráficos de speedup
make analyze-stats          # Gráficos com desvio padrão
make analyze-data           # Análises consolidadas
make analyze-latex          # Tabelas LaTeX
make analyze                # Análise básica
```

### Comando com Python (alternativa)
```bash
python3 executar_analises.py
```

### Verificar Estrutura
```bash
bash verifica_analises.sh
```

## 📊 Saídas Geradas

Após executar `executar_analises.py`, você terá em `results/`:

### 📈 Gráficos de Speedup
- `comparativo_speedup_large.png` - Dataset large
- `comparativo_speedup_standard.png` - Dataset standard
- `comparativo_speedup_datasets.png` - Comparação lado a lado

### 📉 Gráficos com Desvio Padrão
- `grafico_speedup_estatistico_large.png`
- `grafico_speedup_estatistico_standard.png`
- `grafico_speedup_estatistico_datasets.png`

### 📋 Tabelas CSV
- `speedup_por_dataset.csv` - Dados consolidados
- `eficiencia_por_dataset.csv` - Eficiência por modelo

### 📄 Tabelas LaTeX
- `tabela_ranking_large.tex`
- `tabela_ranking_standard.tex`
- `tabela_comparativa_global.tex`

## 💡 Insights Principais

### Por Dataset
- **STANDARD**: Melhor performance geral (média 10.7x speedup)
  - Polly: 20.27x (campeão)
  - ChatGPT: 13.71x
  
- **LARGE**: Performance mais conservadora (média 9.4x speedup)
  - Polly: 11.03x (campeão)
  - ChatGPT: 9.59x

### Por Modelo
- **Polly**: Extraordinária eficiência (5.4x, 2.1x)
- **ChatGPT**: Excelente eficiência (0.94x, 0.76x)
- **Gemini**: Bom balanço (0.85x, 0.79x)
- **CodeLlama**: Menor eficiência (0.52x ambos)

## 🔧 Configuração

### Requirements
```bash
pip install -r requirements.txt
```

Inclui:
- pandas >= 2.0.0
- matplotlib >= 3.8.0
- seaborn >= 0.13.0
- numpy >= 1.26.0
- jinja2 >= 3.1.0

### Ativando Venv
```bash
source .venv/bin/activate
```

## 📝 Fluxo Completo

```
1. Rodar Benchmarks
   python3 run_benchmarks.py
   
2. Gerar Dados
   └─ raw_times.csv é criado

3. Executar Análises
   python3 executar_analises.py
   
4. Revisar Resultados
   └─ Todos em results/
```

## 🎯 Para Artigos e Dissertações

Use as tabelas LaTeX geradas:
```latex
\input{results/tabela_ranking_large.tex}
\input{results/tabela_ranking_standard.tex}
```

Ou inclua os gráficos:
```latex
\includegraphics[width=0.9\textwidth]{results/comparativo_speedup_datasets.png}
```

## 📚 Mais Informações

Veja [analysis_scripts/README.md](analysis_scripts/README.md) para detalhes sobre cada script.
