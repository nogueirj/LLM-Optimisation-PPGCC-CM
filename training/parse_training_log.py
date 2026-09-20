#!/usr/bin/env python3
import sys
import re
import ast
import json

def fmt_sci(val):
    try:
        f = float(val)
        if f == 0:
            return "$0$"
        s = f"{f:.2e}"
        mantissa, exp = s.split("e")
        exp = int(exp)
        return f"${mantissa} \\times 10^{{{exp}}}$"
    except Exception:
        return str(val)

def parse_log(log_file_path):
    """
    Analisa o arquivo de log do treinamento (saida_hard_treinamento.txt ou saidatreinamento.txt)
    e gera automaticamente uma tabela formatada em Markdown pronta para o documento de metodologia.
    """
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[-] Erro: Arquivo de log '{log_file_path}' não encontrado!")
        sys.exit(1)

    dict_pattern = re.compile(r"\{[^{}]*(?:'loss'|'eval_loss')[^{}]*\}")
    matches = dict_pattern.findall(content)

    train_logs = []
    eval_logs = []

    for match in matches:
        try:
            data = ast.literal_eval(match)
            if "loss" in data and "eval_loss" not in data:
                train_logs.append(data)
            elif "eval_loss" in data:
                eval_logs.append(data)
        except Exception:
            continue

    if not train_logs:
        print("[-] Nenhum log de treinamento encontrado no arquivo.")
        sys.exit(0)

    print("\n" + "=" * 100)
    print(f"TABELA GERADA AUTOMATICAMENTE A PARTIR DE: {log_file_path}")
    print("=" * 100 + "\n")

    header = (
        "| Passo (Step) | Época | Training Loss | Token Accuracy | Entropia | Grad Norm | "
        "Learning Rate | Tokens Totais | Eval Loss (Validação) | Eval Token Accuracy |\n"
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    )
    print(header)

    eval_idx = 0
    for i, log in enumerate(train_logs):
        step = (i + 1) * 10
        epoch = float(log.get("epoch", 0))
        loss = log.get("loss", "N/A")
        acc = f"{float(log.get('mean_token_accuracy', 0)) * 100:.2f}%" if "mean_token_accuracy" in log else "N/A"
        entropy = log.get("entropy", "N/A")
        grad_norm = log.get("grad_norm", "N/A")
        lr = fmt_sci(log.get("learning_rate", "N/A"))
        tokens = fmt_sci(log.get("num_tokens", "N/A"))

        eval_loss = "-"
        eval_acc = "-"
        if step % 50 == 0 and eval_idx < len(eval_logs):
            e_data = eval_logs[eval_idx]
            eval_loss = f"**`{e_data.get('eval_loss', 'N/A')}`**"
            if "eval_mean_token_accuracy" in e_data:
                eval_acc = f"**{float(e_data['eval_mean_token_accuracy']) * 100:.2f}%**"
            eval_idx += 1

        print(f"| **{step}** | {epoch:.3f} | `{loss}` | {acc} | {entropy} | {grad_norm} | {lr} | {tokens} | {eval_loss} | {eval_acc} |")

    print("\n" + "=" * 100)
    print("Basta copiar as linhas acima e colar na seção correspondente do METODOLOGIA_FINE_TUNING_E_QUANTIZACAO.md!")
    print("=" * 100 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log_file = "saida_hard_treinamento.txt"
    else:
        log_file = sys.argv[1]
    parse_log(log_file)
