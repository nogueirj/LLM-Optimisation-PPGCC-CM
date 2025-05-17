import os
import requests
import sys

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python request_gpt.py <API_URL> <ARQUIVO_CODIGO> <PROMPT> <MODELO>")
        sys.exit(1)

    if len(sys.argv[1]) < 5:
            print("URL da API não é válida")
            sys.exit(1)
    if len(sys.argv[2]) < 5:
        print("Arquivo de código não é válido")
        sys.exit(1)
    if len(sys.argv[3]) < 5:
        print("Prompt não é válido")
        sys.exit(1)
    if len(sys.argv[4]) < 5:
        print("Modelo não é válido")
        sys.exit(1)


    api_url = sys.argv[1]
    arquivo_codigo = sys.argv[2]
    prompt_desejado = sys.argv[3]
    modelo = sys.argv[4]

    with open(arquivo_codigo, "r") as file:
        codigo_original = file.read()

    if len(prompt_desejado) < 5:
        print("Prompt informado não é válido")
        sys.exit(1)

    headers = {
        "Content-Type": "application/json"
    }

    # Código a ser otimizado
    codigo_fonte = codigo_original

    # Prompt personalizado
    prompt = f"{prompt_desejado}:\n\n```c\n{codigo_fonte}\n```"

    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False  # Define se a resposta será enviada em partes ou completa
    }

    response = requests.post(api_url, json=data, headers=headers)
    resposta = response.json()

    # Tratar a resposta
    if "error" in resposta:
        print("Erro na resposta da API:", resposta["error"])
        sys.exit(1)
    if "response" not in resposta:
        print("Erro: Resposta não contém o campo 'response'")
        sys.exit(1)
    if "c" not in resposta["response"]:
        print("Erro: Resposta não contém o código otimizado")
        sys.exit(1)

    # Extrai o código otimizado da resposta
    codigo_otimizado = resposta["response"].split("```c")[1].split("```")[0].strip()
    print("Código otimizado:\n", codigo_otimizado)

    # Define o caminho do arquivo otimizado
    caminho_base = arquivo_codigo.split("polybench")[0]
    caminho_diretorio = os.path.join(caminho_base, "Codigo Otimizados", modelo.split(":")[0])
    nome_arquivo = os.path.basename(arquivo_codigo).split(".")[0] + "_otimizado.c"
    caminhoArquivoOtimizado = os.path.join(caminho_diretorio, nome_arquivo)

    # Cria os diretórios necessários
    os.makedirs(caminho_diretorio, exist_ok=True)

    # Salva o código otimizado em um novo arquivo
    with open(caminhoArquivoOtimizado, "w") as file:
        file.write(codigo_otimizado)
    print(f"Código otimizado salvo em: {caminhoArquivoOtimizado}")

    # Exibe a resposta completa
    print("Resposta completa da API:")
    print(resposta["response"])