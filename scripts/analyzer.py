import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =================================================================
# CONFIGURAÇÕES
# =================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
RAW_DATA_PATH = os.path.join(BASE_DIR, "results/raw_times.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "results/final_metrics.csv")
OUTPUT_PLOT = os.path.join(BASE_DIR, "results/scaling_curve.png")
OUTPUT_LATEX = os.path.join(BASE_DIR, "results/table_results.tex")

def generate_analysis():
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Erro: Arquivo {RAW_DATA_PATH} não encontrado.")
        return

    print("📈 Lendo dados e calculando métricas...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Converter tempo para numérico (limpeza de possíveis erros de string)
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df = df.dropna(subset=['Time'])

    # 1. Calcular a média das repetições (Collapsing Repetitions)
    df_avg = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads'])['Time'].mean().reset_index()

    # 2. Isolar o Baseline (Sequential)
    # Como o sequential foi rodado várias vezes (1, 2, 4... threads), 
    # tiramos a média de todos os 'sequentials' do mesmo kernel para um baseline ultra-estável.
    baseline = df_avg[df_avg['Model'] == 'sequential'].copy()
    baseline = baseline.groupby(['Dataset', 'Kernel'])['Time'].mean().reset_index()
    baseline.rename(columns={'Time': 'T_Sequential'}, inplace=True)

    # 3. Criar o DataFrame de Modelos Paralelos
    # Removemos o sequential da lista de comparação direta
    par_df = df_avg[df_avg['Model'] != 'sequential'].copy()

    # 4. Mesclar (Join) para calcular Speedup
    # Isso garante que cada linha paralela tenha seu respectivo tempo sequencial ao lado
    merged = pd.merge(par_df, baseline, on=['Dataset', 'Kernel'])
    
    merged['Speedup'] = merged['T_Sequential'] / merged['Time']
    merged['Efficiency'] = merged['Speedup'] / merged['Threads']

    # Salvar CSV de métricas
    merged.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Métricas salvas em: {OUTPUT_CSV}")

    # 5. Geração do Gráfico de Escalabilidade (Strong Scaling)
    print("🎨 Gerando gráficos...")
    sns.set_theme(style="whitegrid")
    
    # Filtramos para um dataset específico se houver vários, ou criamos facetas
    plt.figure(figsize=(12, 7))
    plot = sns.lineplot(
        data=merged, 
        x="Threads", y="Speedup", hue="Model", style="Kernel",
        markers=True, dashes=False, linewidth=2
    )
    
    # Adicionar linha de Speedup Ideal (Diagonal)
    max_t = merged['Threads'].max()
    plt.plot([1, max_t], [1, max_t], color='red', linestyle='--', label='Speedup Ideal', alpha=0.7)
    
    plt.title("Curva de Escalabilidade (Strong Scaling)")
    plt.xlabel("Número de Threads")
    plt.ylabel("Speedup ($T_{seq} / T_{par}$)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.savefig(OUTPUT_PLOT, dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Tabela LaTeX (Resumo no maior número de Threads)
    # Pegamos o máximo de threads para mostrar o "melhor caso" na tabela
    max_threads = merged['Threads'].max()
    final_table = merged[merged['Threads'] == max_threads].pivot_table(
        index='Kernel', 
        columns='Model', 
        values='Speedup'
    ).round(2)

    with open(OUTPUT_LATEX, "w") as f:
        f.write("% Tabela de Speedup no máximo de Threads (" + str(max_threads) + ")\n")
        f.write(final_table.to_latex())
    
    print(f"✅ Tabela LaTeX (Threads={max_threads}) gerada em: {OUTPUT_LATEX}")

if __name__ == "__main__":
    generate_analysis()