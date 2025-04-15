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


