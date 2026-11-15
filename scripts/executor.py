import os, subprocess, csv, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
MODELS_DIR = os.path.join(BASE_DIR, "models")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

MODELS = [
    "sequential",
    "chatgpt",
    "codellama",
    "codestral",
    "deepseekcoder",
    "granite",
    "gemini",
    "qwen",
    "polly",
    "openmp",
    "codestral_22b",
    "granite-code-20b",
    "qwen-2.5-coder-14b",
    "starcode-2_15b",
    "deepseekcoder-coder-v2_16b",
    "codellama_13b",
    "codestral-openmp_16b",
    "codestral-openmp_8b",
    "codestral-openmp_4b",
    "codestral-openmp_3b",
]
KERNELS = ["2mm", "3mm", "atax", "gemm", "syr2k"]
REPETITIONS = int(os.environ.get("REPETITIONS", "10"))
EXEC_TIMEOUT = int(os.environ.get("EXEC_TIMEOUT", "60"))
N_THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
DATASET_LOG = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("DATASET_LABEL", "standard")

SUFFIX_MAP = {"sequential": "seq", "chatgpt": "gpt", "openmp": "openmp", "polly": "polly"}

def get_active_models():
    only_env = os.environ.get("ONLY_MODELS", "").strip()
    if not only_env:
        return MODELS
    requested = [m.strip() for m in only_env.replace(",", " ").split() if m.strip()]
    return requested

def get_active_kernels():
    only_env = os.environ.get("ONLY_KERNELS", "").strip()
    if not only_env:
        return KERNELS
    requested = [k.strip() for k in only_env.replace(",", " ").split() if k.strip()]
    return requested

def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    raw_file = os.environ.get("RAW_CSV_PATH", os.path.join(RESULTS_DIR, "raw_times.csv"))
    also_append = os.environ.get("ALSO_APPEND_CSV", "").strip()
    file_exists = os.path.isfile(raw_file) and os.path.getsize(raw_file) > 0

    extra_writer = None
    extra_f = None
    if also_append:
        extra_exists = os.path.isfile(also_append) and os.path.getsize(also_append) > 0
        extra_f = open(also_append, mode='a', newline='')
        extra_writer = csv.writer(extra_f)
        if not extra_exists:
            extra_writer.writerow(["Model", "Dataset", "Kernel", "Threads", "Repetition", "Time"])

    # Modo 'a' (append) para acumular os resultados de diferentes chamadas de threads
    with open(raw_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Model", "Dataset", "Kernel", "Threads", "Repetition", "Time"])

        dataset_log = DATASET_LOG
        active_models = get_active_models()
        active_kernels = get_active_kernels()

        for model in active_models:
            path = os.path.join(MODELS_DIR, model)
            if not os.path.exists(path): continue

            suf = SUFFIX_MAP.get(model, model)
            
            for kernel in active_kernels:
                exe_name = f"{kernel}-{suf}.exe"
                exe_path = os.path.join(path, exe_name)

                if os.path.exists(exe_path):
                    print(f"🏃 Executando {model}/{kernel} ({dataset_log}) | {N_THREADS}T", end=" ", flush=True)
                    env = os.environ.copy()
                    env["OMP_NUM_THREADS"] = str(N_THREADS)
                    
                    # Otimização para HPC: Afinidade de threads
                    env["OMP_PROC_BIND"] = "true"
                    env["OMP_PLACES"] = "cores"

                    aborted = False
                    for r in range(1, REPETITIONS + 1):
                        try:
                            res = subprocess.run([exe_path], capture_output=True, text=True, env=env, 
                                               check=True, timeout=EXEC_TIMEOUT)
                            val = res.stdout.strip()
                            row = [model, dataset_log, kernel, N_THREADS, r, val]
                            writer.writerow(row)
                            if extra_writer is not None:
                                extra_writer.writerow(row)
                            print(".", end="", flush=True)
                        except subprocess.TimeoutExpired:
                            print("T(timeout->skip_rest)", end="", flush=True)
                            aborted = True
                            break
                        except subprocess.CalledProcessError as e:
                            print(f"F(exit={e.returncode}->skip_rest)", end="", flush=True)
                            aborted = True
                            break
                        except Exception as e:
                            print("E", end="", flush=True)
                            aborted = True
                            break
                    f.flush()
                    if extra_f is not None:
                        extra_f.flush()
                    print(" ABORTADO" if aborted else " OK")

    if extra_f is not None:
        extra_f.close()

if __name__ == "__main__":
    run_experiment()