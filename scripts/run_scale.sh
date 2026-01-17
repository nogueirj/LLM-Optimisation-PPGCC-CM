#!/bin/bash

# =================================================================
# SCRIPT DE AUTOMAÇÃO DE EXPERIMENTOS - ESCALABILIDADE (HPC)
# =================================================================

#!/bin/bash

THREADS_SEQUENCE=(1 2 4 8 16 32 64)

# 1. Limpeza inicial de resultados
echo "🧹 Limpando CSV de resultados antigos..."
rm -f results/raw_times.csv
mkdir -p results

# 2. Loop de Execução Pura
for t in "${THREADS_SEQUENCE[@]}"; do
    echo "=========================================================="
    echo "🚀 EXECUTANDO: $t THREADS"
    echo "=========================================================="
    
    # Chama o python que agora apenas executa os .exe
    python3 scripts/executor.py $t
    
    echo "✅ Concluído nível: $t threads."
done

# 3. Análise
make analyze

# 4. GERAÇÃO DE RELATÓRIOS
echo "📊 Processando dados e gerando visualizações..."
make analyze

echo "=========================================================="
echo "✨ EXPERIMENTO FINALIZADO!"
echo "📈 Resultados em: results/scaling_curve.png"
echo "=========================================================="