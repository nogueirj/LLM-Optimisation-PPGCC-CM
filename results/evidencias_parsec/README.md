# Evidências Empíricas de Execução Multithread — Suíte PARSEC 3.0 (`ws-trx50`)

Este diretório armazena as evidências visuais de telemetria de sistema (`htop`) coletadas no servidor **`ws-trx50`** (AMD Ryzen Threadripper 7970X — 32 núcleos físicos / 64 *threads* lógicas, 256 GB de RAM DDR5 ECC) durante a execução dos benchmarks da suíte **PARSEC 3.0** paralelizados automaticamente pelas variantes quantizadas da família `codestral-openmp`.

---

## 1. Arquivos Catalogados

| Arquivo | Cópia na Dissertação (`tese/figuras/`) | Binário em Execução | Threads Ativas | Ocupação por Thread Lógica (`0..63`) | Load Average (1m / 5m / 15m) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| [`htop_ws_trx50_swaptions_codestral_openmp_16b_32t.jpg`](./htop_ws_trx50_swaptions_codestral_openmp_16b_32t.jpg) | `evidencia_htop_parsec_swaptions_16b_32t.jpg` | `models/codestral-openmp_16b/swaptions-codestral-openmp_16b.exe` | 32 (1/core físico, `VIRT=2236M`) | `84,0%` – `100,0%` (`95%–97%` na thread do processo) | `86.64 / 73.52 / 59.64` |
| [`htop_ws_trx50_swaptions_codestral_openmp_16b_64t_1.jpg`](./htop_ws_trx50_swaptions_codestral_openmp_16b_64t_1.jpg) | `evidencia_htop_parsec_swaptions_16b_64t_1.jpg` | `models/codestral-openmp_16b/swaptions-codestral-openmp_16b.exe` | 64 (SMT, `VIRT=4540M`) | `85,9%` – `98,7%` | `95.46 / 91.50 / 70.53` |
| [`htop_ws_trx50_swaptions_codestral_openmp_16b_64t_2.jpg`](./htop_ws_trx50_swaptions_codestral_openmp_16b_64t_2.jpg) | `evidencia_htop_parsec_swaptions_16b_64t_2.jpg` | `models/codestral-openmp_16b/swaptions-codestral-openmp_16b.exe` | 64 (SMT, `VIRT=4540M`) | `86,3%` – `98,9%` | `98.10 / 91.85 / 70.41` |
| [`htop_ws_trx50_freqmine_codestral_openmp_16b.jpg`](./htop_ws_trx50_freqmine_codestral_openmp_16b.jpg) | `evidencia_htop_parsec_freqmine_16b.jpg` | `models/codestral-openmp_16b/freqmine-codestral-openmp_16b.exe` | 16 (`VIRT=147M`, `58 running`) | `61,5%` – `100,0%` | `69.74 / 57.69 / 48.59` |
| [`htop_ws_trx50_freqmine_codestral_openmp_8b.jpg`](./htop_ws_trx50_freqmine_codestral_openmp_8b.jpg) | `evidencia_htop_parsec_freqmine_8b.jpg` | `models/codestral-openmp_8b/freqmine-codestral-openmp_8b.exe` | 64 (`VIRT=531M`, `64 running`) | `85,8%` – `96,9%` | `101.04 / 98.15 / 85.54` |

---

## 2. Análise Técnica das Evidências

1. **Comparativo Arquitetural: 32 *Threads* (Núcleos Físicos) vs. 64 *Threads* (SMT) no Threadripper 7970X**:
   - Na execução com **32 *threads*** (`htop_ws_trx50_swaptions_codestral_openmp_16b_32t.jpg`, `VIRT = 2236M`), cada *thread* OpenMP é fixada em um núcleo físico exclusivo (`OMP_PLACES=cores`), atingindo utilização individual de **95,5% a 97,3% de CPU** por *thread* do processo.
   - Na execução com **64 *threads*** (`htop_ws_trx50_swaptions_codestral_openmp_16b_64t_2.jpg`, `VIRT = 4540M`), o *Simultaneous Multithreading* (SMT) ativa duas *threads* lógicas por núcleo físico Zen 4; cada *thread* individual opera entre **60% e 71% de CPU** devido ao compartilhamento das unidades vetoriais de ponto flutuante (FPU/AVX-512), elevando a ocupação agregada das 64 *threads* lógicas (`0..63`) para **86% a 99%** e o *Load Average* para **98.10**.
2. **Contraste de Pegada de Memória (`swaptions` vs. `freqmine`)**:
   - No `swaptions-codestral-openmp_16b.exe` (simulação de Monte Carlo do modelo HJM), o processo apresenta pegada enxuta de memória residente (`RES = 3776 KB`, `SHR = 2540 KB`), comprovando que as variáveis intermediárias foram alocadas em escopo privado nos registradores e caches L1/L2 privados de cada núcleo Zen 4.
   - No `freqmine-codestral-openmp_16b.exe` (mineração de padrões frequentes com contagem triangular de suporte e projeção de transações), observa-se maior intensidade de memória (`VIRT = 147M`, `RES = 27604 KB`), refletindo as matrizes de transações e coocorrência do perfil `LARGE_DATASET` (`native`).
3. **Sustentação de Paralelismo Efetivo e Desbalanceamento Natural em Laços Triangulares**:
   - Na segunda captura do `swaptions` (`htop_ws_trx50_swaptions_codestral_openmp_16b_64t_2.jpg`), o contador reporta `64 running` com *Load Average* instantâneo de `98.10`.
   - Na captura do `freqmine` (`htop_ws_trx50_freqmine_codestral_openmp_16b.jpg`), o perfil de ocupação entre `61,5%` e `100,0%` (`Load Average` de `69.74`) ilustra empiricamente o comportamento de um kernel com espaço de iteração triangular (`for (a = 0; a < nitems; a++) for (b = a; b < nitems; b++)`) e tráfego intensivo de barramentos de cache, além do compartilhamento concorrente da estação de trabalho multiusuário.

