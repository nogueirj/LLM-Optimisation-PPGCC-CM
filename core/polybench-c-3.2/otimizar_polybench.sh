#!/bin/bash

# Lista de kernels que você deseja processar
KERNELS=("2mm" "3mm" "ata" "gemm" "syr2k")

for kernel in "${KERNELS[@]}"; do
    # Localiza o arquivo .c dentro da estrutura do PolyBench
    file=$(find . -name "${kernel}.c")
    
    if [ -z "$file" ]; then
        echo "------------------------------------------------"
        echo "⚠️  Aviso: Kernel $kernel não encontrado em ./linear-algebra"
        continue
    fi
    
    dir=$(dirname "$file")
    base=$(basename "$file" .c)
    
    echo "------------------------------------------------"
    echo "🚀 Iniciando otimização DawnCC: $kernel"
    echo "📍 Localização: $file"
    
    # Executa o DawnCC via Docker
    # O comando exporta o PATH para o Clang 3.7 e roda o script de análise
    docker run --rm -v $(pwd):/data -w /data gleisonsdm/dawncc /bin/bash -c \
    "export PATH=\$PATH:/usr/src/llvm-build/bin; /usr/src/DawnCC/run.sh -f $file"
    
    # Verifica qual arquivo foi gerado (o DawnCC costuma usar _omp.c ou _ai.c)
    # e renomeia para o seu padrão: dawnncc_optimized
    if [ -f "${dir}/${base}_omp.c" ]; then
        mv "${dir}/${base}_omp.c" "${dir}/${base}_dawnncc_optimized.c"
        echo "✅ Sucesso: ${base}_dawnncc_optimized.c gerado."
    elif [ -f "${dir}/${base}_ai.c" ]; then
        mv "${dir}/${base}_ai.c" "${dir}/${base}_dawnncc_optimized.c"
        echo "✅ Sucesso: ${base}_dawnncc_optimized.c gerado."
    else
        echo "❌ Erro: O DawnCC não gerou arquivo de saída para $kernel."
    fi
done

echo "------------------------------------------------"
echo "🎉 Processo concluído!"