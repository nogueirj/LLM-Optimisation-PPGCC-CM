#!/bin/bash

# Cores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Detecta o Sistema Operacional
OS_TYPE=$(uname -s)

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}   COLETOR DE INFO (macOS Clang + libomp & Linux)     ${NC}"
echo -e "${CYAN}======================================================${NC}"

# --- 1. PROCESSADOR ---
echo -e "\n${GREEN}[1] PROCESSADOR${NC}"

if [ "$OS_TYPE" == "Darwin" ]; then
    CPU_MODEL=$(sysctl -n machdep.cpu.brand_string)
    CPU_CORES=$(sysctl -n hw.physicalcpu)
    CPU_THREADS=$(sysctl -n hw.logicalcpu)
else
    CPU_MODEL=$(lscpu | grep "Model name" | cut -d: -f2 | xargs)
    CPU_THREADS=$(nproc)
    CORES_PER_SOCKET=$(lscpu | grep "Core(s) per socket:" | awk '{print $4}')
    SOCKETS=$(lscpu | grep "Socket(s):" | awk '{print $2}')
    if [ -z "$SOCKETS" ]; then SOCKETS=1; fi
    if [ -z "$CORES_PER_SOCKET" ]; then CORES_PER_SOCKET=$CPU_THREADS; fi
    CPU_CORES=$(($CORES_PER_SOCKET * $SOCKETS))
fi

echo "Modelo:   $CPU_MODEL"
echo "Núcleos:  $CPU_CORES físicos"
echo "Threads:  $CPU_THREADS lógicas"


# --- 2. MEMÓRIA ---
echo -e "\n${GREEN}[2] MEMÓRIA RAM${NC}"

if [ "$OS_TYPE" == "Darwin" ]; then
    TOTAL_BYTES=$(sysctl -n hw.memsize)
    TOTAL_MEM=$(echo "scale=2; $TOTAL_BYTES / 1024 / 1024 / 1024" | bc)
    echo "Total: ${TOTAL_MEM} GB"
    echo "--- Detalhes (system_profiler) ---"
    system_profiler SPMemoryDataType 2>/dev/null | grep -E "Type:|Speed:" | head -n 2 | xargs
else
    TOTAL_MEM=$(free -h --si | awk '/Mem:/ {print $2}')
    echo "Total (aprox): $TOTAL_MEM"
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}* (Linux) Execute com sudo para ver DDR/MHz${NC}"
    else
        MEM_TYPE=$(dmidecode --type 17 | grep "Type:" | grep -v "Unknown" | head -n 1 | cut -d: -f2 | xargs)
        MEM_SPEED=$(dmidecode --type 17 | grep "Configured Memory Speed:" | grep -v "Unknown" | head -n 1 | cut -d: -f2 | xargs)
        echo "Tipo: $MEM_TYPE @ $MEM_SPEED"
    fi
fi


# --- 3. ARMAZENAMENTO ---
echo -e "\n${GREEN}[3] ARMAZENAMENTO${NC}"

if [ "$OS_TYPE" == "Darwin" ]; then
    diskutil list internal physical | grep "GUID_partition_scheme" -B 1
else
    lsblk -d -o NAME,SIZE,MODEL,TRAN | grep -v "loop"
fi


# --- 4. SISTEMA OPERACIONAL ---
echo -e "\n${GREEN}[4] SISTEMA OPERACIONAL${NC}"

if [ "$OS_TYPE" == "Darwin" ]; then
    OS_NAME=$(sw_vers -productName)
    OS_VER=$(sw_vers -productVersion)
    KERNEL_VER=$(uname -r)
    ARCH=$(uname -m)
    echo "Sistema: macOS $OS_NAME $OS_VER"
    echo "Kernel: Darwin $KERNEL_VER ($ARCH)"
else
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$PRETTY_NAME
    else
        OS_NAME=$(uname -s)
    fi
    KERNEL_VER=$(uname -r)
    echo "Distro: $OS_NAME"
    echo "Kernel: $KERNEL_VER"
fi


# --- 5. COMPILADOR & OPENMP (CLANG + LIBOMP CHECK) ---
echo -e "\n${GREEN}[5] COMPILADOR & OPENMP${NC}"

COMPILER_CMD="gcc" # No Mac, 'gcc' é alias para clang

if [ "$OS_TYPE" == "Darwin" ]; then
    # Verifica se libomp está instalada via brew
    if brew list libomp &>/dev/null; then
        BREW_PREFIX=$(brew --prefix)
        echo -e "${CYAN}Detectado libomp via Homebrew.${NC}"
        
        # Flags mágicas para o Clang achar o OpenMP do Brew
        OMP_FLAGS="-Xpreprocessor -fopenmp -I$BREW_PREFIX/include -L$BREW_PREFIX/lib -lomp"
    else
        # Se não achou libomp, tenta apenas -fopenmp (caso seja gcc real)
        OMP_FLAGS="-fopenmp"
    fi
else
    # Linux padrão
    OMP_FLAGS="-fopenmp"
fi

if command -v $COMPILER_CMD &> /dev/null; then
    GCC_FULL=$($COMPILER_CMD --version | head -n 1)
    echo "Binário: $COMPILER_CMD"
    echo "Versão: $GCC_FULL"
    
    # Teste real de compilação de OpenMP
    # Criamos um mini programa C que imprime a versão do OpenMP
    cat <<EOF > teste_omp.c
#include <stdio.h>
#include <omp.h>
int main() {
    printf("%d", _OPENMP);
    return 0;
}
EOF

    # Tenta compilar com as flags detectadas
    $COMPILER_CMD $OMP_FLAGS teste_omp.c -o teste_omp 2>/dev/null
    
    if [ $? -eq 0 ]; then
        OMP_DATE=$(./teste_omp)
        case $OMP_DATE in
            201511) OMP_VER="4.5" ;;
            201811) OMP_VER="5.0" ;;
            202011) OMP_VER="5.1" ;;
            202111) OMP_VER="5.2" ;;
            *) OMP_VER="Data $OMP_DATE" ;;
        esac
        echo -e "Suporte OpenMP: ${GREEN}SIM${NC} (Versão $OMP_VER)"
        echo "Flags usadas: $OMP_FLAGS"
    else
        echo -e "Suporte OpenMP: ${RED}NÃO DETECTADO${NC}"
        echo "Erro ao compilar teste com flags: $OMP_FLAGS"
        if [ "$OS_TYPE" == "Darwin" ]; then
            echo "Dica: Tente 'brew install libomp' se ainda não fez."
        fi
    fi
    
    # Limpeza
    rm -f teste_omp.c teste_omp
else
    echo "Compilador não encontrado."
fi

echo -e "\n${CYAN}======================================================${NC}"