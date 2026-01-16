#!/bin/bash

# Script: run_gemm_openmp.sh
# Objetivo: Rodar a versão paralela do GEMM com diferentes números de threads e agendamentos OpenMP

EXEC=./gemm-omp.exe
TIME=time
SCHEDULES=("static" "dynamic,32" "guided")
THREADS=(1 2 4 8)

echo "Iniciando testes de performance com OpenMP"
echo "=========================================="

for sched in "${SCHEDULES[@]}"; do
  echo -e "\nSchedule: $sched"
  for t in "${THREADS[@]}"; do
    export OMP_NUM_THREADS=$t
    echo -e "\n[Threads: $t]"
    time OMP_SCHEDULE=$sched $EXEC
  done
done
