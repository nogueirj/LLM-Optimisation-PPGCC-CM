import os, subprocess, csv, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
MODELS_DIR = os.path.join(BASE_DIR, "models")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Configurações dinâmicas
MODELS = ["sequential", "chatgpt", "codellama", "codestral", "deepseekcoder", "gemini", "qwen", "polly", "openmp"]
KERNELS = ["2mm", "3mm", "atax", "gemm", "syr2k"]
DATASETS = {"standard": "", "large": "-DLARGE_DATASET"}
REPETITIONS = 10

# Pega threads da linha de comando ou usa 8 como padrão
N_THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 8

SUFFIX_MAP = {"sequential": "seq", "chatgpt": "gpt", "openmp": "openmp", "polly": "polly"}

def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    raw_file = os.path.join(RESULTS_DIR, "raw_times.csv")
    
    # Se o arquivo não existe, cria com cabeçalho. Se existe, apenas abre para adicionar (append).
    file_exists = os.path.isfile(raw_file)
    
    with open(raw_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Model", "Dataset", "Kernel", "Threads", "Repetition", "Time"])

        print(f"🚀 Executando com {N_THREADS} Threads | Dataset: {list(DATASETS.keys())}")
        
        for ds_name, ds_flag in DATASETS.items():
            for model in MODELS:
                path = os.path.join(MODELS_DIR, model)
                if not os.path.exists(path): continue

                # Compila apenas uma vez por dataset/modelo
                subprocess.run(["make", "-C", path, "clean"], stdout=subprocess.DEVNULL)
                subprocess.run(["make", "-C", path, f"DATASET_SIZE={ds_flag}"], check=True, capture_output=True)

                suf = SUFFIX_MAP.get(model, model)
                for kernel in KERNELS:
                    exe_path = os.path.join(path, f"{kernel}-{suf}.exe")
                    if os.path.exists(exe_path):
                        print(f"🏃 {model}/{kernel} ({N_THREADS}T)", end=" ", flush=True)
                        env = os.environ.copy()
                        env["OMP_NUM_THREADS"] = str(N_THREADS)

                        for r in range(1, REPETITIONS + 1):
                            res = subprocess.run([exe_path], capture_output=True, text=True, env=env)
                            writer.writerow([model, ds_name, kernel, N_THREADS, r, res.stdout.strip()])
                            print(".", end="", flush=True)
                        print(" OK")

if __name__ == "__main__":
    run_experiment()