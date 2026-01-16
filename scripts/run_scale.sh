#!/bin/bash

# =================================================================
# SCRIPT DE AUTOMAÇÃO DE EXPERIMENTOS - ESCALABILIDADE (HPC)
# =================================================================

# 1. Configurações Iniciais
THREADS_SEQUENCE=(1 2 4 8 16 32 64)
DATASET=${1:-"-DSTANDARD_DATASET"} # Pega o primeiro argumento ou usa Standard

echo "📂 Preparando ambiente de resultados..."
mkdir -p results
rm -f results/raw_times.csv

# 2. COMPILAÇÃO ÚNICA (Fora do Loop)
# Compilamos uma vez só para o dataset escolhido. Isso economiza muito tempo!
echo "🔨 Compilando todos os modelos para o dataset: $DATASET"
make all DATASET_SIZE=$DATASET

# Verificação de erro na compilação
if [ $? -ne 0 ]; then
    echo "❌ Erro crítico na compilação. Abortando experimento."
    exit 1
fi

# 3. LOOP DE EXECUÇÃO (Apenas Run)
# Definimos variáveis de afinidade para o Threadripper não "pular" threads entre cores
# Isso reduz o ruído estatístico nos seus gráficos de mestrado.
export OMP_PROC_BIND=true
export OMP_PLACES=cores

for t in "${THREADS_SEQUENCE[@]}"; do
    echo "=========================================================="
    echo "🚀 EXECUTANDO: $t THREADS | DATASET: $DATASET"
    echo "=========================================================="
    
    # Chamamos o executor.py diretamente ou via make run. 
    # Como já compilamos acima, o executor apenas rodará os binários.
    python3 scripts/executor.py $t
    
    echo "✅ Concluído nível de paralelismo: $t"
    echo ""
done

# 4. GERAÇÃO DE RELATÓRIOS
echo "📊 Processando dados e gerando visualizações..."
make analyze

echo "=========================================================="
echo "✨ EXPERIMENTO FINALIZADO!"
echo "📈 Resultados em: results/scaling_curve.png"
echo "=========================================================="