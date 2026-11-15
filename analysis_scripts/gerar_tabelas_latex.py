#!/usr/bin/env python3
"""
Geração de Tabelas LaTeX por Dataset
Cria tabelas rankeadas com speedup e eficiência para cada dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

# Configuração
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_PATH = BASE_DIR / 'results/raw_times.csv'
OUTPUT_DIR = BASE_DIR / 'results'

print("📊 Geração de Tabelas LaTeX por Dataset")
print("=" * 70)

# Carregar dados
if not RAW_DATA_PATH.exists():
    print(f"❌ Erro: Arquivo {RAW_DATA_PATH} não encontrado.")
    exit(1)

df = pd.read_csv(RAW_DATA_PATH)
df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
df = df.dropna(subset=['Time'])

print(f"✓ Dados carregados: {len(df)} registros")

# Agrupar por Model, Dataset, Kernel, Threads e calcular média das repetições
df_avg = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads'])['Time'].mean().reset_index()
df_avg.rename(columns={'Time': 'Time_avg'}, inplace=True)

# Obter baseline (sequential)
baseline = df_avg[df_avg['Model'] == 'sequential'].copy()
baseline = baseline.groupby(['Dataset', 'Kernel'])['Time_avg'].mean().reset_index()
baseline.rename(columns={'Time_avg': 'T_seq'}, inplace=True)

# Modelos paralelos
parallel_models = df_avg[df_avg['Model'] != 'sequential'].copy()

# Mesclar para calcular speedup
merged = pd.merge(parallel_models, baseline, on=['Dataset', 'Kernel'])
merged['Speedup'] = merged['T_seq'] / merged['Time_avg']
merged['Efficiency'] = merged['Speedup'] / merged['Threads']

print(f"✓ Speedup e Efficiency calculados")

# Processar cada dataset
datasets = sorted(df['Dataset'].unique())

for dataset in datasets:
    print(f"\n{'='*70}")
    print(f"📋 Dataset: {dataset.upper()}")
    print(f"{'='*70}")
    
    # Filtrar dados para o dataset
    data_dataset = merged[merged['Dataset'] == dataset].copy()
    
    # Usar o maior número de threads para o ranking
    max_threads = data_dataset['Threads'].max()
    data_ranking = data_dataset[data_dataset['Threads'] == max_threads].copy()
    
    # Agrupar por modelo e kernel
    ranking_data = []
    for model in sorted(data_ranking['Model'].unique()):
        model_data = data_ranking[data_ranking['Model'] == model]
        
        avg_speedup = model_data['Speedup'].mean()
        avg_efficiency = model_data['Efficiency'].mean()
        min_time = model_data['Time_avg'].min()
        max_time = model_data['Time_avg'].max()
        avg_time = model_data['Time_avg'].mean()
        
        ranking_data.append({
            'Model': model,
            'Avg Time (s)': avg_time,
            'Min Time (s)': min_time,
            'Max Time (s)': max_time,
            'Avg Speedup': avg_speedup,
            'Avg Efficiency': avg_efficiency
        })
    
    df_ranking = pd.DataFrame(ranking_data)
    # Ordenar por speedup decrescente
    df_ranking = df_ranking.sort_values('Avg Speedup', ascending=False).reset_index(drop=True)
    df_ranking['Rank'] = range(1, len(df_ranking) + 1)
    
    # Reordenar colunas
    df_ranking = df_ranking[['Rank', 'Model', 'Avg Time (s)', 'Avg Speedup', 'Avg Efficiency']]
    
    print(f"\n✓ Máximo de threads: {max_threads}")
    print(f"\n{df_ranking.to_string(index=False)}\n")
    
    # ========================================================================
    # Gerar Tabela LaTeX - Formato 1: Ranking Geral
    # ========================================================================
    latex_content = f"""% Tabela LaTeX - Dataset {dataset.upper()}
% Ranking de Modelos com Speedup e Eficiência
% Threads: {max_threads}

\\begin{{table}}[H]
\\centering
\\caption{{Ranking de Desempenho - Dataset \\textbf{{{dataset.upper()}}} (Threads={max_threads})}}
\\label{{tab:ranking_{dataset}}}
\\begin{{tabular}}{{|r|l|c|c|c|}}
\\hline
\\textbf{{Rank}} & \\textbf{{Modelo}} & \\textbf{{Tempo Médio (s)}} & \\textbf{{Speedup}} & \\textbf{{Eficiência}} \\\\
\\hline
"""
    
    for _, row in df_ranking.iterrows():
        m_tex = str(row['Model']).replace('_', '\\_')
        latex_content += f"{int(row['Rank'])} & {m_tex} & {row['Avg Time (s)']:.4f} & {row['Avg Speedup']:.2f}x & {row['Avg Efficiency']:.2f} \\\\\n"
    
    latex_content += """\\hline
\\end{tabular}
\\end{table}

"""
    
    # ========================================================================
    # Tabela com detalhamento por kernel
    # ========================================================================
    latex_content += f"""% Tabela detalhada por Kernel
\\begin{{table}}[H]
\\centering
\\caption{{Desempenho Detalhado por Kernel - Dataset \\textbf{{{dataset.upper()}}}}}
\\label{{tab:detail_{dataset}}}
\\begin{{tabular}}{{|l|l|c|c|c|}}
\\hline
\\textbf{{Kernel}} & \\textbf{{Modelo}} & \\textbf{{Tempo (s)}} & \\textbf{{Speedup}} & \\textbf{{Eficiência}} \\\\
\\hline
"""
    
    # Agrupar por kernel e modelo
    kernel_detail = data_ranking.copy()
    kernels = sorted(kernel_detail['Kernel'].unique())
    
    for kernel in kernels:
        kernel_data = kernel_detail[kernel_detail['Kernel'] == kernel].sort_values('Speedup', ascending=False)
        
        for i, (_, row) in enumerate(kernel_data.iterrows()):
            if i == 0:
                kernel_str = kernel
            else:
                kernel_str = ""
            
            m_tex = str(row['Model']).replace('_', '\\_')
            latex_content += f"{kernel_str} & {m_tex} & {row['Time_avg']:.4f} & {row['Speedup']:.2f}x & {row['Efficiency']:.2f} \\\\\n"
        
        latex_content += "\\hline\n"
    
    latex_content += """\\end{tabular}
\\end{table}

"""
    
    # ========================================================================
    # Tabela de Escalabilidade
    # ========================================================================
    latex_content += f"""% Tabela de Escalabilidade
\\begin{{table}}[H]
\\centering
\\caption{{Escalabilidade por Número de Threads - Dataset \\textbf{{{dataset.upper()}}}}}
\\label{{tab:scaling_{dataset}}}
\\begin{{tabular}}{{|l|c|c|c|c|}}
\\hline
\\textbf{{Modelo}} & """
    
    threads_list = sorted(data_dataset['Threads'].unique())
    for t in threads_list:
        latex_content += f"\\textbf{{{t}T}} & "
    latex_content = latex_content.rstrip("& ") + " \\\\\n\\hline\n"
    
    for model in sorted(data_dataset['Model'].unique()):
        model_data = data_dataset[data_dataset['Model'] == model]
        latex_content += f"{str(model).replace('_', '\\_')}"
        
        for t in threads_list:
            thread_data = model_data[model_data['Threads'] == t]
            if not thread_data.empty:
                speedup = thread_data['Speedup'].mean()
                latex_content += f" & {speedup:.2f}x"
            else:
                latex_content += " & --"
        
        latex_content += " \\\\\n"
    
    latex_content += """\\hline
\\end{tabular}
\\end{table}

"""
    
    # Salvar arquivo LaTeX
    output_file = OUTPUT_DIR / f"tabela_ranking_{dataset}.tex"
    with open(output_file, 'w') as f:
        f.write(latex_content)
    
    print(f"✓ Tabela LaTeX salva: {output_file.name}")

# ============================================================================
# Gerar tabela comparativa global
# ============================================================================
print(f"\n{'='*70}")
print("📋 Tabela Comparativa Global (Todos os Datasets)")
print(f"{'='*70}\n")

global_ranking = []
for dataset in datasets:
    data_dataset = merged[merged['Dataset'] == dataset].copy()
    max_threads = data_dataset['Threads'].max()
    data_ranking = data_dataset[data_dataset['Threads'] == max_threads].copy()
    
    for model in sorted(data_ranking['Model'].unique()):
        model_data = data_ranking[data_ranking['Model'] == model]
        avg_speedup = model_data['Speedup'].mean()
        avg_efficiency = model_data['Efficiency'].mean()
        avg_time = model_data['Time_avg'].mean()
        
        global_ranking.append({
            'Dataset': dataset,
            'Model': model,
            'Avg Time (s)': avg_time,
            'Avg Speedup': avg_speedup,
            'Avg Efficiency': avg_efficiency
        })

df_global = pd.DataFrame(global_ranking)

latex_global = """% Tabela Comparativa Global
\\begin{table}[H]
\\centering
\\caption{Comparação Global de Desempenho por Dataset}
\\label{tab:global_comparison}
\\begin{tabular}{|c|l|c|c|c|}
\\hline
\\textbf{Dataset} & \\textbf{Modelo} & \\textbf{Tempo Médio (s)} & \\textbf{Speedup} & \\textbf{Eficiência} \\\\
\\hline
"""

for dataset in datasets:
    dataset_data = df_global[df_global['Dataset'] == dataset].sort_values('Avg Speedup', ascending=False)
    
    for i, (_, row) in enumerate(dataset_data.iterrows()):
        if i == 0:
            dataset_str = dataset
        else:
            dataset_str = ""
        
        m_tex = str(row['Model']).replace('_', '\\_')
        latex_global += f"{dataset_str} & {m_tex} & {row['Avg Time (s)']:.4f} & {row['Avg Speedup']:.2f}x & {row['Avg Efficiency']:.2f} \\\\\n"
    
    latex_global += "\\hline\n"

latex_global += """\\end{tabular}
\\end{table}
"""

# Salvar tabela global
output_global = OUTPUT_DIR / "tabela_comparativa_global.tex"
with open(output_global, 'w') as f:
    f.write(latex_global)

print(f"✓ Tabela Global LaTeX salva: {output_global.name}\n")

# ============================================================================
# Resumo final
# ============================================================================
print("=" * 70)
print("✅ ARQUIVOS GERADOS:")
print("=" * 70)

for dataset in datasets:
    print(f"  • tabela_ranking_{dataset}.tex")

print(f"  • tabela_comparativa_global.tex")

print("\n📁 Localização: " + str(OUTPUT_DIR))
print("=" * 70)
