import os, subprocess, csv, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
MODELS_DIR = os.path.join(BASE_DIR, "models")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

MODELS = ["sequential", "chatgpt", "codellama", "codestral", "deepseekcoder", "granite", "gemini", "qwen", "polly", "openmp",]
KERNELS = ["2mm", "3mm", "atax", "gemm", "syr2k"]
REPETITIONS = 10
N_THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 8

SUFFIX_MAP = {"sequential": "seq", "chatgpt": "gpt", "openmp": "openmp", "polly": "polly"}

def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    raw_file = os.path.join(RESULTS_DIR, "raw_times.csv")
    file_exists = os.path.isfile(raw_file)
    
    # Modo 'a' (append) para acumular os resultados de diferentes chamadas de threads
    with open(raw_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Model", "Dataset", "Kernel", "Threads", "Repetition", "Time"])

        # O Dataset é detectado pelo nome do arquivo ou assumido como 'standard' para o log
        dataset_log = "standard" 

        for model in MODELS:
            path = os.path.join(MODELS_DIR, model)
            if not os.path.exists(path): continue

            suf = SUFFIX_MAP.get(model, model)
            
            for kernel in KERNELS:
                exe_name = f"{kernel}-{suf}.exe"
                exe_path = os.path.join(path, exe_name)

                if os.path.exists(exe_path):
                    print(f"🏃 Executando {model}/{kernel} | {N_THREADS}T", end=" ", flush=True)
                    env = os.environ.copy()
                    env["OMP_NUM_THREADS"] = str(N_THREADS)
                    
                    # Otimização para HPC: Afinidade de threads
                    env["OMP_PROC_BIND"] = "true"
                    env["OMP_PLACES"] = "cores"

                    for r in range(1, REPETITIONS + 1):
                        try:
                            res = subprocess.run([exe_path], capture_output=True, text=True, env=env, 
                                               check=True, timeout=60)
                            writer.writerow([model, dataset_log, kernel, N_THREADS, r, res.stdout.strip()])
                            print(".", end="", flush=True)
                        except subprocess.TimeoutExpired:
                            print("T", end="", flush=True)  # Timeout
                        except subprocess.CalledProcessError as e:
                            print("F", end="", flush=True)  # Falha/Crash
                        except Exception as e:
                            print("E", end="", flush=True)  # Outro erro
                    print(" OK")

if __name__ == "__main__":
    run_experiment()