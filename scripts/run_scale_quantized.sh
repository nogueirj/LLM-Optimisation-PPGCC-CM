#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE ESCALABILIDADE - MODELOS QUANTIZADOS (CODESTRAL-OPENMP 16B/8B/4B/3B)
# ==============================================================================
# Compila e executa os códigos C otimizados pelas variantes quantizadas em
# múltiplos níveis de threads (1, 2, 4, 8, 16, 32, 64) nos datasets STANDARD e
# LARGE, preservando os resultados históricos dos demais modelos em raw_times.csv
# e gerando relatórios comparativos de Speedup e Eficiência Paralela.
#
# Uso:
#   ./scripts/run_scale_quantized.sh             # Executa standard + large (1..64T)
#   ./scripts/run_scale_quantized.sh standard    # Executa apenas standard
#   ./scripts/run_scale_quantized.sh large       # Executa apenas large
#
# Variáveis opcionais de ambiente:
#   THREADS_LIST="1 2 4 8" REPETITIONS=3 ./scripts/run_scale_quantized.sh standard
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

TARGET_MODE="${1:-both}"

if [ -n "${THREADS_LIST:-}" ]; then
    read -r -a THREADS_SEQUENCE <<< "$THREADS_LIST"
else
    THREADS_SEQUENCE=(1 2 4 8 16 32 64)
fi

QUANT_MODELS=(
    "codestral-openmp_16b"
    "codestral-openmp_8b"
    "codestral-openmp_4b"
    "codestral-openmp_3b"
)
ONLY_MODELS_CSV="codestral-openmp_16b,codestral-openmp_8b,codestral-openmp_4b,codestral-openmp_3b"

RAW_CSV="${RAW_CSV_PATH:-results/raw_times.csv}"
RAW_QUANT_CSV="${RAW_QUANT_CSV_PATH:-results/raw_times_quantized.csv}"
FINAL_METRICS_CSV="results/final_metrics.csv"

mkdir -p results logs

# ------------------------------------------------------------------------------
# 1. Garantir integridade do raw_times.csv (preservar ou reconstruir baseline)
#    Usa apenas biblioteca padrão do Python 3 (sem depender de pandas no servidor)
# ------------------------------------------------------------------------------
python3 - "$RAW_CSV" "$FINAL_METRICS_CSV" <<'PYEOF'
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

raw_path = Path(sys.argv[1])
fm_path = Path(sys.argv[2])
backup_path = raw_path.parent / "raw_times_backup.csv"

def is_dataless_on_mac(p: Path) -> bool:
    if not p.exists() or os.uname().sysname != "Darwin":
        return False
    res = subprocess.run(["ls", "-lO", str(p)], capture_output=True, text=True)
    return "dataless" in res.stdout

needs_seed = True
if raw_path.exists() and not is_dataless_on_mac(raw_path) and raw_path.stat().st_size > 100:
    try:
        models_found = set()
        with open(raw_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                models_found.add(row.get("Model", "").strip())
        if "sequential" in models_found and "codestral" in models_found:
            needs_seed = False
            if not backup_path.exists():
                shutil.copy2(raw_path, backup_path)
                print(f"📦 Backup de segurança criado em: {backup_path}")
    except Exception as e:
        print(f"⚠️ Aviso ao verificar {raw_path}: {e}")

if needs_seed and fm_path.exists() and not is_dataless_on_mac(fm_path):
    print(f"🔄 Semeando baseline histórico em {raw_path} a partir de {fm_path}...")
    rows = []
    seq_seen = {}
    with open(fm_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            m = r["Model"].strip()
            ds = r["Dataset"].strip()
            k = r["Kernel"].strip()
            t = int(float(r["Threads"]))
            tm = r["Time"].strip()
            t_seq = r["T_Sequential"].strip()
            rows.append([m, ds, k, t, 1, tm])
            seq_seen[(ds, k, t)] = t_seq

    for (ds, k, t), t_seq in sorted(seq_seen.items()):
        rows.append(["sequential", ds, k, t, 1, t_seq])

    if is_dataless_on_mac(raw_path):
        raw_path.unlink()
    with open(raw_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Model", "Dataset", "Kernel", "Threads", "Repetition", "Time"])
        w.writerows(rows)
    print(f"✅ Baseline histórico restaurado em {raw_path} ({len(rows)} registros).")
PYEOF

# ------------------------------------------------------------------------------
# Função para executar um dataset completo (standard ou large)
# ------------------------------------------------------------------------------
run_dataset_benchmark() {
    local ds_label="$1"
    local ds_flag="$2"
    local ds_upper
    ds_upper="$(echo "$ds_label" | tr '[:lower:]' '[:upper:]')"

    echo ""
    echo "======================================================================"
    echo "📦 PREPARANDO DATASET: ${ds_upper} (${ds_flag})"
    echo "======================================================================"

    # Remover entradas antigas de codestral-openmp_* para este dataset (idempotência)
    python3 - "$ds_label" "$RAW_CSV" "$RAW_QUANT_CSV" <<'PYEOF'
import csv
import os
import subprocess
import sys
from pathlib import Path

def is_dataless_on_mac(p: Path) -> bool:
    if not p.exists() or os.uname().sysname != "Darwin":
        return False
    res = subprocess.run(["ls", "-lO", str(p)], capture_output=True, text=True)
    return "dataless" in res.stdout

ds = sys.argv[1]
for p_str in sys.argv[2:]:
    p = Path(p_str)
    if p.exists() and not is_dataless_on_mac(p) and p.stat().st_size > 0:
        try:
            kept = []
            removed = 0
            with open(p, "r", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    kept.append(header)
                for row in reader:
                    if len(row) >= 2 and row[1].strip() == ds and row[0].strip().startswith("codestral-openmp_"):
                        removed += 1
                    else:
                        kept.append(row)
            with open(p, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(kept)
            if removed > 0:
                print(f"🧹 Removidos {removed} registros anteriores de codestral-openmp_* ({ds}) em {p_str}")
        except Exception as e:
            print(f"⚠️ Aviso ao limpar {p_str}: {e}")
PYEOF

    # Compilar as 4 variantes quantizadas com o DATASET_SIZE correspondente
    for m in "${QUANT_MODELS[@]}"; do
        echo "----------------------------------------------------------------------"
        echo "🔨 Compilando $m para dataset ${ds_upper} (${ds_flag})..."
        make -C "models/$m" clean all DATASET_SIZE="$ds_flag"
    done

    # Verificar se sequential já existe no CSV para este dataset; se não, compilar e rodar em 1T
    HAS_SEQ=$(python3 - "$ds_label" "$RAW_CSV" <<'PYEOF'
import csv
import os
import subprocess
import sys
from pathlib import Path

ds = sys.argv[1]
p = Path(sys.argv[2])
if p.exists() and p.stat().st_size > 0:
    has = False
    with open(p, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Model", "").strip() == "sequential" and row.get("Dataset", "").strip() == ds:
                has = True
                break
    print("1" if has else "0")
else:
    print("0")
PYEOF
)
    if [ "$HAS_SEQ" = "0" ]; then
        echo "🔨 Compilando e executando baseline sequential (1T) para dataset ${ds_upper}..."
        make -C "models/sequential" clean all DATASET_SIZE="$ds_flag"
        RAW_CSV_PATH="$RAW_CSV" ONLY_MODELS="sequential" ALSO_APPEND_CSV="$RAW_QUANT_CSV" python3 scripts/executor.py 1 "$ds_label"
    fi

    # Loop de escalabilidade por número de threads
    for t in "${THREADS_SEQUENCE[@]}"; do
        echo "======================================================================"
        echo "🚀 EXECUTANDO QUANTIZADOS | DATASET: ${ds_upper} | THREADS: ${t}T"
        echo "======================================================================"
        RAW_CSV_PATH="$RAW_CSV" \
        ONLY_MODELS="$ONLY_MODELS_CSV" \
        ALSO_APPEND_CSV="$RAW_QUANT_CSV" \
        EXEC_TIMEOUT="${EXEC_TIMEOUT:-30}" \
        python3 scripts/executor.py "$t" "$ds_label"
    done
}

# ------------------------------------------------------------------------------
# 2. Execução conforme o modo escolhido (standard, large ou both)
# ------------------------------------------------------------------------------
case "$TARGET_MODE" in
    standard|-DSTANDARD_DATASET)
        run_dataset_benchmark "standard" "-DSTANDARD_DATASET"
        ;;
    large|-DLARGE_DATASET)
        run_dataset_benchmark "large" "-DLARGE_DATASET"
        ;;
    both|"")
        run_dataset_benchmark "standard" "-DSTANDARD_DATASET"
        run_dataset_benchmark "large" "-DLARGE_DATASET"
        ;;
    *)
        echo "❌ Uso inválido: $TARGET_MODE (use: standard, large ou both)"
        exit 1
        ;;
esac

# ------------------------------------------------------------------------------
# 3. Consolidação e Análise de Escalabilidade
# ------------------------------------------------------------------------------
echo ""
echo "======================================================================"
echo "📊 GERANDO MÉTRICAS, TABELAS LATEX E GRÁFICOS DE ESCALABILIDADE"
echo "======================================================================"
python3 analysis_scripts/analise_quantizados_escalabilidade.py
python3 scripts/analyzer.py || echo "⚠️ Aviso: scripts/analyzer.py requer pandas/matplotlib (pode ser rodado localmente)."
python3 analysis_scripts/analise_por_dataset.py || true
python3 analysis_scripts/gerar_tabelas_latex.py || true
python3 analysis_scripts/speedup_grafico.py || true

echo ""
echo "======================================================================"
echo "✨ BENCHMARK DE ESCALABILIDADE DOS QUANTIZADOS FINALIZADO!"
echo "📁 Arquivos gerados para versionamento e análise:"
echo "  • results/raw_times_quantized.csv             (tempos brutos das 4 variantes)"
echo "  • results/quantized_scaling_metrics.csv       (speedup e eficiência consolidados)"
echo "  • results/tabela_escalabilidade_quantizados.tex (tabelas LaTeX para a tese)"
echo "  • results/scaling_curve_quantized.png         (curvas de escalabilidade)"
echo "  • results/final_metrics.csv                   (métricas globais de todos os modelos)"
echo "======================================================================"
