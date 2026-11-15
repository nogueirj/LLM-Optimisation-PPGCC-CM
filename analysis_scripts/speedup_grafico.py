import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Obter caminho relativo correto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 1. Carregar os dados do raw_times.csv
df = pd.read_csv(PROJECT_ROOT / 'results' / 'raw_times.csv')

# 2. Calcular a média de tempo para cada Model, Dataset, Kernel, Threads
df_avg = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads'])['Time'].mean().reset_index()
df_avg = df_avg.rename(columns={'Kernel': 'Benchmark', 'Model': 'Modelo'})

# 3. Separar Sequencial de Otimizado para calcular Speedup
# Baseline: tempo sequencial com Threads=1
seq = df_avg[(df_avg['Modelo'] == 'sequential') & (df_avg['Threads'] == 1)].copy()
seq = seq.rename(columns={'Time': 'T_seq'})
seq = seq[['Modelo', 'Dataset', 'Benchmark', 'T_seq']]

# Dados otimizados: todos exceto sequencial
opt = df_avg[df_avg['Modelo'] != 'sequential'].copy()
opt = opt.rename(columns={'Time': 'T_opt'})

# Faz o merge para ter T_seq e T_opt na mesma linha
merged = pd.merge(opt, seq, on=['Dataset', 'Benchmark'])
merged = merged.rename(columns={'Modelo_x': 'Modelo'})
merged = merged.drop(columns=['Modelo_y'], errors='ignore')

# 4. Calcular Speedup
merged['Speedup'] = merged['T_seq'] / merged['T_opt']

# 5. Criar diretório de resultados se não existir
results_dir = PROJECT_ROOT / 'results'
results_dir.mkdir(exist_ok=True)

# 6. Gerar gráficos separados por dataset
datasets = merged['Dataset'].unique()

for dataset in sorted(datasets):
    plot_df = merged[merged['Dataset'] == dataset]
    
    plt.figure(figsize=(14, 7))
    sns.barplot(data=plot_df, x='Benchmark', y='Speedup', hue='Modelo', palette='viridis')
    
    plt.axhline(1, color='red', linestyle='--', label='Baseline (Sequencial)', linewidth=2)
    plt.title(f'Speedup por Modelo de IA vs Versão Sequencial (Dataset: {dataset.upper()})', fontsize=14)
    plt.ylabel('Speedup (Vezes mais rápido)')
    plt.xlabel('Algoritmo (Kernel)')
    plt.legend(title='Modelo de IA', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    filename = results_dir / f'comparativo_speedup_{dataset}.png'
    plt.savefig(filename, dpi=300)
    print(f"✅ Gráfico de speedup gerado: {filename}")
    plt.close()

# 7. Gráfico comparativo: ambos datasets lado a lado
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

for idx, dataset in enumerate(sorted(datasets)):
    plot_df = merged[merged['Dataset'] == dataset]
    
    ax = axes[idx]
    sns.barplot(data=plot_df, x='Benchmark', y='Speedup', hue='Modelo', 
                palette='viridis', ax=ax)
    
    ax.axhline(1, color='red', linestyle='--', label='Baseline', linewidth=2)
    ax.set_title(f'Dataset: {dataset.upper()}', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup')
    ax.set_xlabel('Algoritmo')
    ax.legend(title='Modelo', loc='upper right', fontsize=8)
    ax.grid(axis='y', linestyle=':', alpha=0.7)

plt.suptitle('Comparação de Speedup entre Datasets', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(results_dir / 'comparativo_speedup_datasets.png', dpi=300, bbox_inches='tight')
print(f"✅ Gráfico comparativo (ambos datasets): results/comparativo_speedup_datasets.png")
plt.close()

print("\n📊 Resumo de Speedup por Dataset:")
print("=" * 70)
for dataset in sorted(datasets):
    data = merged[merged['Dataset'] == dataset]
    print(f"\n{dataset.upper()}:")
    summary = data.groupby('Modelo')['Speedup'].agg(['mean', 'min', 'max'])
    print(summary.round(3))