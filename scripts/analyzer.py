import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
RAW_DATA_PATH = f"{BASE_DIR}/results/raw_times.csv"

def analyze():
    df = pd.read_csv(RAW_DATA_PATH)
    df['Time'] = pd.to_numeric(df['Time'])
    
    # Média das repetições
    df_avg = df.groupby(['Model', 'Dataset', 'Kernel', 'Threads'])['Time'].mean().reset_index()
    
    # Baseline: Tempo do modelo 'sequential' (que sempre deve ser Threads=1 para comparação)
    seq_df = df_avg[df_avg['Model'] == 'sequential'].set_index(['Dataset', 'Kernel'])['Time']
    
    def get_speedup(row):
        t_seq = seq_df.loc[(row['Dataset'], row['Kernel'])]
        return t_seq / row['Time']

    df_avg['Speedup'] = df_avg.apply(get_speedup, axis=1)
    
    # Gerar Gráfico de Escalabilidade (Strong Scaling)
    sns.set_theme(style="whitegrid")
    
    # Filtrar apenas o dataset LARGE para o gráfico ficar mais limpo
    plot_df = df_avg[(df_avg['Model'] != 'sequential') & (df_avg['Dataset'] == 'large')]
    
    plt.figure(figsize=(12, 8))
    g = sns.lineplot(data=plot_df, x="Threads", y="Speedup", hue="Model", style="Kernel", markers=True, dashes=False)
    
    # Adicionar linha de Speedup Ideal (Diagonal)
    max_threads = df_avg['Threads'].max()
    plt.plot([1, max_threads], [1, max_threads], 'r--', label="Ideal Scaling")
    
    plt.title("Curva de Escalabilidade (Strong Scaling) - Dataset LARGE")
    plt.xlabel("Número de Threads")
    plt.ylabel("Speedup ($T_{seq} / T_{par}$)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.savefig(f"{BASE_DIR}/results/scaling_curve.png", dpi=300, bbox_inches='tight')
    print("📈 Curva de escalabilidade gerada em results/scaling_curve.png")

if __name__ == "__main__":
    analyze()