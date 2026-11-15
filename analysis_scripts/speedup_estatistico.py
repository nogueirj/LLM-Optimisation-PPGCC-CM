import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Obter caminho relativo correto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 1. Carregar os dados brutos
df = pd.read_csv(PROJECT_ROOT / 'results' / 'raw_times.csv')

# 2. Calcular estatísticas (média, desvio padrão) por Model, Dataset, Kernel, Threads
df_stats = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads']).agg({
    'Time': ['mean', 'std', 'count']
}).reset_index()

df_stats.columns = ['Model', 'Dataset', 'Kernel', 'Threads', 'Media_Tempo', 'Desvio_Padrao', 'N_Repeticoes']
df_stats = df_stats.rename(columns={'Kernel': 'Benchmark', 'Model': 'Modelo'})

# 3. Separar Sequencial de Otimizado
# Baseline: tempo sequencial com Threads=1
seq = df_stats[(df_stats['Modelo'] == 'sequential') & (df_stats['Threads'] == 1)].copy()
seq = seq.rename(columns={'Media_Tempo': 'T_seq', 'Desvio_Padrao': 'Std_seq'})
seq = seq[['Modelo', 'Dataset', 'Benchmark', 'T_seq', 'Std_seq']]

# Dados otimizados: todos exceto sequencial
opt = df_stats[df_stats['Modelo'] != 'sequential'].copy()
opt = opt.rename(columns={'Media_Tempo': 'T_opt', 'Desvio_Padrao': 'Std_opt'})

# Faz o merge
merged = pd.merge(opt, seq, on=['Dataset', 'Benchmark'])
merged = merged.rename(columns={'Modelo_x': 'Modelo'})
merged = merged.drop(columns=['Modelo_y'], errors='ignore')

# 4. Calcular Speedup
merged['Speedup'] = merged['T_seq'] / merged['T_opt']

# Calcular incerteza no Speedup usando propagação de erros
# Speedup = T_seq / T_opt => δSpeedup = Speedup * sqrt((δT_seq/T_seq)² + (δT_opt/T_opt)²)
merged['Std_Speedup'] = merged['Speedup'] * np.sqrt(
    (merged['Std_seq'] / merged['T_seq'])**2 + 
    (merged['Std_opt'] / merged['T_opt'])**2
)

# 5. Criar diretório de resultados se não existir
results_dir = PROJECT_ROOT / 'results'
results_dir.mkdir(exist_ok=True)

# 6. Gerar gráficos separados por dataset
datasets = sorted(merged['Dataset'].unique())
sns.set_style("whitegrid")

for dataset in datasets:
    plot_df = merged[merged['Dataset'] == dataset]
    
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(
        data=plot_df, 
        x='Benchmark', 
        y='Speedup', 
        hue='Modelo',
        palette='viridis',
        errorbar=None  # Vamos adicionar erros manualmente
    )
    
    # Adicionar barras de erro manualmente
    for i, patch in enumerate(ax.patches):
        x_pos = patch.get_x() + patch.get_width() / 2
        speedup_val = patch.get_height()
        
        # Encontrar o erro correspondente
        for idx, row in plot_df.iterrows():
            if abs(row['Speedup'] - speedup_val) < 0.01:
                ax.errorbar(x_pos, speedup_val, yerr=row['Std_Speedup'], 
                           fmt='none', color='black', capsize=4, capthick=1.5, alpha=0.7)
                break
    
    plt.axhline(1, color='red', linestyle='--', label='Baseline (Sequencial)', linewidth=2)
    plt.title(f'Comparativo de Speedup: Médias de 10 Execuções (Dataset: {dataset.upper()})', fontsize=15)
    plt.ylabel('Speedup (T_seq / T_opt)', fontsize=12)
    plt.xlabel('Algoritmos do Benchmark', fontsize=12)
    plt.legend(title='Modelo de IA', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adicionar o valor do Speedup no topo de cada barra
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 9), 
                        textcoords='offset points',
                        fontsize=8)
    
    plt.tight_layout()
    filename = results_dir / f'grafico_speedup_estatistico_{dataset}.png'
    plt.savefig(filename, dpi=300)
    print(f"✅ Gráfico de speedup estatístico gerado: {filename}")
    plt.close()

# 7. Gráfico comparativo: ambos datasets lado a lado
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

for idx, dataset in enumerate(datasets):
    plot_df = merged[merged['Dataset'] == dataset]
    ax = axes[idx]
    
    sns.barplot(data=plot_df, x='Benchmark', y='Speedup', hue='Modelo',
                palette='viridis', ax=ax, errorbar=None)
    
    # Adicionar erros
    for i, patch in enumerate(ax.patches):
        x_pos = patch.get_x() + patch.get_width() / 2
        speedup_val = patch.get_height()
        for jdx, row in plot_df.iterrows():
            if abs(row['Speedup'] - speedup_val) < 0.01:
                ax.errorbar(x_pos, speedup_val, yerr=row['Std_Speedup'],
                           fmt='none', color='black', capsize=3, capthick=1, alpha=0.6)
                break
    
    ax.axhline(1, color='red', linestyle='--', label='Baseline', linewidth=2)
    ax.set_title(f'Dataset: {dataset.upper()}', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup')
    ax.set_xlabel('Algoritmo')
    ax.legend(title='Modelo', loc='upper right', fontsize=8)
    ax.grid(axis='y', linestyle=':', alpha=0.7)

plt.suptitle('Comparação de Speedup (com desvio padrão) entre Datasets', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(results_dir / 'grafico_speedup_estatistico_datasets.png', dpi=300, bbox_inches='tight')
print(f"✅ Gráfico comparativo (ambos datasets): results/grafico_speedup_estatistico_datasets.png")
plt.close()

print("\n📊 Resumo Estatístico de Speedup por Dataset:")
print("=" * 70)
for dataset in datasets:
    data = merged[merged['Dataset'] == dataset]
    print(f"\n{dataset.upper()}:")
    summary = data.groupby('Modelo').agg({
        'Speedup': ['mean', 'std', 'min', 'max']
    }).round(3)
    summary.columns = ['Média', 'Desvio Padrão', 'Mínimo', 'Máximo']
    print(summary)