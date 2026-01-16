#!/bin/bash

# =================================================================
# SCRIPT DE AUTOMAÇÃO DE EXPERIMENTOS - ESCALABILIDADE (HPC)
# Mestrado em Ciência da Computação
# =================================================================

# 1. Definição da sequência de threads (Potências de 2 até o limite da máquina)
# No Mac use até 8, no Threadripper mude para 1 2 4 8 16 32 64
THREADS_SEQUENCE=(1 2 4 8 16 32 64)

# 2. Limpeza de resultados anteriores para evitar contaminação
echo "🧹 Limpando dados antigos..."
rm -f results/raw_times.csv
mkdir -p results

# 3. Loop de execução
for t in "${THREADS_SEQUENCE[@]}"; do
    echo "=========================================================="
    echo "🚀 INICIANDO EXPERIMENTO COM $t THREADS"
    echo "=========================================================="
    
    # Chama o Master Makefile passando o número de threads
    # O executor.py salvará os dados com a coluna de threads correta
    make run N_THREADS=$t
    
    echo "✅ Concluído: $t threads."
    echo ""
done

# 4. Gerar Análise Final
echo "📊 Gerando gráficos de escalabilidade e tabelas LaTeX..."
make analyze

echo "=========================================================="
echo "✨ BATERIA DE TESTES FINALIZADA COM SUCESSO!"
echo "📈 Verifique a pasta results/ para visualizar os gráficos."
echo "=========================================================="