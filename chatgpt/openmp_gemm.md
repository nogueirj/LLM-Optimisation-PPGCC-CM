# 🧵 Paralelização com OpenMP no GEMM do PolyBench

Este documento mostra como paralelizar o código GEMM (`gemm.c`) do benchmark PolyBench usando OpenMP, além de como medir o speedup e testar diferentes estratégias de agendamento.

---

## ✅ Inserindo OpenMP

### 🔧 Adicione o cabeçalho `omp.h`

Logo após os `#includes` no topo do arquivo:

```c
#include <omp.h>
```

---

🔄 Atualize a função `kernel_gemm` com OpenMP

```c static
static
void kernel_gemm(int ni, int nj, int nk,
		 DATA_TYPE alpha,
		 DATA_TYPE beta,
		 DATA_TYPE POLYBENCH_2D(C,NI,NJ,ni,nj),
		 DATA_TYPE POLYBENCH_2D(A,NI,NK,ni,nk),
		 DATA_TYPE POLYBENCH_2D(B,NK,NJ,nk,nj))
{
  int i, j, k;

#pragma scop
  /* C := alpha*A*B + beta*C */
  #pragma omp parallel for private(i,j,k) shared(C,A,B,alpha,beta)
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NJ; j++)
      {
        C[i][j] *= beta;
        for (k = 0; k < _PB_NK; ++k)
          C[i][j] += alpha * A[i][k] * B[k][j];
      }
#pragma endscop
}
```

### ✅ **Notas importantes:**

- A paralelização ocorre no nível do loop externo `i` (que geralmente é a melhor escolha em matrizes grandes).
- Como cada iteração de `i` atualiza `C[i][j]`, e não há sobreposição entre diferentes valores de `i`, não há *data races*.
- A cláusula `private(i,j,k)` garante que cada thread tenha suas próprias variáveis locais para os índices.
- `shared(...)` é tecnicamente opcional se você já sabe que `C`, `A`, `B`, etc., são visíveis para todas as threads, mas é boa prática declarar explicitamente.

### 🔄 Atualize a função `kernel_gemm` com OpenMP

Vamos usar `collapse(2)` para paralelizar **dois níveis de loop** (`i` e `j`) de uma vez só. Isso permite ao OpenMP distribuir melhor o trabalho entre as threads, especialmente quando o loop interno (`j`) tem iterações suficientes para justificar o paralelismo extra.

#### ✅ Versão com `collapse(2)`

```c
static
void kernel_gemm(int ni, int nj, int nk,
		 DATA_TYPE alpha,
		 DATA_TYPE beta,
		 DATA_TYPE POLYBENCH_2D(C,NI,NJ,ni,nj),
		 DATA_TYPE POLYBENCH_2D(A,NI,NK,ni,nk),
		 DATA_TYPE POLYBENCH_2D(B,NK,NJ,nk,nj))
{
  int i, j, k;

#pragma scop
  /* C := alpha*A*B + beta*C */
  #pragma omp parallel for collapse(2) private(i,j,k) shared(C,A,B,alpha,beta)
  for (i = 0; i < _PB_NI; i++)
    for (j = 0; j < _PB_NJ; j++)
      {
        C[i][j] *= beta;
        for (k = 0; k < _PB_NK; ++k)
          C[i][j] += alpha * A[i][k] * B[k][j];
      }
#pragma endscop
}
```

---

### 🧠 **Por que isso pode ser melhor:**

- Quando o número de threads é alto, `collapse(2)` permite mais granularidade e melhor balanceamento de carga.
- Útil especialmente quando `ni` ou `nj` são pequenos demais isoladamente, mas seu produto (`ni * nj`) é grande.

---

### 🛠️ **Compilação com suporte ao OpenMP**

Use a flag `-fopenmp` ao compilar com `gcc` ou `clang`:

```bash
gcc -O2 -fopenmp -I utilities gemm.c -o gemm -lm
```

-----

## 🚀 Medindo Speedup

### 🧪 Compilação

#### Serial:
```bash
gcc -O2 gemm.c -o gemm_serial -lm
```

#### Paralelo:
```bash
gcc -O2 -fopenmp gemm.c -o gemm_omp -lm
```

---

### 🧮 Execução e comparação

Execute ambos e compare o tempo usando os timers do PolyBench.

```bash
./gemm_serial
./gemm_omp
```

---

## ⚙️ Testando diferentes estratégias de `schedule`

Você pode alterar a diretiva para explorar diferentes agendamentos:

```c
#pragma omp parallel for collapse(2) schedule(dynamic,16) private(i,j,k) shared(C,A,B,alpha,beta)
```

### Exemplos:

- `schedule(static)`
- `schedule(dynamic,32)`
- `schedule(guided)`

---

## 📊 Medir número de threads

Adicione no `main()`:

```c
printf("Rodando com %d threads.\n", omp_get_max_threads());
```

E execute com diferentes valores de `OMP_NUM_THREADS`:

```bash
OMP_NUM_THREADS=2 ./gemm_omp
OMP_NUM_THREADS=4 ./gemm_omp
OMP_NUM_THREADS=8 ./gemm_omp
```

---

## 💡 Automatizar os testes

Podemos usar um script para automatizar os testes de desempenho com diferentes estratégias de `schedule` e números de threads, o script `run_gemm_openmp.sh`:

```shell
#!/bin/bash

# Script: run_gemm_openmp.sh
# Objetivo: Rodar a versão paralela do GEMM com diferentes números de threads e agendamentos OpenMP

EXEC=./gemm_omp
SCHEDULES=("static" "dynamic,32" "guided")
THREADS=(1 2 4 8)

echo "Iniciando testes de performance com OpenMP"
echo "=========================================="

for sched in "${SCHEDULES[@]}"; do
  echo -e "\nSchedule: $sched"
  for t in "${THREADS[@]}"; do
    export OMP_NUM_THREADS=$t
    echo -e "\n[Threads: $t]"
    OMP_SCHEDULE=$sched $EXEC
  done
done
```



📥 Baixar script `run_gemm_openmp.sh`

### 🧪 Como usar

1. Coloque o executável `gemm_omp` no mesmo diretório do script.
2. Torne o script executável (se ainda não estiver):

```bash
chmod +x run_gemm_openmp.sh
```

1. Execute:

```bash
./run_gemm_openmp.sh
```

Ele vai testar as combinações de:

- `schedule(static)`
- `schedule(dynamic,32)`
- `schedule(guided)`

Com os seguintes valores de `OMP_NUM_THREADS`: **1, 2, 4, 8**.

Se quiser incluir mais estratégias ou threads, posso ajustar rapidinho! 
