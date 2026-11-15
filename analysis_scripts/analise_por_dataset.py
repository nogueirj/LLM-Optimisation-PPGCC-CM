#!/usr/bin/env python3
"""
Análise consolidada de Speedup e Eficiência por Dataset
Compara performance dos modelos entre datasets small, standard e large
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Obter caminho relativo correto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Carregar dados
df = pd.read_csv(PROJECT_ROOT / 'results' / 'raw_times.csv')

# Calcular estatísticas
df_stats = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads']).agg({
    'Time': ['mean', 'std', 'count']
}).reset_index()

df_stats.columns = ['Model', 'Dataset', 'Kernel', 'Threads', 'Media_Tempo', 'Desvio_Padrao', 'N_Repeticoes']

# Separar sequencial e otimizado
seq = df_stats[(df_stats['Model'] == 'sequential') & (df_stats['Threads'] == 1)].copy()
seq = seq.rename(columns={'Media_Tempo': 'T_seq', 'Desvio_Padrao': 'Std_seq'})
seq = seq[['Dataset', 'Kernel', 'T_seq', 'Std_seq']]

opt = df_stats[df_stats['Model'] != 'sequential'].copy()
opt = opt.rename(columns={'Media_Tempo': 'T_opt', 'Desvio_Padrao': 'Std_opt', 'Model': 'Modelo'})

# Merge
merged = pd.merge(opt, seq, on=['Dataset', 'Kernel'])

# Calcular speedup
merged['Speedup'] = merged['T_seq'] / merged['T_opt']
merged['Eficiencia'] = merged['Speedup'] / merged['Threads']

# Criar diretório
results_dir = PROJECT_ROOT / 'results'
results_dir.mkdir(exist_ok=True)

# Análise por Dataset
print("\n" + "="*80)
print("📊 ANÁLISE CONSOLIDADA: SPEEDUP POR DATASET")
print("="*80)

datasets = sorted(merged['Dataset'].unique())
models = sorted(merged['Modelo'].unique())

# Tabela 1: Speedup médio por modelo e dataset
print("\n📈 SPEEDUP MÉDIO (T_seq / T_opt):")
print("-" * 80)
speedup_pivot = merged.pivot_table(values='Speedup', index='Modelo', columns='Dataset', aggfunc='mean')
print(speedup_pivot.round(2))

# Tabela 2: Eficiência média por modelo e dataset
print("\n⚡ EFICIÊNCIA MÉDIA (Speedup / Threads):")
print("-" * 80)
eficiencia_pivot = merged.pivot_table(values='Eficiencia', index='Modelo', columns='Dataset', aggfunc='mean')
print(eficiencia_pivot.round(3))

# Tabela 3: Melhor performance por dataset
print("\n🏆 MODELO COM MELHOR SPEEDUP MÉDIO POR DATASET:")
print("-" * 80)
for dataset in datasets:
    data = merged[merged['Dataset'] == dataset]
    best_model = data.groupby('Modelo')['Speedup'].mean().idxmax()
    best_speedup = data.groupby('Modelo')['Speedup'].mean().max()
    print(f"  {dataset.upper():12} → {best_model:15} (Speedup: {best_speedup:.2f}x)")

# Tabela 4: Desvio padrão (variabilidade)
print("\n📉 DESVIO PADRÃO DE SPEEDUP (variabilidade):")
print("-" * 80)
std_speedup = merged.groupby(['Modelo', 'Dataset'])['Speedup'].std().reset_index()
std_pivot = std_speedup.pivot_table(values='Speedup', index='Modelo', columns='Dataset')
print(std_pivot.round(2))

# Salvar tabelas em CSV
speedup_pivot.to_csv(results_dir / 'speedup_por_dataset.csv')
eficiencia_pivot.to_csv(results_dir / 'eficiencia_por_dataset.csv')

print("\n✅ Tabelas salvas em results/speedup_por_dataset.csv e results/eficiencia_por_dataset.csv")

# Análise por Kernel
print("\n" + "="*80)
print("📊 ANÁLISE POR KERNEL (algoritmo)")
print("="*80)

for dataset in datasets:
    data = merged[merged['Dataset'] == dataset]
    print(f"\n{dataset.upper()}:")
    print("-" * 80)
    kernel_analysis = data.groupby('Kernel').agg({
        'Speedup': ['mean', 'min', 'max', 'std']
    }).round(2)
    kernel_analysis.columns = ['Média', 'Mínimo', 'Máximo', 'Desvio Padrão']
    print(kernel_analysis)

print("\n" + "="*80)
