import os
import platform
import shutil
import subprocess
import importlib.util
import tempfile

def print_header(text):
    print(f"\n{'-'*60}\n{text}\n{'-'*60}")

def check_python_lib(lib_name):
    spec = importlib.util.find_spec(lib_name)
    status = "✅ INSTALADO" if spec is not None else "❌ NÃO ENCONTRADO"
    print(f"🐍 Python Lib: {lib_name.ljust(15)} -> {status}")
    return spec is not None

def get_hpc_compiler():
    """Identifica o compilador Clang correto baseado no sistema operacional."""
    system = platform.system()
    if system == "Darwin": # macOS
        # Prioriza o caminho que você definiu no seu Makefile
        brew_clang = "/opt/homebrew/opt/llvm/bin/clang"
        if os.path.exists(brew_clang):
            return brew_clang
    # No Ubuntu ou se o Homebrew não estiver no caminho padrão
    return shutil.which("clang")

def test_hpc_capabilities(clang_path):
    """
    Realiza um teste de fumaça funcional para OpenMP e Polly.
    Em vez de procurar arquivos, tentamos compilar um código real.
    """
    if not clang_path:
        return False, False

    code = """
    #include <omp.h>
    #include <stdio.h>
    int main() {
        #pragma omp parallel
        {
            if(omp_get_thread_num() == 0) 
                printf("OpenMP ativo com %d threads", omp_get_num_threads());
        }
        return 0;
    }
    """
    
    system = platform.system()
    
    # Flags de suporte baseadas no seu Makefile
    if system == "Darwin":
        omp_flags = [
            "-I/opt/homebrew/opt/llvm/include",
            "-L/opt/homebrew/opt/llvm/lib",
            "-lomp",
            "-Wl,-rpath,/opt/homebrew/opt/llvm/lib"
        ]
    else: # Ubuntu
        omp_flags = ["-fopenmp", "-lomp"]

    # Flags do Polly (exatamente as que você usa)
    polly_flags = ["-mllvm", "-polly", "-mllvm", "-polly-parallel"]

    omp_ok = False
    polly_ok = False

    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, "test.c")
        exe_path = os.path.join(tmpdir, "test.exe")
        
        with open(source_path, "w") as f:
            f.write(code)

        # Teste 1: OpenMP
        try:
            subprocess.run([clang_path, source_path] + omp_flags + ["-o", exe_path], 
                           check=True, capture_output=True)
            res = subprocess.run([exe_path], check=True, capture_output=True, text=True)
            print(f"🔬 OpenMP: {''.ljust(15)} -> ✅ FUNCIONANDO ({res.stdout.strip()})")
            omp_ok = True
        except Exception:
            print(f"🔬 OpenMP: {''.ljust(15)} -> ❌ FALHA NA COMPILAÇÃO/EXECUÇÃO")

        # Teste 2: Polly
        try:
            # Tentamos compilar usando as flags do Polly
            subprocess.run([clang_path, source_path] + omp_flags + polly_flags + ["-o", exe_path], 
                           check=True, capture_output=True)
            print(f"💎 LLVM Polly: {''.ljust(11)} -> ✅ FUNCIONANDO (Flags aceitas)")
            polly_ok = True
        except Exception:
            print(f"💎 LLVM Polly: {''.ljust(11)} -> ❌ FALHOU (Compilador não reconhece as flags)")

    return omp_ok, polly_ok

def main():
    sys_info = platform.uname()
    print_header(f"🔍 RELATÓRIO DE SAÚDE DO AMBIENTE - {sys_info.system}")
    
    # 1. Check Python
    print_header("📦 DEPENDÊNCIAS PYTHON")
    libs = ["pandas", "seaborn", "matplotlib", "numpy"]
    py_ok = all([check_python_lib(l) for l in libs])

    # 2. Check Compiler Path
    print_header("🛠️ COMPILADORES")
    clang_path = get_hpc_compiler()
    if clang_path:
        print(f"💻 Clang Path:    {clang_path} -> ✅ ENCONTRADO")
    else:
        print(f"💻 Clang Path:    Nenhum -> ❌ NÃO ENCONTRADO")

    # 3. Check Functional HPC
    print_header("🚀 HIGH PERFORMANCE COMPUTING (HPC)")
    omp_ok, polly_ok = test_hpc_capabilities(clang_path)

    print_header("🏁 VEREDITO FINAL")
    if py_ok and clang_path and omp_ok and polly_ok:
        print("🚀 TUDO PRONTO! O ambiente está validado para o experimento.")
    else:
        print("⚠️  ATENÇÃO: Existem pendências técnicas. Verifique as falhas acima.")

if __name__ == "__main__":
    main()