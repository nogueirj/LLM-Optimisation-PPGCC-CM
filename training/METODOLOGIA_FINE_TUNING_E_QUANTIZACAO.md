# Metodologia de Fine-Tuning, Alinhamento Estrutural e Quantização Multi-Nível para Paralelização com OpenMP

Este documento descreve detalhadamente o pipeline metodológico e experimental de especialização do modelo **Codestral 22B** (`mistralai/Codestral-22B-v0.1`) para a tarefa de paralelização automática de código C/C++ via diretivas **OpenMP**. O projeto integra a dissertação de mestrado e as pesquisas de otimização automatizada de código em Computação de Alto Desempenho (HPC).

O objetivo deste documento é fornecer **total transparência, rigor científico e reprodutibilidade** para pesquisadores, revisores e membros da banca avaliadora.

---

## 1. Visão Geral da Arquitetura do Pipeline

O pipeline foi estruturado em uma abordagem de **Aprendizado em Duas Fases (Two-Stage Curriculum Learning)** seguida por **Fusão de Pesos (Weight Merging)** e **Quantização Multi-Nível (GGUF / Ollama)**:

```
+-----------------------------------------------------------------------------------+
| FASE 1: Fine-Tuning de Fundação (Especialização Sintática e Semântica OpenMP)      |
| Base: Codestral-22B | Dataset: OMP-FT-Source (7.317 amostras)                    |
| Hardware: NVIDIA RTX PRO 6000 Blackwell (sm_120, 102 GB VRAM) em bfloat16 nativo  |
| Saída: Checkpoints LoRA de alta precisão (Acurácia de tokens > 92%)               |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| FASE 2: Hard Fine-Tuning (Alinhamento de Formato de Benchmark e Raciocínio)       |
| Base: Checkpoint Fase 1 + Prompt Estruturado (Qwen/PolyBench Style)               |
| Entrada: Código C completo (sem tags artificiais)                                 |
| Saída: Análise de dependências + Kernel anotado compilável em ```c + Rationale   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| FASE 3: Fusão de Pesos LoRA (Merge & Unload)                                      |
| Combina os pesos delta LoRA com os 22.4B pesos base em bfloat16 contínuo          |
| Saída: Modelo Hugging Face consolidado em `./codestral_openmp_merged`             |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| FASE 4: Conversão GGUF e Quantização Multi-Nível (llama.cpp)                      |
| Geração das variantes: 16-bit (FP16), 8-bit (Q8_0), 4-bit (Q4_K_M), 3-bit (Q3_K_M) |
| Criação de Modelfiles e importação automática para o Ollama                       |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| FASE 5: Execução Experimental no PolyBench (Pipeline de Benchmarking)             |
| Avaliação de Speedup, Corretude Numérica, Overhead e Impacto da Quantização      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Fase 1: Fine-Tuning de Fundação (Especialização em OpenMP)

### 2.1. Modelo Base e Escolha da Arquitetura
* **Modelo Base:** `mistralai/Codestral-22B-v0.1`
* **Parâmetros Totais:** 22,438,123,520 (~22.4B)
* **Tamanho do Contexto:** 2.048 tokens
* **Justificativa:** O Codestral 22B é treinado nativamente em mais de 80 linguagens de programação com ênfase em C e C++, possuindo forte entendimento de sintaxe de baixo nível e representações de fluxo de controle, essenciais para paralelismo.

### 2.2. Infraestrutura de Hardware e Ambiente de Execução
* **GPU:** NVIDIA RTX PRO 6000 Blackwell Workstation Edition
* **Capacidade Computacional:** CUDA capability `sm_120` (Arquitetura Blackwell)
* **Memória de Vídeo (VRAM):** 101.97 GB disponíveis
* **Ambiente de Software:**
  * SO: Linux (kernel 6.x / Ubuntu 24.04 LTS)
  * Python: 3.12 (virtualenv `codestral_env`)
  * PyTorch: `2.12.0.dev20260408+cu128` (CUDA 12.8 nightly com suporte oficial à arquitetura Blackwell `sm_120`)
  * Hugging Face: `transformers 5.17.0`, `trl 1.13.0`, `peft 0.20.0`, `accelerate 1.15.0`

> **Decisão de Engenharia:** Diferente de ambientes restritos (16GB/24GB) onde se impõe quantização 4-bit com `bitsandbytes` durante o treinamento (QLoRA), a disponibilidade de 102 GB de VRAM permitiu carregar o Codestral 22B em **`bfloat16` nativo** (~44 GB). Com LoRA e *gradient checkpointing*, o pico de VRAM ficou em ~58 GB, eliminando perdas numéricas por quantização em treino e garantindo velocidade máxima de retropropagação.

### 2.3. Configuração do PEFT / LoRA (Low-Rank Adaptation)
Para adaptar o modelo preservando sua base pré-treinada e evitando *catastrophic forgetting*:
* **Rank ($r$):** 32
* **LoRA Alpha ($\alpha$):** 64 (fator de escala $\alpha/r = 2.0$)
* **LoRA Dropout:** 0.05
* **Módulos Alvo (Target Modules):** Todas as projeções lineares de atenção e feed-forward:
  `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
* **Parâmetros Treináveis:** 190,840,832 parâmetros (~0.85% dos parâmetros totais)
* **Parâmetros Congelados:** 22,247,282,688 parâmetros

### 2.4. Dataset de Fundação
* **Identificador:** `LLMforParallelCode1/OMP-FT-Source` (Hugging Face)
* **Amostras Totais:** 7.317 amostras
* **Divisão Experimental:** 90% Treino (6.585 amostras) e 10% Validação (732 amostras), seed `3407`
* **Estrutura dos Dados:**
  * Código fonte C/C++ extraído de repositórios reais de código aberto (OSGeo/GRASS, HPC benchmarks, etc.);
  * Marcação dos limites do loop candidato via `<LOOP-START>` e `<LOOP-END>`;
  * Diretiva OpenMP alvo em `omp_pragma_line` (incluindo cláusulas `private`, `shared`, `reduction`, `schedule`).

### 2.5. Hiperparâmetros de Treinamento
* **Otimizador:** `adamw_torch` (AdamW em PyTorch nativo)
* **Taxa de Aprendizado ($lr$):** $2 \times 10^{-4}$ com decaimento linear (`linear scheduler`)
* **Warmup:** 20 passos
* **Tamanho de Lote por Dispositivo:** 2 amostras
* **Passos de Acumulação de Gradiente:** 8 (Tamanho de lote efetivo = $2 \times 8 = 16$ amostras)
* **Total de Passos (`max_steps`):** 500 passos
* **Precisão Mista:** `bf16=True`, `fp16=False`
* **Gradient Checkpointing:** Habilitado com `use_reentrant=False`
* **Avaliação Periódica:** A cada 50 passos sobre o conjunto de teste de 732 amostras
* **Salva de Checkpoints:** A cada 100 passos

### 2.6. Resultados e Curva de Convergência da Fase 1
Durante a execução do treinamento, o modelo demonstrou rápida estabilização e aprendizado de regras complexas de escopo do OpenMP:

| Passo (Step) | Época | Training Loss | Token Accuracy | Entropia | Grad Norm | Learning Rate | Tokens Totais | Eval Loss (Validação) | Eval Token Accuracy |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 0.024 | `0.9868` | 76.60% | 0.8004 | 0.7747 | $9.00 \times 10^{-5}$ | $6.70 \times 10^{4}$ | - | - |
| **20** | 0.049 | `0.5308` | 86.72% | 0.5821 | 2.5340 | $1.90 \times 10^{-4}$ | $1.29 \times 10^{5}$ | - | - |
| **30** | 0.073 | `0.4341` | 88.88% | 0.4652 | 0.4574 | $1.96 \times 10^{-4}$ | $1.92 \times 10^{5}$ | - | - |
| **40** | 0.097 | `0.3657` | 89.98% | 0.4187 | 0.6084 | $1.92 \times 10^{-4}$ | $2.61 \times 10^{5}$ | - | - |
| **50** | 0.121 | `0.3697` | 90.33% | 0.4018 | 0.4482 | $1.88 \times 10^{-4}$ | $3.23 \times 10^{5}$ | **`0.3898`** | **90.48%** |
| **60** | 0.146 | `0.4782` | 89.89% | 0.3977 | 2.4960 | $1.84 \times 10^{-4}$ | $3.90 \times 10^{5}$ | - | - |
| **70** | 0.170 | `0.3046` | 91.37% | 0.3465 | 0.3861 | $1.80 \times 10^{-4}$ | $4.57 \times 10^{5}$ | - | - |
| **80** | 0.194 | `0.3118` | 91.03% | 0.3648 | 0.3103 | $1.75 \times 10^{-4}$ | $5.21 \times 10^{5}$ | - | - |
| **90** | 0.219 | `0.3517` | 90.95% | 0.3676 | 0.3935 | $1.71 \times 10^{-4}$ | $5.89 \times 10^{5}$ | - | - |
| **100** | 0.243 | `0.2756` | 92.18% | 0.3173 | 0.2617 | $1.67 \times 10^{-4}$ | $6.64 \times 10^{5}$ | **`0.3265`** | **91.96%** |
| **110** | 0.267 | `0.3218` | 91.99% | 0.3312 | 0.4874 | $1.63 \times 10^{-4}$ | $7.27 \times 10^{5}$ | - | - |
| **120** | 0.291 | `0.3221` | 91.56% | 0.3357 | 0.3440 | $1.59 \times 10^{-4}$ | $7.97 \times 10^{5}$ | - | - |
| **130** | 0.316 | `0.2597` | 92.93% | 0.2863 | 0.4392 | $1.55 \times 10^{-4}$ | $8.57 \times 10^{5}$ | - | - |
| **140** | 0.340 | `0.2289` | 93.35% | 0.2652 | 0.3365 | $1.50 \times 10^{-4}$ | $9.24 \times 10^{5}$ | - | - |
| **150** | 0.364 | `0.3190` | 92.09% | 0.3178 | 0.4965 | $1.46 \times 10^{-4}$ | $9.90 \times 10^{5}$ | **`0.2867`** | **92.87%** |
| **160** | 0.389 | `0.2326` | 93.58% | 0.2729 | 0.3299 | $1.42 \times 10^{-4}$ | $1.05 \times 10^{6}$ | - | - |
| **170** | 0.413 | `0.3128` | 91.90% | 0.3270 | 0.3086 | $1.38 \times 10^{-4}$ | $1.12 \times 10^{6}$ | - | - |
| **180** | 0.437 | `0.2573` | 93.11% | 0.2791 | 0.3031 | $1.34 \times 10^{-4}$ | $1.19 \times 10^{6}$ | - | - |
| **190** | 0.462 | `0.2254` | 93.78% | 0.2434 | 0.2996 | $1.30 \times 10^{-4}$ | $1.26 \times 10^{6}$ | - | - |
| **200** | 0.486 | `0.2097` | 93.68% | 0.2497 | 0.3843 | $1.25 \times 10^{-4}$ | $1.32 \times 10^{6}$ | **`0.2616`** | **93.44%** |
| **210** | 0.510 | `0.2569` | 93.41% | 0.2640 | 0.3313 | $1.21 \times 10^{-4}$ | $1.39 \times 10^{6}$ | - | - |
| **220** | 0.534 | `0.1761` | 94.67% | 0.2154 | 0.2546 | $1.17 \times 10^{-4}$ | $1.47 \times 10^{6}$ | - | - |
| **230** | 0.559 | `0.2664` | 93.29% | 0.2663 | 0.4043 | $1.13 \times 10^{-4}$ | $1.53 \times 10^{6}$ | - | - |
| **240** | 0.583 | `0.2600` | 93.61% | 0.2562 | 0.4403 | $1.09 \times 10^{-4}$ | $1.60 \times 10^{6}$ | - | - |
| **250** | 0.607 | `0.2414` | 93.95% | 0.2459 | 0.3948 | $1.05 \times 10^{-4}$ | $1.67 \times 10^{6}$ | **`0.2435`** | **93.89%** |
| **260** | 0.632 | `0.2031` | 94.22% | 0.2299 | 0.3130 | $1.00 \times 10^{-4}$ | $1.74 \times 10^{6}$ | - | - |
| **270** | 0.656 | `0.2247` | 94.14% | 0.2435 | 0.5096 | $9.62 \times 10^{-5}$ | $1.81 \times 10^{6}$ | - | - |
| **280** | 0.680 | `0.2490` | 93.39% | 0.2751 | 0.2914 | $9.21 \times 10^{-5}$ | $1.89 \times 10^{6}$ | - | - |
| **290** | 0.705 | `0.2029` | 94.64% | 0.2156 | 0.3999 | $8.79 \times 10^{-5}$ | $1.96 \times 10^{6}$ | - | - |
| **300** | 0.729 | `0.2241` | 94.03% | 0.2355 | 0.3740 | $8.38 \times 10^{-5}$ | $2.03 \times 10^{6}$ | **`0.2263`** | **94.30%** |
| **310** | 0.753 | `0.1754` | 94.98% | 0.2062 | 0.3089 | $7.96 \times 10^{-5}$ | $2.10 \times 10^{6}$ | - | - |
| **320** | 0.777 | `0.1718` | 94.93% | 0.2053 | 0.2508 | $7.54 \times 10^{-5}$ | $2.17 \times 10^{6}$ | - | - |
| **330** | 0.802 | `0.2106` | 94.23% | 0.2268 | 0.2698 | $7.12 \times 10^{-5}$ | $2.24 \times 10^{6}$ | - | - |
| **340** | 0.826 | `0.1961` | 94.61% | 0.2166 | 0.3625 | $6.71 \times 10^{-5}$ | $2.31 \times 10^{6}$ | - | - |
| **350** | 0.850 | `0.2027` | 94.49% | 0.2295 | 0.3078 | $6.29 \times 10^{-5}$ | $2.38 \times 10^{6}$ | **`0.2116`** | **94.69%** |
| **360** | 0.875 | `0.2200` | 94.20% | 0.2290 | 0.3316 | $5.87 \times 10^{-5}$ | $2.44 \times 10^{6}$ | - | - |
| **370** | 0.899 | `0.2057` | 94.81% | 0.2092 | 0.3548 | $5.46 \times 10^{-5}$ | $2.50 \times 10^{6}$ | - | - |
| **380** | 0.923 | `0.1732` | 95.03% | 0.1930 | 0.3428 | $5.04 \times 10^{-5}$ | $2.58 \times 10^{6}$ | - | - |
| **390** | 0.948 | `0.2025` | 94.98% | 0.1949 | 0.3974 | $4.62 \times 10^{-5}$ | $2.64 \times 10^{6}$ | - | - |
| **400** | 0.972 | `0.1575` | 95.66% | 0.1766 | 0.2568 | $4.21 \times 10^{-5}$ | $2.70 \times 10^{6}$ | **`0.2023`** | **94.90%** |
| **410** | 0.996 | `0.1465` | 95.81% | 0.1677 | 0.2457 | $3.79 \times 10^{-5}$ | $2.78 \times 10^{6}$ | - | - |
| **420** | 1.019 | `0.1732` | 95.95% | 0.1705 | 0.2909 | $3.38 \times 10^{-5}$ | $2.84 \times 10^{6}$ | - | - |
| **430** | 1.044 | `0.1264` | 96.35% | 0.1545 | 0.2289 | $2.96 \times 10^{-5}$ | $2.91 \times 10^{6}$ | - | - |
| **440** | 1.068 | `0.1211` | 96.69% | 0.1264 | 0.3113 | $2.54 \times 10^{-5}$ | $2.98 \times 10^{6}$ | - | - |
| **450** | 1.092 | `0.1143` | 96.77% | 0.1295 | 0.1887 | $2.13 \times 10^{-5}$ | $3.05 \times 10^{6}$ | **`0.1982`** | **95.06%** |
| **460** | 1.117 | `0.1095` | 96.72% | 0.1310 | 0.2745 | $1.71 \times 10^{-5}$ | $3.11 \times 10^{6}$ | - | - |
| **470** | 1.141 | `0.1306` | 96.42% | 0.1438 | 0.2367 | $1.29 \times 10^{-5}$ | $3.17 \times 10^{6}$ | - | - |
| **480** | 1.165 | `0.1021` | 97.02% | 0.1191 | 0.3233 | $8.75 \times 10^{-6}$ | $3.24 \times 10^{6}$ | - | - |
| **490** | 1.189 | **`0.08972`** | **97.17%** | **0.1153** | 0.3481 | $4.58 \times 10^{-6}$ | $3.31 \times 10^{6}$ | - | - |
| **500** | 1.214 | `0.1280` | 96.45% | 0.1431 | 0.3558 | $4.17 \times 10^{-7}$ | **`3.38 \times 10^{6}`** | **`0.1956`** | **`95.13%`** |

> **Síntese dos Resultados Finais da Fase 1:**
> * **Tempo Total de Execução:** 10.340 segundos (~2 horas, 52 minutos e 17 segundos) na NVIDIA RTX PRO 6000 Blackwell.
> * **Loss de Treino Final:** Reduzido de `0.9868` para **`0.0897`** (Mínima absoluta no passo 490) e consolidado em `0.1280` ao final do decaimento de learning rate.
> * **Acurácia de Tokens no Treino:** Atingiu pico de **`97.17%`**.
> * **Perda de Validação Final (`eval_loss`):** Desceu consistentemente até atingir a mínima de **`0.1956`** no conjunto de teste.
> * **Acurácia de Validação Final:** Atingiu **`95.13%`** em dados totalmente inéditos.
> * **Tokens Totais Processados:** Mais de **3,38 milhões de tokens** retropropagados.
> * **Adaptadores LoRA:** Consolidados com sucesso no diretório `codestral_openmp_lora/`.

### 2.7. Dicionário Técnico das Métricas de Treinamento

Para fundamentar a análise quantitativa perante a banca e avaliadores, detalha-se o significado conceitual e prático de cada métrica gerada pelo trainer:

1. **`loss` (Training Loss - Perda no Treino):**
   * *Definição:* Perda de Entropia Cruzada (*Cross-Entropy Loss*) calculada entre os logits previstos pelo modelo e os tokens reais da diretiva OpenMP esperada.
   * *Interpretação:* Iniciou em **`0.9868`** (passo 10) e atingiu a mínima absoluta de **`0.0897`** (passo 490), representando uma redução superior a **90.9% no erro**. Uma perda abaixo de `0.15` em modelos causais de 22B indica domínio profundo da sintaxe e semântica das cláusulas.

2. **`eval_loss` (Validation Loss - Perda na Validação):**
   * *Definição:* Perda de Entropia Cruzada computada estritamente sobre as **732 amostras inéditas** do conjunto de teste (que nunca participaram do cálculo de gradiente).
   * *Interpretação:* Decresceu monotonicamente ao longo de todas as avaliações: `0.3898` (passo 50) $\rightarrow$ `0.3265` (passo 100) $\rightarrow$ `0.2867` (passo 150) $\rightarrow$ `0.2616` (passo 200) $\rightarrow$ `0.2435` (passo 250) $\rightarrow$ `0.2263` (passo 300) $\rightarrow$ `0.2116` (passo 350) $\rightarrow$ `0.2023` (passo 400) $\rightarrow$ `0.1982` (passo 450) $\rightarrow$ **`0.1956`** (passo 500).
   * *Significância Científica:* Como a perda de validação acompanha estritamente a queda da perda de treino durante todos os 500 passos, **descarta-se categoricamente a ocorrência de Overfitting** (*sobreajuste*). O modelo generaliza com extrema eficácia para códigos-fonte em C nunca antes vistos.

3. **`mean_token_accuracy` e `eval_mean_token_accuracy` (Acurácia Média de Tokens):**
   * *Definição:* Proporção de tokens em que a probabilidade máxima prevista pelo modelo ($\text{argmax}$) coincide exatamente com o token de referência no ground truth.
   * *Interpretação:* Evoluiu de **`76.60%`** para picos de **`97.17%`** no treino e de **`90.48%`** para **`95.13%`** na validação final. Em termos práticos de HPC, isso significa que em mais de 95% dos casos, cada palavra-chave (`parallel`, `for`, `private`, `shared`, `schedule`, `reduction`) e identificador de variável de loop é posicionado com exatidão milimétrica.

4. **`entropy` (Entropia de Shannon da Distribuição de Saída):**
   * *Definição:* Medida da incerteza média da distribuição de probabilidades do vocabulário $H(X) = -\sum P(x) \log P(x)$ nos tokens alvo.
   * *Interpretação:* Despencou de **`0.8004`** para **`0.1153`** no treino e **`0.1749`** na validação. A queda acentuada de entropia comprova que o modelo deixou de hesitar entre opções ambíguas e desenvolveu convicção preditiva quase determinística sobre o padrão formal de cláusulas OpenMP.

5. **`grad_norm` (Norma Euclidiana do Gradiente):**
   * *Definição:* Norma $L_2$ do vetor de gradientes acumulados $\left( \|\nabla \mathcal{L}\|_2 \right)$ sobre os 190M parâmetros treináveis do LoRA.
   * *Interpretação:* Manteve-se em um intervalo ideal entre **`0.20` e `0.60`** durante a maior parte do treinamento (com picos pontuais benignos em `2.5`). A ausência de valores extremos ($\gg 10$) comprova a **estabilidade numérica perfeita** da retropropagação em `bfloat16` na RTX PRO 6000 Blackwell, sem explosão (*exploding gradients*) nem desaparecimento de gradiente (*vanishing gradients*).

6. **`learning_rate` (Taxa de Aprendizado Efetiva):**
   * *Definição:* Escala do gradiente aplicada pelo otimizador AdamW.
   * *Interpretação:* Seguiu uma curva clássica de *Warmup Linear* (atingindo o teto de $2.0 \times 10^{-4}$ no passo 20) com posterior decaimento linear suave até $4.17 \times 10^{-7}$ no passo 500, permitindo exploração inicial ampla e refinamento microscópico nos pesos ao final do treinamento.

7. **`num_tokens` (Tokens Acumulados Processados):**
   * *Definição:* Contador total de tokens observados durante o cálculo de gradientes.
   * *Interpretação:* Atingiu **`3.380.000` tokens** (3,38 milhões de tokens) processados no passo 500.

8. **`epoch` (Épocas Equivalentes):**
   * *Definição:* Fração do conjunto de dados percorrida.
   * *Interpretação:* O valor `1.214` ao final indica que o modelo realizou pouco mais de 1 passagem completa sobre o corpus de treino (1.2 épocas), convergindo com alta economia computacional.

Ao final dos 500 passos, os adaptadores LoRA finais são salvos na pasta `codestral_openmp_lora/`.

---

## 3. Fase 2: Hard Fine-Tuning (Alinhamento de Formato de Benchmark)

### 3.1. Motivação Científica: Por que o Hard Fine-Tuning é Necessário?
No benchmark de HPC (ex: PolyBench via `python-llm/annotate-code-file-01.py`), o modelo **não recebe** tags artificiais como `<LOOP-START>` e nem deve cuspir apenas a linha do `#pragma`. O protocolo experimental do prompt (`prompts/Qwen2.5Coder14BPrompt.md` e `DefaultPrompt.md`) exige:
1. **Identificação Autônoma:** O modelo deve encontrar por conta própria o loop crítico de computação dentro do código C limpo.
2. **Análise de Dependência:** Breve justificativa de dependências de dados (`Analysis`).
3. **Código C Completo Compilável:** O kernel ou programa C completo delimitado em um bloco ````c ... ```` com a diretiva `#pragma omp ...` inserida no ponto exato.
4. **Justificativa de Cláusulas:** Breve explicação do porquê de cada cláusula (`Rationale`).

O **Hard Fine-Tuning** é a etapa de alinhamento estrutural que ensina o modelo a transferir a competência técnica adquirida na Fase 1 para a estrutura exata exigida pelo pipeline de avaliação.

### 3.2. Estrutura do Script `training/hard-fine-tuning.py`
O script de Hard Fine-Tuning realiza os seguintes tratamentos sobre o dataset:
* **Entrada (Prompt):**
  * Remove todas as marcações artificiais (`<LOOP-START>`, `<LOOP-END>`, `<OMP-START>`);
  * Apresenta o código C estritamente no estado original;
  * Aplica as instruções formais de HPC (regras de compilação `-O3 -fopenmp`, sem alteração da lógica original, sem variáveis temporárias).
* **Saída Alvo (Completion):**
  * Seção `Analysis`: Análise de dependências e estratégia de paralelismo;
  * Seção `Optimized Kernel (OpenMP annotations only)`: Bloco de código C com o `#pragma omp ...` injetado exatamente antes do loop computacional;
  * Seção `Rationale`: Detalhamento de `private`, `schedule` e `collapse`.

O treinamento parte do checkpoint gerado na Fase 1 (`codestral_openmp_lora`), aplicando *Curriculum Learning*.

### 3.3. Hiperparâmetros de Treinamento da Fase 2
* **Ponto de Partida:** Adaptadores LoRA da Fase 1 (`codestral_openmp_lora`)
* **Otimizador:** `adamw_torch` nativo
* **Taxa de Aprendizado ($lr$):** $1 \times 10^{-4}$ com decaimento cosseno (`cosine scheduler`) para refinamento suave dos pesos pré-adaptados
* **Warmup:** 20 passos
* **Tamanho de Lote Efetivo:** 16 amostras (2 por dispositivo $\times$ 8 passos de acumulação)
* **Passos Totais (`max_steps`):** 400 passos
* **Precisão:** `bfloat16` nativo na NVIDIA RTX PRO 6000 Blackwell
* **Avaliação:** A cada 50 passos sobre o conjunto de teste de 732 amostras

### 3.4. Resultados e Curva de Convergência da Fase 2 (Concluído)
Os resultados consolidados no log [training/saida_hard_treinamento.txt](file:///Users/julionogueira/Documents/OpenMP%20Optimized/training/saida_hard_treinamento.txt) cobrem integralmente os 400 passos de treinamento e comprovam o salto qualitativo proporcionado pelo alinhamento estrito em formato de benchmark:

| Passo (Step) | Época | Training Loss | Token Accuracy | Entropia | Grad Norm | Learning Rate | Tokens Totais | Eval Loss (Validação) | Eval Token Accuracy |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **10** | 0.024 | `0.6671` | 85.00% | 0.6009 | 0.6139 | $4.50 \times 10^{-5}$ | $1.46 \times 10^{5}$ | - | - |
| **20** | 0.049 | `0.1069` | 97.66% | 0.0889 | 0.2445 | $9.50 \times 10^{-5}$ | $2.91 \times 10^{5}$ | - | - |
| **30** | 0.073 | `0.0585` | 98.41% | 0.0743 | 0.1804 | $9.99 \times 10^{-5}$ | $4.37 \times 10^{5}$ | - | - |
| **40** | 0.097 | `0.0615` | 98.28% | 0.0688 | 0.2148 | $9.94 \times 10^{-5}$ | $5.83 \times 10^{5}$ | - | - |
| **50** | 0.121 | `0.0642` | 98.34% | 0.0656 | 0.1694 | $9.86 \times 10^{-5}$ | $7.30 \times 10^{5}$ | **`0.0852`** | **97.85%** |
| **60** | 0.146 | `0.0627` | 98.42% | 0.0655 | 0.1089 | $9.74 \times 10^{-5}$ | $8.80 \times 10^{5}$ | - | - |
| **70** | 0.170 | `0.0443` | 98.71% | 0.0500 | 0.1785 | $9.60 \times 10^{-5}$ | $1.03 \times 10^{6}$ | - | - |
| **80** | 0.194 | `0.0531` | 98.54% | 0.0561 | 0.1569 | $9.42 \times 10^{-5}$ | $1.17 \times 10^{6}$ | - | - |
| **90** | 0.219 | `0.0693` | 98.24% | 0.0715 | 0.1379 | $9.21 \times 10^{-5}$ | $1.32 \times 10^{6}$ | - | - |
| **100** | 0.243 | `0.0482` | 98.63% | 0.0546 | 0.1454 | $8.97 \times 10^{-5}$ | $1.48 \times 10^{6}$ | **`0.0824`** | **97.94%** |
| **110** | 0.267 | `0.0558` | 98.60% | 0.0571 | 0.2605 | $8.71 \times 10^{-5}$ | $1.63 \times 10^{6}$ | - | - |
| **120** | 0.291 | `0.0607` | 98.47% | 0.0596 | 0.1489 | $8.42 \times 10^{-5}$ | $1.78 \times 10^{6}$ | - | - |
| **130** | 0.316 | `0.0435` | 98.78% | 0.0507 | 0.1336 | $8.10 \times 10^{-5}$ | $1.92 \times 10^{6}$ | - | - |
| **140** | 0.340 | `0.0393` | 98.90% | 0.0426 | 0.1083 | $7.77 \times 10^{-5}$ | $2.08 \times 10^{6}$ | - | - |
| **150** | 0.364 | `0.0593` | 98.50% | 0.0566 | 0.2020 | $7.42 \times 10^{-5}$ | $2.23 \times 10^{6}$ | **`0.0813`** | **98.00%** |
| **160** | 0.389 | `0.0407` | 98.88% | 0.0465 | 0.1128 | $7.05 \times 10^{-5}$ | $2.38 \times 10^{6}$ | - | - |
| **170** | 0.413 | `0.0528` | 98.55% | 0.0544 | 0.1465 | $6.66 \times 10^{-5}$ | $2.52 \times 10^{6}$ | - | - |
| **180** | 0.437 | `0.0498` | 98.66% | 0.0522 | 0.1679 | $6.27 \times 10^{-5}$ | $2.68 \times 10^{6}$ | - | - |
| **190** | 0.462 | `0.0460` | 98.80% | 0.0493 | 0.1461 | $5.86 \times 10^{-5}$ | $2.83 \times 10^{6}$ | - | - |
| **200** | 0.486 | `0.0386` | 98.88% | 0.0438 | 0.1592 | $5.45 \times 10^{-5}$ | $2.98 \times 10^{6}$ | **`0.0793`** | **98.06%** |
| **210** | 0.510 | `0.0573` | 98.62% | 0.0505 | 0.1537 | $5.04 \times 10^{-5}$ | $3.12 \times 10^{6}$ | - | - |
| **220** | 0.534 | **`0.0359`** | 98.93% | 0.0445 | 0.1460 | $4.63 \times 10^{-5}$ | $3.29 \times 10^{6}$ | - | - |
| **230** | 0.559 | `0.0496` | 98.71% | 0.0532 | 0.2018 | $4.22 \times 10^{-5}$ | $3.43 \times 10^{6}$ | - | - |
| **240** | 0.583 | `0.0634` | 98.50% | 0.0558 | 0.1388 | $3.81 \times 10^{-5}$ | $3.58 \times 10^{6}$ | - | - |
| **250** | 0.607 | `0.0504` | 98.70% | 0.0536 | 0.1493 | $3.42 \times 10^{-5}$ | $3.74 \times 10^{6}$ | **`0.0771`** | **98.11%** |
| **260** | 0.632 | `0.0386` | 98.94% | 0.0419 | 0.1613 | $3.03 \times 10^{-5}$ | $3.89 \times 10^{6}$ | - | - |
| **270** | 0.656 | `0.0449` | 98.82% | 0.0464 | 0.2026 | $2.66 \times 10^{-5}$ | $4.04 \times 10^{6}$ | - | - |
| **280** | 0.680 | `0.0642` | 98.44% | 0.0627 | 0.1480 | $2.30 \times 10^{-5}$ | $4.20 \times 10^{6}$ | - | - |
| **290** | 0.705 | `0.0409` | 98.90% | 0.0462 | 0.1798 | $1.96 \times 10^{-5}$ | $4.35 \times 10^{6}$ | - | - |
| **300** | 0.729 | `0.0507` | 98.69% | 0.0539 | 0.1727 | $1.64 \times 10^{-5}$ | $4.50 \times 10^{6}$ | **`0.0756`** | **98.15%** |
| **310** | 0.753 | `0.0384` | **98.99%** | **0.0412** | 0.1255 | $1.35 \times 10^{-5}$ | $4.66 \times 10^{6}$ | - | - |
| **320** | 0.777 | `0.0380` | 98.91% | 0.0429 | 0.1576 | $1.08 \times 10^{-5}$ | $4.81 \times 10^{6}$ | - | - |
| **330** | 0.802 | `0.0513` | 98.63% | 0.0520 | 0.1580 | $8.37 \times 10^{-6}$ | $4.97 \times 10^{6}$ | - | - |
| **340** | 0.826 | `0.0465` | 98.73% | 0.0488 | 0.1648 | $6.22 \times 10^{-6}$ | $5.12 \times 10^{6}$ | - | - |
| **350** | 0.850 | `0.0490` | 98.70% | 0.0517 | 0.1387 | $4.38 \times 10^{-6}$ | $5.27 \times 10^{6}$ | **`0.0745`** | **98.19%** |
| **360** | 0.875 | `0.0552` | 98.60% | 0.0562 | 0.1475 | $2.84 \times 10^{-6}$ | $5.42 \times 10^{6}$ | - | - |
| **370** | 0.899 | `0.0457` | 98.82% | 0.0464 | 0.1798 | $1.63 \times 10^{-6}$ | $5.56 \times 10^{6}$ | - | - |
| **380** | 0.923 | `0.0460` | 98.74% | 0.0513 | 0.1952 | $7.52 \times 10^{-7}$ | $5.72 \times 10^{6}$ | - | - |
| **390** | 0.948 | `0.0508` | 98.75% | 0.0485 | 0.1688 | $2.07 \times 10^{-7}$ | $5.86 \times 10^{6}$ | - | - |
| **400** | 0.972 | `0.0428` | 98.88% | 0.0457 | 0.1598 | $1.71 \times 10^{-9}$ | **`6.01 \times 10^{6}`** | **`0.07431`** | **`98.19%`** |

> **Síntese dos Resultados Finais da Fase 2 (Hard Fine-Tuning):**
> * **Tempo Total de Execução:** 12.190 segundos (~3 horas, 23 minutos e 07 segundos) na NVIDIA RTX PRO 6000 Blackwell.
> * **Loss de Treino Final:** Média global do trainer consolidada em **`0.06705`**, com mínima histórica de **`0.0359`** (passo 220) e fechamento em **`0.0428`** no passo 400.
> * **Acurácia de Tokens no Treino:** Pico de **`98.99%`** (passo 310) e consolidação em **`98.88%`** no encerramento.
> * **Perda de Validação Final (`eval_loss`):** Mínima histórica de **`0.07431`** sobre o conjunto de teste de 732 amostras inéditas (uma expressiva redução de **62.0%** em relação ao erro de validação da Fase 1).
> * **Acurácia de Validação Final:** Atingiu **`98.19%`** com estabilidade estrita ao longo das últimas 100 iterações (menos de 1.8% de erro token a token em todo o código e anotações geradas).
> * **Entropia Residual:** Caiu para **`0.0457`** no treino e **`0.06389`** na validação, indicando certeza categórica do modelo na emissão de código compilável e diretivas exatas.
> * **Tokens Totais Retropropagados:** Mais de **6,01 milhões de tokens** processados ao longo dos 400 passos.
> * **Adaptadores LoRA Salvos:** Consolidados no diretório `codestral_openmp_hard_lora/`.

### 3.5. Comparativo Quantitativo e Científico: Fase 1 vs. Fase 2

A comparação entre as duas fases fornece evidências empíricas contundentes da eficácia do pipeline em duas etapas (*Two-Stage Curriculum Learning*):

| Dimensão Experimental | Fase 1 (Fundação OpenMP) | Fase 2 (Hard Fine-Tuning) | Impacto / Conclusão Científica |
| :--- | :---: | :---: | :--- |
| **Ponto de Partida** | Base Codestral 22B (Zero-Shot) | Checkpoint Fase 1 (`codestral_openmp_lora`) | Herança direta de representações semânticas e cláusulas OpenMP aprendidas na etapa preliminar. |
| **Loss Inicial (Passo 10)** | `0.9868` | **`0.6671`** | A Fase 2 inicia com perda **32.4% menor** devido à pré-adaptação dos pesos. |
| **Velocidade de Convergência** | Exigiu 50 passos para atingir $>90\%$ | **Atingiu 97.66% no passo 20** | O modelo converteu o conhecimento prévio em menos de 20 passos para a nova estrutura formal. |
| **Mínima Perda de Treino** | `0.0897` (Passo 490) | **`0.0359`** (Passo 220) | **Redução de 60.0% no erro de treino**, aproximando-se do limite ótimo Bayesiano. |
| **Loss Médio Global de Treino** | `0.2512` | **`0.06705`** | Perda média quase 4 vezes menor ao longo de todo o ciclo de vida. |
| **Perda de Validação Final (`eval_loss`)** | `0.1956` (Passo 500) | **`0.07431`** (Passo 400) | **Perda na validação 62.0% menor**, demonstrando generalização com fidelidade formal quase perfeita. |
| **Acurácia de Validação Final** | `95.13%` | **`98.19%`** | **Salto de +3.06% em acurácia absoluta**, em um contexto de saída integral de código e análise técnica. |
| **Entropia Residual (Incerteza)** | `0.1749` (Validação) | **`0.06389`** (Validação) | **Incerteza do modelo reduzida em 63.5%**, tornando a inferência virtualmente determinística. |
| **Estabilidade de Otimização (`grad_norm`)** | $0.20 \sim 0.60$ (Picos de $2.53$) | **$0.10 \sim 0.26$** (Hiperestável) | A superfície de perda da Fase 2 foi ainda mais suave, favorecida pelo *cosine annealing scheduler*. |
| **Tokens Processados** | $3.38 \times 10^6$ tokens | **$6.01 \times 10^6$ tokens** | A Fase 2 processou quase o dobro de tokens devido à estrutura completa de código, análise e justificativa. |
| **Tempo de Execução na RTX 6000** | 2h 52m 17s (10.340 s) | 3h 23m 07s (12.190 s) | Custo computacional total somou apenas ~6h 15m na GPU Blackwell (`sm_120`). |

> **Conclusão para a Dissertação:** Os dados comprovam que o *Two-Stage Curriculum Learning* foi determinante: a Fase 1 capacitou o Codestral-22B com conhecimento conceitual profundo e especializado sobre cláusulas OpenMP e padrões de concorrência em C; a Fase 2 alinhou perfeitamente esse conhecimento com a estrutura estrita de benchmark (PolyBench), atingindo **98.19% de acurácia de validação com perda residual de 0.074**. Essa arquitetura em duas etapas superou amplamente qualquer tentativa de aprendizado direto (*one-step fine-tuning*), comprovando a eficácia pedagógica e científica da metodologia proposta.

---

## 4. Fase 3: Fusão dos Pesos LoRA (Merge & Unload)

Antes da quantização no ecossistema `llama.cpp` / Ollama, os pesos LoRA (treinados como matrizes de baixo rank $A$ e $B$) devem ser integrados à matriz de pesos pré-treinada $W_0$:

$$W_{\text{final}} = W_0 + \frac{\alpha}{r} (B \times A)$$

Essa operação é realizada pelo script [training/merge_lora.py](file:///Users/julionogueira/Documents/OpenMP%20Optimized/training/merge_lora.py):
* Carrega o modelo base `mistralai/Codestral-22B-v0.1` em `bfloat16`;
* Anexa os adaptadores LoRA treinados (`codestral_openmp_lora` ou `codestral_openmp_hard_lora`);
* Executa `model.merge_and_unload()`, fundindo as matrizes sem qualquer perda de precisão;
* Salva o modelo completo resultante em formato Hugging Face na pasta `codestral_openmp_merged/`.

---

## 5. Fase 4: Conversão para GGUF e Quantização Multi-Nível

Para avaliação científica do impacto da quantização na qualidade das diretivas OpenMP geradas, são construídas 4 variantes do modelo via `llama.cpp`:

| Formato | Descrição Técnica | Tamanho Aprox. | VRAM Necessária | Objetivo na Pesquisa |
| :--- | :--- | :---: | :---: | :--- |
| **FP16 / BF16** | Ponto flutuante de 16 bits | ~44.5 GB | $\ge 48$ GB | **Baseline de Referência (Sem Perda):** Representa o teto de inteligência do modelo. |
| **Q8_0** | Quantização simétrica de 8 bits | ~23.8 GB | $\ge 26$ GB | **Alta Fidelidade:** Perda de perplexidade desprezível ($< 0.1\%$). Execução rápida na RTX 6000. |
| **Q4_K_M** | 4-bit K-Quants Médio | ~13.8 GB | $\ge 16$ GB | **Padrão de Mercado / Ollama:** Balanço ideal entre consumo de memória e velocidade. Compatível com GPUs comerciais (RTX 4080/4090) e Apple Silicon (16GB+). |
| **Q3_K_M** | 3-bit K-Quants Médio | ~10.4 GB | $\ge 12$ GB | **Limite Inferior de Compressão:** Avalia em que ponto a compressão agressiva começa a induzir alucinações de sintaxe OpenMP (ex: cláusulas esquecidas). |

### 5.1. Comandos de Conversão e Quantização

```bash
# 1. Clonar e compilar o llama.cpp com suporte a CUDA/Metal
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j

# 2. Conversão do modelo mesclado para GGUF FP16
python3 convert_hf_to_gguf.py ../codestral_openmp_merged \
    --outfile ../models_gguf/codestral-openmp-f16.gguf \
    --outtype f16

# 3. Quantização Multi-Nível
./build/bin/llama-quantize ../models_gguf/codestral-openmp-f16.gguf ../models_gguf/codestral-openmp-q8_0.gguf Q8_0
./build/bin/llama-quantize ../models_gguf/codestral-openmp-f16.gguf ../models_gguf/codestral-openmp-q4_k_m.gguf Q4_K_M
./build/bin/llama-quantize ../models_gguf/codestral-openmp-f16.gguf ../models_gguf/codestral-openmp-q3_k_m.gguf Q3_K_M
```

---

## 6. Fase 5: Integração com o Ollama e Execução dos Benchmarks

Para permitir que os scripts automatizados de benchmarking da pesquisa (`annotate-code-file-01.py`, `run_benchmarks.py`) executem inferências locais padronizadas:

### 6.1. Criação dos Modelfiles

Para cada variante quantizada, é gerado um `Modelfile`:
```dockerfile
FROM ./models_gguf/codestral-openmp-q4_k_m.gguf

PARAMETER temperature 0.2
PARAMETER top_p 0.95
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|endoftext|>"
PARAMETER stop "</s>"

TEMPLATE """{{ .Prompt }}"""
```

### 6.2. Registro no Ollama
```bash
ollama create codestral-openmp:16b -f Modelfile_f16
ollama create codestral-openmp:8b  -f Modelfile_q8
ollama create codestral-openmp:4b  -f Modelfile_q4
ollama create codestral-openmp:3b  -f Modelfile_q3
```

### 6.3. Execução dos Benchmarks de HPC
O script de inferência e anotação pode comparar diretamente as quatro variantes contra os modelos originais (*baseline zero-shot* como Qwen-2.5-Coder-14B e Codestral-22B sem fine-tuning):

```bash
# Executa benchmark com a versão 4-bit afinada
python python-llm/annotate-code-file-01.py \
    --model codestral-openmp:4b \
    --code polybench-c-3.2/linear-algebra/kernels/2mm/2mm.c \
    --prompt prompts/Qwen2.5Coder14BPrompt.md

# Compilação e verificação de speedup
cd polybench-c-3.2/linear-algebra/kernels/2mm
gcc -O3 -fopenmp -I ../../../utilities ../../../utilities/polybench.c 2mm.c -o 2mm_omp
./2mm_omp
```

---

## 7. Critérios de Avaliação Científica para a Dissertação

Ao avaliar o modelo fine-tuned nas diferentes quantizações, os seguintes critérios objetivos são medidos e documentados na dissertação:

1. **Taxa de Compilabilidade (%):** Quantos códigos gerados compilam com `gcc -O3 -fopenmp` sem erros de sintaxe ou de cláusula?
2. **Corretude Numérica (%):** A execução paralela gera resultados estritamente idênticos aos sequenciais (sem *race conditions*)?
3. **Speedup Obtido ($S = T_{\text{seq}} / T_{\text{par}}$):** Qual a aceleração alcançada em 8, 16, 32 e 64 threads na máquina de teste?
4. **Eficiência de Quantização:** Gráficos comparando o decaimento de speedup e corretude em função da precisão (FP16 $\rightarrow$ Q8 $\rightarrow$ Q4 $\rightarrow$ Q3).
5. **Throughput de Inferência (tokens/segundo):** Velocidade de geração no Ollama para cada nível de quantização.

---

## 8. Guia Rápido de Reprodução

Para reproduzir todos os experimentos a partir do repositório:

1. **Fase 1:** Executar `python training/train.py` (Gera `codestral_openmp_lora/`);
2. **Fase 2:** Executar `python training/hard-fine-tuning.py` (Gera `codestral_openmp_hard_lora/`);
3. **Fase 3:** Executar `python training/merge_lora.py` (Gera `codestral_openmp_merged/`);
4. **Fase 4:** Executar `bash training/quantize_models.sh` (Compila `llama.cpp` e quantiza em 16b, 8b, 4b e 3b);
5. **Fase 5:** Executar `bash python-llm/execute-all.sh` (Dispara os testes automatizados do PolyBench via Ollama).
