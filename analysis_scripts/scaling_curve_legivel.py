#!/usr/bin/env python3
"""
Gráficos de Escalabilidade (Strong Scaling) - Versões Legíveis
Cria múltiplas visualizações limpas e fáceis de interpretar
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Obter caminho relativo correto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Carregar dados
df = pd.read_csv(PROJECT_ROOT / 'results' / 'raw_times.csv')

# Calcular estatísticas
df_avg = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads'])['Time'].mean().reset_index()

# Baseline (sequential)
baseline = df_avg[df_avg['Model'] == 'sequential'].copy()
baseline = baseline.groupby(['Dataset', 'Kernel'])['Time'].mean().reset_index()
baseline.rename(columns={'Time': 'T_seq'}, inplace=True)

# Merge para calcular speedup
par_df = df_avg[df_avg['Model'] != 'sequential'].copy()
merged = pd.merge(par_df, baseline, on=['Dataset', 'Kernel'])
merged['Speedup'] = merged['T_seq'] / merged['Time']
merged['Efficiency'] = merged['Speedup'] / merged['Threads']

results_dir = PROJECT_ROOT / 'results'
results_dir.mkdir(exist_ok=True)

sns.set_style("whitegrid")
sns.set_palette("husl")

# =====================================================================
# OPÇÃO 1: Escalabilidade por Dataset (Modelo Médio)
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, dataset in enumerate(sorted(merged['Dataset'].unique())):
    data = merged[merged['Dataset'] == dataset]
    
    # Calcular speedup médio por threads (média de todos os modelos e kernels)
    speedup_by_threads = data.groupby('Threads')['Speedup'].mean()
    
    ax = axes[idx]
    
    # Plot de linha com preenchimento
    ax.plot(speedup_by_threads.index, speedup_by_threads.values, 
            marker='o', linewidth=3, markersize=10, label='Speedup Médio', color='#2E86AB')
    
    # Linha de escalabilidade ideal
    max_t = speedup_by_threads.index.max()
    ax.plot([1, max_t], [1, max_t], 'r--', linewidth=2, label='Escalabilidade Ideal', alpha=0.7)
    
    # Preenchimento entre real e ideal
    ax.fill_between(speedup_by_threads.index, speedup_by_threads.values, 
                    speedup_by_threads.index, alpha=0.2, color='#2E86AB')
    
    ax.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup', fontsize=12, fontweight='bold')
    ax.set_title(f'Escalabilidade - Dataset {dataset.upper()}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig(results_dir / 'scaling_curve_by_dataset.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 1 gerado: scaling_curve_by_dataset.png")
plt.close()

# =====================================================================
# OPÇÃO 2: Escalabilidade por Kernel (Facet Plot)
# =====================================================================
kernels = sorted(merged['Kernel'].unique())
n_kernels = len(kernels)
n_cols = 3
n_rows = (n_kernels + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 12))
axes = axes.flatten()

for idx, kernel in enumerate(kernels):
    data_kernel = merged[merged['Kernel'] == kernel]
    
    ax = axes[idx]
    
    # Plot por dataset
    for dataset in sorted(data_kernel['Dataset'].unique()):
        data_subset = data_kernel[data_kernel['Dataset'] == dataset]
        speedup_by_threads = data_subset.groupby('Threads')['Speedup'].mean()
        
        ax.plot(speedup_by_threads.index, speedup_by_threads.values,
                marker='o', linewidth=2.5, markersize=8, label=f'{dataset.upper()}')
    
    # Linha ideal
    max_t = data_kernel['Threads'].max()
    ax.plot([1, max_t], [1, max_t], 'r--', linewidth=2, alpha=0.5)
    
    ax.set_xlabel('Threads', fontsize=10)
    ax.set_ylabel('Speedup', fontsize=10)
    ax.set_title(f'Kernel: {kernel.upper()}', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

# Remover subplots vazios
for idx in range(len(kernels), len(axes)):
    fig.delaxes(axes[idx])

plt.suptitle('Escalabilidade por Kernel (Strong Scaling)', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(results_dir / 'scaling_curve_by_kernel.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 2 gerado: scaling_curve_by_kernel.png")
plt.close()

# =====================================================================
# OPÇÃO 3: Top 3 Melhores Modelos - Escalabilidade por Dataset
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, dataset in enumerate(sorted(merged['Dataset'].unique())):
    data = merged[merged['Dataset'] == dataset]
    
    # Encontrar top 3 modelos
    top_models = data.groupby('Model')['Speedup'].mean().nlargest(5).index.tolist()
    
    ax = axes[idx]
    
    for model in top_models:
        data_model = data[data['Model'] == model]
        speedup_by_threads = data_model.groupby('Threads')['Speedup'].mean()
        
        ax.plot(speedup_by_threads.index, speedup_by_threads.values,
                marker='o', linewidth=3, markersize=10, label=model.upper())
    
    # Linha ideal
    max_t = data['Threads'].max()
    ax.plot([1, max_t], [1, max_t], 'r--', linewidth=2, label='Ideal', alpha=0.7)
    
    ax.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup', fontsize=12, fontweight='bold')
    ax.set_title(f'Top 3 Modelos - Dataset {dataset.upper()}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig(results_dir / 'scaling_curve_top3_models.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 3 gerado: scaling_curve_top3_models.png")
plt.close()

# =====================================================================
# OPÇÃO 4: Eficiência vs Threads (por Dataset)
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, dataset in enumerate(sorted(merged['Dataset'].unique())):
    data = merged[merged['Dataset'] == dataset]
    
    # Calcular eficiência média
    efficiency_by_threads = data.groupby('Threads')['Efficiency'].mean() * 100
    
    ax = axes[idx]
    
    # Plot com preenchimento
    ax.fill_between(efficiency_by_threads.index, efficiency_by_threads.values, 
                    alpha=0.3, color='#A23B72')
    ax.plot(efficiency_by_threads.index, efficiency_by_threads.values,
            marker='s', linewidth=3, markersize=10, color='#A23B72', label='Eficiência Média')
    
    # Linha de eficiência 100%
    ax.axhline(y=100, color='g', linestyle='--', linewidth=2, label='Eficiência 100%', alpha=0.7)
    
    ax.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
    ax.set_ylabel('Eficiência (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Eficiência - Dataset {dataset.upper()}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig(results_dir / 'scaling_curve_efficiency.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 4 gerado: scaling_curve_efficiency.png")
plt.close()

# =====================================================================
# OPÇÃO 5: Comportamento Comparativo - Standard Dataset
# ChatGPT/Gemini (Linear) vs CodeLlama (Saturação Precoce)
# =====================================================================
data_standard = merged[merged['Dataset'] == 'standard'].copy()

fig, ax = plt.subplots(figsize=(14, 8))

# Modelos de interesse com cores distintas
model_colors = {
    'chatgpt': '#2E86AB',      # Azul - escalabilidade linear
    'gemini': '#06A77D',       # Verde - escalabilidade linear
    'codellama': '#D62828',    # Vermelho - saturação precoce
}

for model in ['chatgpt', 'gemini', 'codellama']:
    data_model = data_standard[data_standard['Model'] == model]
    speedup_by_threads = data_model.groupby('Threads')['Speedup'].mean()
    
    # Determinar estilo de linha baseado no comportamento
    linestyle = '-' if model in ['chatgpt', 'gemini'] else '--'
    linewidth = 3.5 if model in ['chatgpt', 'gemini'] else 3
    
    ax.plot(speedup_by_threads.index, speedup_by_threads.values,
            marker='o', linewidth=linewidth, markersize=12, 
            label=f'{model.upper()} ({"Linear até 32T" if model != "codellama" else "Saturação Precoce"})',
            color=model_colors.get(model, '#2E86AB'),
            linestyle=linestyle)

# Linha de escalabilidade ideal
max_t = data_standard['Threads'].max()
ax.plot([1, max_t], [1, max_t], 'k--', linewidth=2.5, label='Escalabilidade Ideal', 
        alpha=0.6, zorder=0)

# Marcador visual em 32 threads
ax.axvline(x=32, color='gray', linestyle=':', linewidth=2, alpha=0.5, label='32 Threads')
ax.text(32, ax.get_ylim()[1]*0.95, '32T', ha='center', fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.set_xlabel('Número de Threads', fontsize=14, fontweight='bold')
ax.set_ylabel('Speedup', fontsize=14, fontweight='bold')
ax.set_title('Comportamento de Escalabilidade - Dataset Standard\n' + 
             'Contraste: ChatGPT/Gemini (Linear) vs CodeLlama (Saturação)',
             fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12, loc='upper left', framealpha=0.95)
ax.set_xlim(left=0, right=max_t*1.05)
ax.set_ylim(bottom=0)

# Anotações
ax.text(0.98, 0.05, 'ChatGPT e Gemini: Escalabilidade quase linear até 32 threads\n' +
        'CodeLlama: Satura rapidamente, indicando overhead de paralelização',
        transform=ax.transAxes, fontsize=11, verticalalignment='bottom',
        horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='lightyellow', 
        alpha=0.8, pad=0.8))

plt.tight_layout()
plt.savefig(results_dir / 'scaling_curve_standard_behavior_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 5 gerado: scaling_curve_standard_behavior_comparison.png")
plt.close()

print("\n" + "="*70)
print("✅ TODOS OS GRÁFICOS DE ESCALABILIDADE GERADOS COM SUCESSO!")
print("="*70)
print("\n📊 Gráficos disponíveis em results/:")
print("  1. scaling_curve_by_dataset.png              - Escalabilidade média por dataset")
print("  2. scaling_curve_by_kernel.png               - Escalabilidade por kernel (facet)")
print("  3. scaling_curve_top3_models.png             - Top 3 melhores modelos")
print("  4. scaling_curve_efficiency.png              - Eficiência vs threads")
print("  5. scaling_curve_standard_behavior_comparison.png - ChatGPT/Gemini vs CodeLlama")
print("\n💡 Dica: Use estes gráficos para relatórios e artigos!")
print("="*70)
