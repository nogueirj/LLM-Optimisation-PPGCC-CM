import sys
import os
import re
import json
import time
import urllib.request
import urllib.error

def extract_kernel_function(code_str):
    """
    Finds `static void kernel_<name>(...) { ... }` using brace balancing.
    Returns (start_idx, end_idx, func_text) or None.
    """
    m = re.search(r'static\s+void\s+kernel_\w+\s*\(', code_str)
    if not m:
        return None
    start = m.start()
    brace_start = code_str.find('{', m.end())
    if brace_start == -1:
        return None
    depth = 0
    for idx in range(brace_start, len(code_str)):
        if code_str[idx] == '{':
            depth += 1
        elif code_str[idx] == '}':
            depth -= 1
            if depth == 0:
                return (start, idx + 1, code_str[start:idx + 1])
    return None


def sanitize_kernel_function(k_text):
    """
    Cleans up common quantized-LLM pragma artifacts inside `kernel_*`:
    - Removes non-OpenMP / non-scop pragmas (e.g. `#pragma vector always`).
    - Collapses consecutive `#pragma omp` lines that have no C statement between them.
    """
    lines = k_text.splitlines()
    cleaned = []
    for line in lines:
        s = line.strip()
        if s.startswith('#pragma') and not (
            s.startswith('#pragma omp')
            or s.startswith('#pragma scop')
            or s.startswith('#pragma endscop')
        ):
            continue
        if s.startswith('#pragma omp'):
            while cleaned and cleaned[-1].strip().startswith('#pragma omp'):
                cleaned.pop()
        if s.startswith('#pragma scop') and cleaned and cleaned[-1].strip().startswith('#pragma omp'):
            omp_line = cleaned.pop()
            cleaned.append(line)
            cleaned.append(omp_line)
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def _score_c_candidate(block):
    clean_block = block.strip()
    # Remove placeholder lines echoed from old prompts
    lines = [
        ln for ln in clean_block.splitlines()
        if '<The entire, complete C source code' not in ln
        and ln.strip() not in ('c', 'cpp', 'C')
    ]
    clean_block = '\n'.join(lines).strip()
    if clean_block.startswith('<stdio.h>'):
        clean_block = '#include ' + clean_block

    num_lines = len(clean_block.splitlines())
    num_chars = len(clean_block)
    if num_lines < 3 or num_chars < 50:
        return None

    score = 0
    if '#include' in clean_block:
        score += 30
    if 'polybench' in clean_block.lower():
        score += 25
    if 'main' in clean_block:
        score += 30
    if 'kernel_' in clean_block:
        score += 60
    if 'init_array' in clean_block:
        score += 20
    if '#pragma omp' in clean_block:
        score += 25
    if 'for (' in clean_block or 'for(' in clean_block:
        score += 15
    score += min(num_lines, 200)
    return (score, num_chars, clean_block)


def extract_c_code(text, original_code=None):
    """
    Extracts pure C code from the LLM response, removing markdown, explanations, and thinking.
    Resilient against inverted Markdown fence parity (e.g. stray ``` before the main block).
    When `original_code` is provided, splices only the annotated `kernel_*` function into
    `original_code` so headers, `init_array`, `print_array`, and `main()` remain 100% intact.
    """
    candidates = []

    # 1. Standard paired fence regex
    for block in re.findall(r'```(?:c|cpp|C)?\s*\n(.*?)```', text, re.DOTALL):
        scored = _score_c_candidate(block)
        if scored:
            candidates.append(scored)

    # 2. Fence-split segments (immune to odd/inverted fence parity like a stray opening ```)
    for segment in re.split(r'(?m)^\s*```[a-zA-Z]*\s*$', text):
        scored = _score_c_candidate(segment)
        if scored:
            candidates.append(scored)

    best_code = None
    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_code = candidates[0][2]
    else:
        # Fallback: search for where C code starts
        lines = text.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('/*', '/**', '#include', '#pragma', 'static void', 'void ', 'int ')):
                start_idx = i
                break
        best_code = '\n'.join(lines[start_idx:]).strip()
        if best_code.startswith('<stdio.h>'):
            best_code = '#include ' + best_code

    # 3. Surgical Kernel Injection: transplant the annotated `kernel_*` function into `original_code`
    if original_code and best_code:
        k_llm = extract_kernel_function(best_code)
        k_orig = extract_kernel_function(original_code)
        if k_llm and k_orig:
            sanitized_k = sanitize_kernel_function(k_llm[2])
            # Verify C token integrity inside kernel_* (ignoring #pragma lines)
            no_p_llm = re.sub(r'(?m)^\s*#pragma\s+.*$', '', sanitized_k)
            no_p_orig = re.sub(r'(?m)^\s*#pragma\s+.*$', '', k_orig[2])
            if re.findall(r'\w+|[^\w\s]', no_p_llm) == re.findall(r'\w+|[^\w\s]', no_p_orig):
                reconstructed = (
                    original_code[:k_orig[0]]
                    + sanitized_k
                    + original_code[k_orig[1]:]
                )
                return reconstructed.strip()

        # 4. Loop-Aligned Pragma Transplantation: if the model returned only #pragma scop..endscop
        # or slightly altered loop headers/braces, map its #pragma omp lines onto the exact loops of original_code
        transplanted = transplant_pragmas_to_original(best_code, original_code)
        if transplanted:
            return transplanted.strip()

    return best_code


def _extract_scop_or_kernel_loops(code_text):
    """
    Extracts a list of (loop_var, pragma_line_or_None) for each `for (...)` loop
    inside `#pragma scop ... #pragma endscop` or `kernel_*`.
    """
    region = code_text
    m_scop = re.search(r'#pragma\s+scop\b(.*?)#pragma\s+endscop\b', code_text, re.DOTALL)
    if m_scop:
        region = m_scop.group(1)
    else:
        k_fn = extract_kernel_function(code_text)
        if k_fn:
            region = k_fn[2]

    loops = []
    pending_pragma = None
    for line in region.splitlines():
        s = line.strip()
        if s.startswith('#pragma omp'):
            pending_pragma = s
        else:
            m_for = re.match(r'for\s*\(\s*(?:int\s+)?([A-Za-z_]\w*)\s*=', s)
            if m_for:
                loops.append((m_for.group(1), pending_pragma))
                pending_pragma = None
    return loops


def transplant_pragmas_to_original(llm_code, orig_code):
    """
    Maps `#pragma omp` directives associated with `for` loops in `llm_code`
    directly onto the corresponding `for` loops inside `#pragma scop ... #pragma endscop`
    of `orig_code`, keeping 100% of `orig_code` C tokens intact.
    """
    from collections import defaultdict

    llm_loops = _extract_scop_or_kernel_loops(llm_code)
    if not llm_loops or not any(p for _, p in llm_loops):
        return None

    m_scop = re.search(r'(#pragma\s+scop\b)(.*?)(#pragma\s+endscop\b)', orig_code, re.DOTALL)
    if not m_scop:
        return None

    scop_body = m_scop.group(2)
    orig_lines = scop_body.splitlines()
    orig_for_indices = []
    for idx, ln in enumerate(orig_lines):
        m_for = re.match(r'^\s*for\s*\(\s*(?:int\s+)?([A-Za-z_]\w*)\s*=', ln)
        if m_for:
            orig_for_indices.append((idx, m_for.group(1)))

    pragma_by_orig_line = {}
    if len(llm_loops) == len(orig_for_indices):
        for (_, pragma), (o_idx, _) in zip(llm_loops, orig_for_indices):
            if pragma:
                pragma_by_orig_line[o_idx] = pragma
    else:
        orig_by_var = defaultdict(list)
        for o_idx, o_var in orig_for_indices:
            orig_by_var[o_var].append(o_idx)
        seen_var = defaultdict(int)
        for l_var, pragma in llm_loops:
            occ = seen_var[l_var]
            seen_var[l_var] += 1
            if pragma and occ < len(orig_by_var[l_var]):
                pragma_by_orig_line[orig_by_var[l_var][occ]] = pragma

    if not pragma_by_orig_line:
        return None

    new_scop_lines = []
    for idx, ln in enumerate(orig_lines):
        if idx in pragma_by_orig_line:
            indent = re.match(r'^(\s*)', ln).group(1)
            new_scop_lines.append(f"{indent}{pragma_by_orig_line[idx]}")
        new_scop_lines.append(ln)

    new_scop_body = '\n'.join(new_scop_lines) + '\n'
    return orig_code[:m_scop.start(2)] + new_scop_body + orig_code[m_scop.end(2):]

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
        prompt = prompt_template.replace("{code}", code_content.strip())
    else:
        empty_block = re.search(r'```(?:c|cpp|C)?\s*\n\s*```\s*$', prompt_template)
        if empty_block:
            prompt = prompt_template[:empty_block.start()] + "```c\n" + code_content + "\n```"
        else:
            prompt = prompt_template.rstrip() + "\n\n```c\n" + code_content + "\n```"

    print(f"[*] Connecting to Ollama ({llm_model})...")
    print(f"[*] (Generating code, keeping model loaded in RAM with keep_alive='5m')...\r", end="", flush=True)

    url = f"{host}/api/chat"
    payload = {
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "keep_alive": "5m",
        "options": {
            "num_ctx": 8192,
            "num_predict": 4096,
            "temperature": 0.1,
            "top_p": 0.95,
            "repeat_penalty": 1.1
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

                if 'error' in chunk:
                    print(f"\n[-] Ollama error: {chunk['error']}")
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

    # Smart path resolution if file is under core/ or prompts/
    if not os.path.exists(code_file):
        candidate = os.path.join("core", code_file)
        if os.path.exists(candidate):
            code_file = candidate

    if not os.path.exists(prompt_file):
        candidate = os.path.join("prompts", prompt_file)
        if os.path.exists(candidate):
            prompt_file = candidate

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

    try:
        with open(code_file, 'r') as cf:
            original_code_content = cf.read()
    except FileNotFoundError:
        original_code_content = None

    c_code = extract_c_code(raw_response, original_code=original_code_content)
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
