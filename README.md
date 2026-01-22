# Experimentos para o artigo PAPER GENIA.

Link para o Artigo: [`Uso de IA Generativa na Geração de Código Paralelo para Arquiteturas Heterogêneas`](https://pt.overleaf.com/project/67dc14860cf4074a0dd5d508)

<https://www.overleaf.com/project/67f3d7d192540c2e2cb9e569>

## TODO

### Reunião: 20/03/2025

1. Fornecer o Código Original/Sequencial e pedir para gerar o Código com as diretivas `OpenMP` para comparar com o mesmo benchmark no `Polybench-ACC/OpenMP` feito por humano.

2. Analisar o código gerado se utiliza diretivas mais recentes, por exemplo, construtores para laços, construtor `FOR` é mais antigo e `TASKLOOP` mais recente.

3. Pedir para gerar código `OpenMP` para `GPU`, construtor `target` que gera código para `GPU` pelo `GCC`, sem a necessidade de saber `CUDA`. Comparar com o `Polybench-GPU`

### Reunião: 26/05/2025

Júlio mandou artigos parecidos com o que estamos fazendo:
<https://arxiv.org/pdf/2401.12554>
<https://dl.acm.org/doi/10.1145/3625549.3658689>

Artigo das métricas que citam: <https://arxiv.org/abs/2107.03374#>

## Ferramentas

```bash
https://ollama.com/
https://github.com/open-webui/open-webui

https://ollama.com/library/deepseek-coder-v2
ollama run deepseek-coder-v2

https://ollama.com/search


```

O `deepseek-coder-v2:236b` não rolou na minha máquina com 32GB.

```bash
[rag@backporting open-webui]$ ollama run deepseek-coder-v2:236b
pulling manifest 
pulling 6bbfda8eb96d... 100% ▕███████▏ 132 GB                         
pulling 22091531faf0... 100% ▕███████▏  705 B                         
pulling 4bb71764481f... 100% ▕███████▏  13 KB                         
pulling 1c8f573e830c... 100% ▕███████▏ 1.1 KB                         
pulling 19f2fb9e8bc6... 100% ▕███████▏   32 B                         
pulling 1f3aee0087c2... 100% ▕███████▏  569 B                         
verifying sha256 digest 
writing manifest 
success 
Error: model requires more system memory (132.5 GiB) than is available (11.5 GiB)
[rag@backporting open-webui]$
```

## Compilação e Execução dos Experimentos

Como estamo usando o `PolyBench-ACC` e `PolyBenchC-4.2.1` como sub módulos é necessário quando baixar o repositório iniciar e atualizá-los, eles não vão para o repositório.

```bash
$ git clone https://github.com/nogueirj/LLM-Optimisation-PPGCC-CM.git
Cloning into 'LLM-Optimisation-PPGCC-CM'...
remote: Enumerating objects: 233, done.
remote: Counting objects: 100% (233/233), done.
remote: Compressing objects: 100% (131/131), done.
remote: Total 233 (delta 113), reused 217 (delta 100), pack-reused 0 (from 0)
Receiving objects: 100% (233/233), 611.85 KiB | 966.00 KiB/s, done.
Resolving deltas: 100% (113/113), done.
rag@titanx:~$ git submodule init
fatal: not a git repository (or any of the parent directories): .git
rag@titanx:~$ cd LLM-Optimisation-PPGCC-CM/
rag@titanx:~/LLM-Optimisation-PPGCC-CM$ git submodule init
Submodule 'PolyBench-ACC' (https://github.com/cavazos-lab/PolyBench-ACC.git) registered for path 'PolyBench-ACC'
Submodule 'PolyBenchC-4.2.1' (https://github.com/MatthiasJReisinger/PolyBenchC-4.2.1) registered for path 'PolyBenchC-4.2.1'
rag@titanx:~/LLM-Optimisation-PPGCC-CM$ git submodule update
Cloning into '/home/rag/LLM-Optimisation-PPGCC-CM/PolyBench-ACC'...
Cloning into '/home/rag/LLM-Optimisation-PPGCC-CM/PolyBenchC-4.2.1'...
Submodule path 'PolyBench-ACC': checked out '70ea4ca9047dc4ec9c3ca79b4c91b3b2cc1510e7'
Submodule path 'PolyBenchC-4.2.1': checked out '3e872547cef7e5c9909422ef1e6af03cf4e56072'
```

Preparei um script par executar a versão sequencial, está no diretório `scripts`. O _script_ `./run_polybench_mult_exec.sh` vai executar e coletar o tempo de 10 repetições, ele chama um script em python que calcula a média e o desvio padrão e depois gera um gráfico.

```bash
~/LLM-Optimisation-PPGCC-CM/scripts$ ./run_polybench_mult_exec.sh ../PolyBenchC-4.2.1/ 10 gcc "-O3 -march=native -lm" 
→ Início: sex 23 mai 2025 16:07:38 -03.
Received 4 arguments.
Argument 1: ../PolyBenchC-4.2.1/
Argument 2: 10
Argument 3: gcc
Argument 4: -O3 -march=native -lm
== Etapa 1: Compilando kernels para todos os tamanhos ==
  • ludcmp_mini
  • ludcmp_small
  • ludcmp_medium
  • ludcmp_large
  • ludcmp_extralarge
  • trisolv_mini
  • trisolv_small
  • trisolv_medium
  • trisolv_large
  • trisolv_extralarge
  • lu_mini
  • lu_small
  • lu_medium
  • lu_large
  • lu_extralarge
  • durbin_mini
  • durbin_small
  • durbin_medium
  • durbin_large
  • durbin_extralarge
  • cholesky_mini
  • cholesky_small
  • cholesky_medium
  • cholesky_large
  • cholesky_extralarge
  • gramschmidt_mini
  • gramschmidt_small
  • gramschmidt_medium
  • gramschmidt_large
  • gramschmidt_extralarge
  • 3mm_mini
  • 3mm_small
  • 3mm_medium
  • 3mm_large
  • 3mm_extralarge
  • 2mm_mini
  • 2mm_small
  • 2mm_medium
  • 2mm_large
  • 2mm_extralarge
  • atax_mini
  • atax_small
  • atax_medium
  • atax_large
  • atax_extralarge
  • doitgen_mini
  • doitgen_small
  • doitgen_medium
  • doitgen_large
  • doitgen_extralarge
  • bicg_mini
  • bicg_small
  • bicg_medium
  • bicg_large
  • bicg_extralarge
  • mvt_mini
  • mvt_small
  • mvt_medium
  • mvt_large
  • mvt_extralarge
  • symm_mini
  • symm_small
  • symm_medium
  • symm_large
  • symm_extralarge
  • gemver_mini
  • gemver_small
  • gemver_medium
  • gemver_large
  • gemver_extralarge
  • trmm_mini
  • trmm_small
  • trmm_medium
  • trmm_large
  • trmm_extralarge
  • syr2k_mini
  • syr2k_small
  • syr2k_medium
  • syr2k_large
  • syr2k_extralarge
  • syrk_mini
  • syrk_small
  • syrk_medium
  • syrk_large
  • syrk_extralarge
  • gesummv_mini
  • gesummv_small
  • gesummv_medium
  • gesummv_large
  • gesummv_extralarge
  • gemm_mini
  • gemm_small
  • gemm_medium
  • gemm_large
  • gemm_extralarge
  • correlation_mini
  • correlation_small
  • correlation_medium
  • correlation_large
  • correlation_extralarge
  • covariance_mini
  • covariance_small
  • covariance_medium
  • covariance_large
  • covariance_extralarge
  • heat-3d_mini
  • heat-3d_small
  • heat-3d_medium
  • heat-3d_large
  • heat-3d_extralarge
  • seidel-2d_mini
  • seidel-2d_small
  • seidel-2d_medium
  • seidel-2d_large
  • seidel-2d_extralarge
  • jacobi-2d_mini
  • jacobi-2d_small
  • jacobi-2d_medium
  • jacobi-2d_large
  • jacobi-2d_extralarge
  • fdtd-2d_mini
  • fdtd-2d_small
  • fdtd-2d_medium
  • fdtd-2d_large
  • fdtd-2d_extralarge
  • adi_mini
  • adi_small
  • adi_medium
  • adi_large
  • adi_extralarge
  • jacobi-1d_mini
  • jacobi-1d_small
  • jacobi-1d_medium
  • jacobi-1d_large
  • jacobi-1d_extralarge
  • nussinov_mini
  • nussinov_small
  • nussinov_medium
  • nussinov_large
  • nussinov_extralarge
  • deriche_mini
  • deriche_small
  • deriche_medium
  • deriche_large
  • deriche_extralarge
  • floyd-warshall_mini
  • floyd-warshall_small
  • floyd-warshall_medium
  • floyd-warshall_large
  • floyd-warshall_extralarge
== Etapa 2: Executando (10× por kernel/tamanho) e coletando tempos. ==
[2mm]
 44.868978 s            extralarge run 1/10
 44.835689 s            extralarge run 2/10
 45.133398 s            extralarge run 3/10
 44.932548 s            extralarge run 4/10
 45.684537 s            extralarge run 5/10
 45.315014 s            extralarge run 6/10
 45.241562 s            extralarge run 7/10
 45.116489 s            extralarge run 8/10
 45.020022 s            extralarge run 9/10
 45.429856 s            extralarge run 10/10
[2mm]
 1.588630 s             large      run 1/10
 1.581165 s             large      run 2/10
 1.581217 s             large      run 3/10
 1.598157 s             large      run 4/10
 1.587820 s             large      run 5/10
 1.587313 s             large      run 6/10
 1.596565 s             large      run 7/10
 1.576189 s             large      run 8/10
 1.575682 s             large      run 9/10
 1.587147 s             large      run 10/10
[2mm]
 0.012455 s             medium     run 1/10
 0.012308 s             medium     run 2/10
 0.012368 s             medium     run 3/10
 0.012274 s             medium     run 4/10
 0.012464 s             medium     run 5/10
 0.012624 s             medium     run 6/10
 0.012667 s             medium     run 7/10
 0.012572 s             medium     run 8/10
 0.012677 s             medium     run 9/10
 0.012564 s             medium     run 10/10
[2mm]
 0.000008 s             mini       run 1/10
 0.000009 s             mini       run 2/10
 0.000008 s             mini       run 3/10
 0.000009 s             mini       run 4/10
 0.000009 s             mini       run 5/10
 0.000008 s             mini       run 6/10
 0.000008 s             mini       run 7/10
 0.000009 s             mini       run 8/10
 0.000010 s             mini       run 9/10
 0.000009 s             mini       run 10/10
[2mm]
 0.000223 s             small      run 1/10
 0.000223 s             small      run 2/10
 0.000224 s             small      run 3/10
 0.000240 s             small      run 4/10
 0.000240 s             small      run 5/10
 0.000237 s             small      run 6/10
 0.000239 s             small      run 7/10
 0.000237 s             small      run 8/10
 0.000246 s             small      run 9/10
 0.000240 s             small      run 10/10
[3mm]
 73.800716 s            extralarge run 1/10
 • 3mm                  extralarge run 2/10
...
```

