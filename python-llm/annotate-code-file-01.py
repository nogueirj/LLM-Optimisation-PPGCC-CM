import sys
import os
import re
import json
import time
import urllib.request
import urllib.error

def extract_c_code(text):
    """
    Extracts pure C code from the LLM response, removing markdown, explanations, and thinking.
    Prefers complete C source files over tiny 1-line snippets.
    """
    code_blocks = re.findall(r'```(?:c|cpp|C)?\s*\n(.*?)```', text, re.DOTALL)
    if code_blocks:
        candidates = []
        for block in code_blocks:
            clean_block = block.strip()
            num_lines = len(clean_block.splitlines())
            num_chars = len(clean_block)
            
            # Skip tiny snippets like `gcc -fopenmp ...` or `#include <omp.h>`
            if num_lines < 3 or num_chars < 50:
                continue

            score = 0
            if '#include' in clean_block:
                score += 30
            if 'polybench' in clean_block.lower():
                score += 25
            if 'main' in clean_block:
                score += 30
            if 'kernel_' in clean_block or 'init_array' in clean_block:
                score += 20
            if '#pragma omp' in clean_block:
                score += 25
            if 'for (' in clean_block or 'for(' in clean_block:
                score += 15

            # Size score: prefer larger, complete blocks over small fragments
            score += min(num_lines, 200)

            candidates.append((score, num_chars, clean_block))

        if candidates:
            candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
            return candidates[0][2]

        # If all blocks were < 3 lines, just take the longest one
        code_blocks.sort(key=lambda b: len(b), reverse=True)
        return code_blocks[0].strip()

    # Fallback: if no markdown fences, search for where C code starts
    lines = text.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('/*', '/**', '#include', '#pragma', 'static void', 'void ', 'int ')):
            start_idx = i
            break
    
    code = '\n'.join(lines[start_idx:])
    return code.strip()

def format_metrics(response, model, code_file, prompt_file, raw_content):
    total_duration = response.get('total_duration')
    load_duration = response.get('load_duration')
    prompt_eval_count = response.get('prompt_eval_count')
    prompt_eval_duration = response.get('prompt_eval_duration')
    eval_count = response.get('eval_count')
    eval_duration = response.get('eval_duration')
    created_at = response.get('created_at', 'N/A')

    total_s = f"{total_duration / 1e9:.2f} s" if total_duration else "N/A"
    load_s = f"{load_duration / 1e9:.2f} s" if load_duration else "N/A"
    prompt_eval_s = f"{prompt_eval_duration / 1e9:.2f} s" if prompt_eval_duration else "N/A"
    eval_s = f"{eval_duration / 1e9:.2f} s" if eval_duration else "N/A"
    
    prompt_rate = f"{prompt_eval_count / (prompt_eval_duration / 1e9):.2f} tokens/s" if (prompt_eval_count and prompt_eval_duration) else "N/A"
    eval_rate = f"{eval_count / (eval_duration / 1e9):.2f} tokens/s" if (eval_count and eval_duration) else "N/A"

    report = [
        "=" * 80,
        "OLLAMA EXECUTION METRICS & VERBOSE LOG",
        "=" * 80,
        f"Model:                {model}",
        f"Code File:            {code_file}",
        f"Prompt File:          {prompt_file}",
        f"Timestamp:            {created_at}",
        "",
        "-" * 80,
        "Performance Metrics",
        "-" * 80,
        f"Total Duration:       {total_s}",
        f"Load Duration:        {load_s}",
        f"Prompt Eval Count:    {prompt_eval_count if prompt_eval_count is not None else 'N/A'} tokens",
        f"Prompt Eval Duration: {prompt_eval_s}",
        f"Prompt Eval Rate:     {prompt_rate}",
        f"Eval Count:           {eval_count if eval_count is not None else 'N/A'} tokens",
        f"Eval Duration:        {eval_s}",
        f"Generation Rate:      {eval_rate}",
        "",
        "-" * 80,
        "Raw Response (including analysis, thinking, and explanations)",
        "-" * 80,
        raw_content,
        "=" * 80
    ]
    return "\n".join(report)

def process_code_with_llm(code_file_path, llm_model, prompt_template, host="http://localhost:11434"):
    """
    Reads code from a file and processes it using Ollama REST API with streaming output and keep_alive.
    """
    try:
        with open(code_file_path, 'r') as file:
            code_content = file.read()
    except FileNotFoundError:
        print(f"[-] Error: Code file '{code_file_path}' not found.")
        return "", {}

    # Smart injection of code into prompt template
    if "{code}" in prompt_template:
        prompt = prompt_template.replace("{code}", code_content)
    else:
        empty_block = re.search(r'```(?:c|cpp|C)?\s*\n\s*```\s*$', prompt_template)
        if empty_block:
            prompt = prompt_template[:empty_block.start()] + "```c\n" + code_content + "\n```"
        else:
            prompt = prompt_template.rstrip() + "\n\n```c\n" + code_content + "\n```"

    print(f"[*] Connecting to Ollama ({llm_model})...")
    print(f"[*] (Generating code, keeping model loaded in RAM with keep_alive='1h')...\r", end="", flush=True)

    url = f"{host}/api/chat"
    payload = {
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "keep_alive": "1h",
        "options": {
            "num_ctx": 4096,
            "num_predict": 4096,
            "temperature": 1.0,
            "top_p": 0.95
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )

    try:
        full_content = []
        token_count = 0
        final_metadata = {}

        with urllib.request.urlopen(req) as response:
            for line in response:
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode('utf-8'))
                except json.JSONDecodeError:
                    continue

                msg = chunk.get('message', {})
                content_piece = msg.get('content', '') if isinstance(msg, dict) else ''

                if content_piece:
                    full_content.append(content_piece)
                    token_count += 1
                    if token_count % 15 == 0:
                        print(f"[*] Generating code... ({token_count} tokens generated)\r", end="", flush=True)

                if chunk.get('done', False):
                    final_metadata = chunk

        print(f"\n[+] Finished generation ({token_count} tokens received).")
        raw_response = "".join(full_content)
        return raw_response, final_metadata

    except KeyboardInterrupt:
        print("\n[!] Execution interrupted by user (Ctrl+C).")
        sys.exit(130)
    except urllib.error.URLError as e:
        print(f"\n[-] Error connecting to Ollama: {e}")
        print("[-] Make sure Ollama is running ('ollama serve' or Ollama app).")
        return "", {}
    except Exception as e:
        print(f"\n[-] Error during Ollama inference: {e}")
        return "", {}

if __name__ == "__main__":
    import argparse

    # Flexible parser supporting both named flags (--model, --code, ...) and positional arguments
    parser = argparse.ArgumentParser(description="Annotate C code using an Ollama LLM.")
    parser.add_argument("pos_args", nargs="*", help="Positional: <model> <code_file> <prompt_file> [output_file]")
    parser.add_argument("--model", "-m", help="Name of the Ollama model")
    parser.add_argument("--code", "-c", help="Path to input C code file")
    parser.add_argument("--prompt", "-p", help="Path to prompt markdown file")
    parser.add_argument("--output", "-o", help="Path to save annotated C output file")

    args = parser.parse_args()

    model = args.model
    code_file = args.code
    prompt_file = args.prompt
    output_file = args.output

    # Fallback to positional arguments if flags were not provided
    if args.pos_args:
        if len(args.pos_args) >= 1 and not model:
            model = args.pos_args[0]
        if len(args.pos_args) >= 2 and not code_file:
            code_file = args.pos_args[1]
        if len(args.pos_args) >= 3 and not prompt_file:
            prompt_file = args.pos_args[2]
        if len(args.pos_args) >= 4 and not output_file:
            output_file = args.pos_args[3]

    if not model or not code_file or not prompt_file:
        print("Usage:")
        print("  python", sys.argv[0], "<model> <code_file> <prompt_file> [output_file]")
        print("  python", sys.argv[0], "--model <model> --code <code_file> --prompt <prompt_file> [--output <output_file>]")
        print("\nExample:")
        print("  python", sys.argv[0], "codestral-openmp:3b polybench-c-3.2/linear-algebra/kernels/2mm/2mm.c prompts/DefaultPrompt.md models/codestral/2mm/2mm.c")
        sys.exit(1)

    # Auto-generate output filename if not given
    if not output_file:
        base_name = os.path.splitext(os.path.basename(code_file))[0]
        model_clean = re.sub(r'[:/]', '_', model)
        output_file = f"models/{model_clean}/{base_name}/{base_name}.c"

    try:
        with open(prompt_file, 'r') as pf:
            prompt_template = pf.read()
    except FileNotFoundError:
        print(f"[-] Error: Prompt file '{prompt_file}' not found.")
        sys.exit(1)

    print("=" * 60)
    print(f"Model:       {model}")
    print(f"Code File:   {code_file}")
    print(f"Prompt File: {prompt_file}")
    print(f"Output File: {output_file}")
    print("=" * 60)

    raw_response, metadata = process_code_with_llm(code_file, model, prompt_template)

    if not raw_response:
        print("[-] No response received from model. Skipping save.")
        sys.exit(1)

    # 1. Extract pure C code and ensure output directory exists
    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    c_code = extract_c_code(raw_response)
    with open(output_file, "w") as f:
        f.write(c_code + "\n")
    print(f"[+] Saved pure C code to: {output_file}")

    # 2. Save verbose metadata and raw reasoning to a separate .txt file
    verbose_file = os.path.splitext(output_file)[0] + "_verbose.txt"
    metrics_report = format_metrics(metadata, model, code_file, prompt_file, raw_response)
    with open(verbose_file, "w") as f:
        f.write(metrics_report + "\n")
    print(f"[+] Saved metrics & verbose log to: {verbose_file}")
    print("-" * 60)
