#!/bin/bash -xe


PROMPT="Consegue anotar o código fornecido com diretivas OpenMP."

for model in $(ollama list | awk ' { print $1 }'| sed -e '1d'); do
  echo "Executing with model: $model"
  python annotate-code-file.py ${model} gemm.c "${PROMPT}"
done
