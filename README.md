# Experimentos para o artigo PAPER GENIA.

Link para o Artigo: [`Uso de IA Generativa na Geração de Código Paralelo para Arquiteturas Heterogêneas`](https://pt.overleaf.com/project/67dc14860cf4074a0dd5d508)

## TODO

### Reunião: 20/03/2025

1. Fornecer o Código Original/Sequencial e pedir para gerar o Código com as diretivas `OpenMP` para comparar com o mesmo benchmark no `Polybench-ACC/OpenMP` feito por humano.

2. Analisar o código gerado se utiliza diretivas mais recentes, por exemplo, construtores para laços, construtor `FOR` é mais antigo e `TASKLOOP` mais recente.

3. Pedir para gerar código `OpenMP` para `GPU`, construtor `target` que gera código para `GPU` pelo `GCC`, sem a necessidade de saber `CUDA`. Comparar com o `Polybench-GPU`



## Ferramentas

```bash
https://ollama.com/
https://github.com/open-webui/open-webui

```


