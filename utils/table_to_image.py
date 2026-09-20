import pandas as pd
import matplotlib.pyplot as plt

def gerar_imagem_tabela_ranking():
    # 1. Dados Exatos da sua Tabela LaTeX
    dados = {
        "Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Modelo": [
            "chatgpt", 
            "gemini", 
            "openmp", # Baseline Manual
            "codestral", 
            "qwen", 
            "granite", 
            "deepseekcoder", 
            "PoLLy", 
            "codellama"
        ],
        "Tempo Médio (s)": [
            "0.0811", "0.0885", "0.0919", "0.0960", 
            "0.1005", "0.1037", "0.3365", "0.1650", "1.3574"
        ],
        "Speedup": [
            "38.77x", "35.56x", "31.98x", "30.06x", 
            "28.96x", "27.66x", "23.32x", "18.24x", "11.05x"
        ],
        "Eficiência": [
            "0.61", "0.56", "0.50", "0.47", 
            "0.45", "0.43", "0.36", "0.28", "0.17"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura
    # Largura x Altura (Ajustado para o conteúdo)
    fig, ax = plt.subplots(figsize=(10, 5)) 
    ax.axis('off')

    # 3. Desenhar a Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização Profissional
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)
    
    # Cores e Bordas
    cor_cabecalho = '#40466e' # Azul Escuro (Estilo Acadêmico)
    cor_linha_par = '#f1f1f2' # Cinza muito claro
    cor_linha_impar = '#ffffff' # Branco

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_height(0.09) # Altura da linha
        
        if row == 0: # Cabeçalho
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            # Cores alternadas (Zebra striping)
            cor_fundo = cor_linha_par if row % 2 == 0 else cor_linha_impar
            
            # Se quiser destacar o 'openmp' (Baseline) descomente as linhas abaixo:
            # if df.iloc[row-1]["Modelo"] == "openmp":
            #     cell.set_text_props(weight='bold', color='#c0392b') # Vermelho
            
            cell.set_facecolor(cor_fundo)

    # 5. Título
    plt.title("Ranking de Desempenho - Dataset STANDARD (Threads=64)", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo_saida = "Tabela_Ranking_Standard_Final.png"
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Tabela gerada com sucesso: {arquivo_saida}")


def gerar_tabela_detalhada():
    # 1. Dados extraídos fielmente do LaTeX fornecido
    # Usei strings vazias "" na coluna Kernel para replicar o agrupamento visual
    dados = {
        "Kernel": [
            "2mm", "", "", "", "", "", "", "", "",
            "3mm", "", "", "", "", "", "", "", "",
            "atax", "", "", "", "", "", "", "", "",
            "gemm", "", "", "", "", "", "", "",
            "syr2k", "", "", "", "", "", "", "", ""
        ],
        "Modelo": [
            # 2mm
            "chatgpt", "gemini", "codestral", "granite", "openmp", "deepseekcoder", "qwen", "PoLLy", "codellama",
            # 3mm
            "chatgpt", "qwen", "codellama", "deepseekcoder", "gemini", "openmp", "codestral", "granite", "PoLLy",
            # atax
            "gemini", "granite", "openmp", "PoLLy", "deepseekcoder", "chatgpt", "codestral", "codellama", "qwen",
            # gemm
            "chatgpt", "codestral", "qwen", "gemini", "openmp", "deepseekcoder", "PoLLy", "codellama",
            # syr2k
            "chatgpt", "gemini", "openmp", "granite", "PoLLy", "qwen", "codestral", "codellama", "deepseekcoder"
        ],
        "Tempo (s)": [
            # 2mm
            "0.1192", "0.1309", "0.1323", "0.1334", "0.1334", "0.1431", "0.1560", "0.2625", "5.7132",
            # 3mm
            "0.1982", "0.2121", "0.2122", "0.2150", "0.2150", "0.2152", "0.2166", "0.2309", "0.3354",
            # atax
            "0.0023", "0.0043", "0.0043", "0.0044", "0.0053", "0.0081", "0.0087", "0.0133", "0.0147",
            # gemm
            "0.0547", "0.0642", "0.0642", "0.0666", "0.0669", "0.0874", "0.1708", "0.2718",
            # syr2k
            "0.0254", "0.0275", "0.0398", "0.0462", "0.0521", "0.0556", "0.0582", "0.5767", "1.2319"
        ],
        "Speedup": [
            # 2mm
            "48.42x", "44.06x", "43.61x", "43.26x", "43.25x", "40.33x", "36.99x", "21.98x", "1.01x",
            # 3mm
            "43.42x", "40.58x", "40.56x", "40.04x", "40.03x", "39.99x", "39.75x", "37.27x", "25.66x",
            # atax
            "6.48x", "3.49x", "3.43x", "3.35x", "2.81x", "1.84x", "1.71x", "1.12x", "1.01x",
            # gemm
            "51.81x", "44.12x", "44.11x", "42.57x", "42.34x", "32.43x", "16.59x", "10.43x",
            # syr2k
            "48.38x", "44.66x", "30.90x", "26.64x", "23.60x", "22.13x", "21.14x", "2.13x", "1.00x"
        ],
        "Eficiência": [
            # 2mm
            "0.76", "0.69", "0.68", "0.68", "0.68", "0.63", "0.58", "0.34", "0.02",
            # 3mm
            "0.68", "0.63", "0.63", "0.63", "0.63", "0.62", "0.62", "0.58", "0.40",
            # atax
            "0.10", "0.05", "0.05", "0.05", "0.04", "0.03", "0.03", "0.02", "0.02",
            # gemm
            "0.81", "0.69", "0.69", "0.67", "0.66", "0.51", "0.26", "0.16",
            # syr2k
            "0.76", "0.70", "0.48", "0.42", "0.37", "0.35", "0.33", "0.03", "0.02"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura (Alta/Longa devido à quantidade de linhas)
    fig, ax = plt.subplots(figsize=(8, 14)) 
    ax.axis('off')

    # 3. Desenhar Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10) # Fonte levemente reduzida (\small do LaTeX)

    cor_cabecalho = '#40466e'
    cor_par = '#f1f1f2'
    cor_impar = '#ffffff'

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        
        # Ajuste de altura das linhas para ficar compacto e legível
        if row == 0:
            cell.set_height(0.04)
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            cell.set_height(0.022) # Linhas de dados mais finas
            
            # Lógica de cores:
            # Vamos alternar a cor baseada no GRUPO de Kernel para facilitar leitura?
            # Ou manter zebra simples? Zebra simples é mais limpo.
            bg_color = cor_par if row % 2 == 0 else cor_impar
            cell.set_facecolor(bg_color)
            
            # Se for a coluna "Kernel" e tiver texto (início do grupo), negrito
            if col == 0 and df.iloc[row-1]["Kernel"] != "":
                cell.set_text_props(weight='bold')

    # 5. Título
    plt.title("Desempenho Detalhado por Kernel - Dataset STANDARD", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo = "Tabela_Detalhada_Standard_Final.png"
    plt.savefig(arquivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gerado: {arquivo}")

def gerar_tabela_scaling():
    # 1. Dados extraídos fielmente do LaTeX
    dados = {
        "Modelo": [
            "chatgpt", 
            "codellama", 
            "codestral", 
            "deepseekcoder", 
            "gemini", 
            "granite", 
            "openmp", # Baseline
            "PoLLy", 
            "qwen"
        ],
        "1T": [
            "1.12x", "1.26x", "0.85x", "0.89x", "1.03x", "1.00x", "1.00x", "18.64x", "0.88x"
        ],
        "2T": [
            "2.20x", "1.55x", "1.69x", "1.58x", "1.99x", "1.95x", "1.92x", "19.02x", "1.53x"
        ],
        "4T": [
            "4.29x", "2.16x", "3.44x", "2.87x", "3.97x", "3.68x", "3.77x", "19.80x", "2.94x"
        ],
        "8T": [
            "7.48x", "3.05x", "5.87x", "5.07x", "6.90x", "6.54x", "6.67x", "19.34x", "5.22x"
        ],
        "16T": [
            "14.62x", "4.64x", "11.29x", "8.92x", "12.95x", "11.41x", "12.30x", "22.19x", "10.26x"
        ],
        "32T": [
            "28.04x", "7.85x", "21.20x", "16.29x", "24.57x", "21.81x", "23.83x", "25.75x", "19.88x"
        ],
        "64T": [
            "38.77x", "11.05x", "30.06x", "23.32x", "35.56x", "27.66x", "31.98x", "18.24x", "28.96x"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura
    # Largura x Altura (Mais larga para acomodar as 8 colunas confortavelmente)
    fig, ax = plt.subplots(figsize=(12, 5)) 
    ax.axis('off')

    # 3. Desenhar a Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)

    cor_cabecalho = '#40466e' # Azul Acadêmico
    cor_par = '#f1f1f2'
    cor_impar = '#ffffff'

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_height(0.1) # Altura das linhas
        
        if row == 0: # Cabeçalho
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            # Cores alternadas
            bg_color = cor_par if row % 2 == 0 else cor_impar
            cell.set_facecolor(bg_color)
            
            # (Opcional) Destaque para o Baseline 'openmp' se desejar
            # if df.iloc[row-1]["Modelo"] == "openmp":
            #     cell.set_text_props(weight='bold')

    # 5. Título
    plt.title("Escalabilidade por Número de Threads - Dataset STANDARD", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo_saida = "Tabela_Escalabilidade_Standard.png"
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gerado com sucesso: {arquivo_saida}")


def gerar_tabela_ranking_large():
    # 1. Dados Exatos do LaTeX fornecido (Dataset LARGE)
    dados = {
        "Rank": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Modelo": [
            "openmp",       # Baseline Manual assumiu a ponta
            "qwen", 
            "gemini", 
            "chatgpt", 
            "codestral", 
            "granite", 
            "PoLLy", 
            "deepseekcoder", 
            "codellama"
        ],
        "Tempo Médio (s)": [
            "0.4078", "0.4232", "0.4317", "0.4200", 
            "0.4345", "0.4684", "0.8822", "2.5319", "4.0162"
        ],
        "Speedup": [
            "23.98x", "23.20x", "21.64x", "21.63x", 
            "20.74x", "19.92x", "18.04x", "13.62x", "7.35x"
        ],
        "Eficiência": [
            "0.37", "0.36", "0.34", "0.34", 
            "0.32", "0.31", "0.28", "0.21", "0.11"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura
    fig, ax = plt.subplots(figsize=(10, 5)) 
    ax.axis('off')

    # 3. Desenhar a Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)

    cor_cabecalho = '#40466e' 
    cor_par = '#f1f1f2'
    cor_impar = '#ffffff'

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_height(0.09) 
        
        if row == 0: # Cabeçalho
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            bg_color = cor_par if row % 2 == 0 else cor_impar
            cell.set_facecolor(bg_color)
            
            # (Opcional) Se quiser destacar o vencedor (openmp) em negrito:
            # if df.iloc[row-1]["Modelo"] == "openmp":
            #     cell.set_text_props(weight='bold')

    # 5. Título
    plt.title("Ranking de Desempenho - Dataset LARGE (Threads=64)", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo_saida = "Tabela_Ranking_Large.png"
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gerado: {arquivo_saida}")

def gerar_tabela_detalhada_large():
    # 1. Dados extraídos fielmente do LaTeX fornecido (Dataset LARGE)
    # Coluna Kernel usa "" para criar o efeito visual de agrupamento
    dados = {
        "Kernel": [
            "2mm", "", "", "", "", "", "", "", "",
            "3mm", "", "", "", "", "", "", "", "",
            "atax", "", "", "", "", "", "", "", "",
            "gemm", "", "", "", "", "", "", "",
            "syr2k", "", "", "", "", "", "", "", ""
        ],
        "Modelo": [
            # 2mm
            "chatgpt", "openmp", "deepseekcoder", "codestral", "gemini", "qwen", "granite", "PoLLy", "codellama",
            # 3mm
            "chatgpt", "codellama", "openmp", "granite", "codestral", "deepseekcoder", "gemini", "qwen", "PoLLy",
            # atax
            "gemini", "openmp", "deepseekcoder", "chatgpt", "granite", "codestral", "PoLLy", "codellama", "qwen",
            # gemm
            "chatgpt", "openmp", "gemini", "qwen", "codestral", "deepseekcoder", "codellama", "PoLLy",
            # syr2k (O destaque do Polly)
            "PoLLy", "qwen", "openmp", "chatgpt", "codestral", "gemini", "granite", "codellama", "deepseekcoder"
        ],
        "Tempo (s)": [
            # 2mm
            "0.5856", "0.5926", "0.6012", "0.6029", "0.6057", "0.6088", "0.6094", "1.4464", "14.1732",
            # 3mm
            "0.8840", "0.8985", "0.8997", "0.9024", "0.9080", "0.9080", "0.9131", "0.9156", "1.9461",
            # atax
            "0.0087", "0.0140", "0.0156", "0.0166", "0.0198", "0.0274", "0.0285", "0.0358", "0.0572",
            # gemm
            "0.2918", "0.2971", "0.3004", "0.3018", "0.3062", "0.3969", "0.7848", "0.8079",
            # syr2k
            "0.1818", "0.2327", "0.2358", "0.3221", "0.3282", "0.3306", "0.3419", "4.1886", "10.7380"
        ],
        "Speedup": [
            # 2mm
            "23.79x", "23.50x", "23.17x", "23.10x", "23.00x", "22.88x", "22.86x", "9.63x", "0.98x",
            # 3mm
            "22.82x", "22.45x", "22.42x", "22.35x", "22.21x", "22.21x", "22.09x", "22.03x", "10.36x",
            # atax
            "6.63x", "4.12x", "3.68x", "3.47x", "2.91x", "2.10x", "2.02x", "1.61x", "1.01x",
            # gemm
            "24.56x", "24.12x", "23.86x", "23.74x", "23.40x", "18.06x", "9.13x", "8.87x",
            # syr2k
            "59.32x", "46.35x", "45.74x", "33.49x", "32.86x", "32.63x", "31.54x", "2.57x", "1.00x"
        ],
        "Eficiência": [
            # 2mm
            "0.37", "0.37", "0.36", "0.36", "0.36", "0.36", "0.36", "0.15", "0.02",
            # 3mm
            "0.36", "0.35", "0.35", "0.35", "0.35", "0.35", "0.35", "0.34", "0.16",
            # atax
            "0.10", "0.06", "0.06", "0.05", "0.05", "0.03", "0.03", "0.03", "0.02",
            # gemm
            "0.38", "0.38", "0.37", "0.37", "0.37", "0.28", "0.14", "0.14",
            # syr2k
            "0.93", "0.72", "0.71", "0.52", "0.51", "0.51", "0.49", "0.04", "0.02"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura (Alta para caber todas as linhas)
    fig, ax = plt.subplots(figsize=(8, 14)) 
    ax.axis('off')

    # 3. Desenhar a Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)

    cor_cabecalho = '#40466e'
    cor_par = '#f1f1f2'
    cor_impar = '#ffffff'

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        
        if row == 0: # Cabeçalho
            cell.set_height(0.04)
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            cell.set_height(0.022) # Altura compacta
            
            # Cores alternadas
            bg_color = cor_par if row % 2 == 0 else cor_impar
            cell.set_facecolor(bg_color)
            
            # Negrito para o nome do Kernel (início do grupo)
            if col == 0 and df.iloc[row-1]["Kernel"] != "":
                cell.set_text_props(weight='bold')
            
            # (Opcional) Destaque para o Polly no syr2k
            # if df.iloc[row-1]["Kernel"] == "syr2k" and df.iloc[row-1]["Modelo"] == "PoLLy":
            #     cell.set_text_props(weight='bold', color='#c0392b')

    # 5. Título
    plt.title("Desempenho Detalhado por Kernel - Dataset LARGE", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo_saida = "Tabela_Detalhada_Large_Final.png"
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gerado com sucesso: {arquivo_saida}")

def gerar_tabela_scaling_large():
    # 1. Dados extraídos fielmente do LaTeX fornecido (Dataset LARGE)
    dados = {
        "Modelo": [
            "chatgpt", 
            "codellama", 
            "codestral", 
            "deepseekcoder", 
            "gemini", 
            "granite", 
            "openmp", # Baseline
            "PoLLy", 
            "qwen"
        ],
        "1T": [
            "1.00x", "1.47x", "0.90x", "0.91x", 
            "1.02x", "1.01x", "1.00x", "6.68x", "1.01x"
        ],
        "2T": [
            "1.85x", "1.70x", "1.69x", "1.50x", 
            "1.93x", "1.90x", "1.87x", "7.09x", "1.70x"
        ],
        "4T": [
            "3.47x", "2.21x", "3.29x", "2.66x", 
            "3.71x", "3.58x", "3.55x", "7.83x", "3.14x"
        ],
        "8T": [
            "6.07x", "2.98x", "5.68x", "4.61x", 
            "6.49x", "6.26x", "6.28x", "9.13x", "5.59x"
        ],
        "16T": [
            "11.61x", "4.22x", "10.43x", "7.68x", 
            "12.12x", "10.78x", "11.23x", "11.76x", "10.82x"
        ],
        "32T": [
            "21.32x", "7.39x", "19.79x", "14.22x", 
            "21.54x", "19.46x", "21.26x", "16.55x", "21.00x"
        ],
        "64T": [
            "21.63x", "7.35x", "20.74x", "13.62x", 
            "21.64x", "19.92x", "23.98x", "18.04x", "23.20x"
        ]
    }

    df = pd.DataFrame(dados)

    # 2. Configuração da Figura
    # Largura x Altura (Larga para acomodar as colunas confortavelmente)
    fig, ax = plt.subplots(figsize=(12, 5)) 
    ax.axis('off')

    # 3. Desenhar a Tabela
    tabela = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 4. Estilização
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)

    cor_cabecalho = '#40466e' # Azul Acadêmico
    cor_par = '#f1f1f2'
    cor_impar = '#ffffff'

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_height(0.1) # Altura das linhas
        
        if row == 0: # Cabeçalho
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(cor_cabecalho)
        else:
            # Cores alternadas
            bg_color = cor_par if row % 2 == 0 else cor_impar
            cell.set_facecolor(bg_color)
            
            # (Opcional) Destaque para o 'openmp' que venceu no 64T Large
            # if df.iloc[row-1]["Modelo"] == "openmp":
            #     cell.set_text_props(weight='bold')

    # 5. Título
    plt.title("Escalabilidade por Número de Threads - Dataset LARGE", 
              fontsize=14, weight='bold', pad=15)

    # 6. Salvar
    arquivo_saida = "Tabela_Escalabilidade_Large.png"
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gerado com sucesso: {arquivo_saida}")

if __name__ == "__main__":
    gerar_imagem_tabela_ranking()
    gerar_tabela_detalhada()
    gerar_tabela_scaling()
    gerar_tabela_ranking_large()
    gerar_tabela_detalhada_large()
    gerar_tabela_scaling_large()