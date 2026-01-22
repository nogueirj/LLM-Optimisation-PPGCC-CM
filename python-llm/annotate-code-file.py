import sys
import os
import subprocess
import cpuinfo
import ollama

def process_code_with_llm(code_file_path, llm_model, prompt_template):
    """
    Reads code from a file and processes it using an Ollama language model.

    Args:
        code_file_path (str): Path to the code file.
        llm_model (str): Model name.
        prompt_template (str): Template for the prompt, including a placeholder for the code.

    Returns:
        str: The generated response from the language model.
    """
    try:
        with open(code_file_path, 'r') as file:
            code_content = file.read()
    except FileNotFoundError:
        return "Error: Code file not found."
    
    prompt = prompt_template.format(code=code_content)

    response = ollama.chat(model=llm_model, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']


def get_model_list():
    """
    Get a list of names of Ollama models.

    Args:
        None

    Returns:
        list: Generated list of models.
    """

    # First command: ollama list
    p1 = subprocess.Popen(['ollama', 'list'], stdout=subprocess.PIPE)

    # Second command: awk ' { print $1 }'
    p2 = subprocess.Popen(['awk', '{ print $1 }'], stdin=p1.stdout, stdout=subprocess.PIPE)

    # Close p1's stdout to prevent deadlocks
    p1.stdout.close()

    # Third command: sed -e '1d'
    p3 = subprocess.Popen(['sed', '-e', '1d'], stdin=p2.stdout, stdout=subprocess.PIPE)

    # Close p2's stdout to prevent deadlocks
    p2.stdout.close()

    # Get the output from p2
    output, errors = p3.communicate()

    # Print the output
    print(output.decode("utf-8"))

    return output.decode("utf-8").split()

if __name__ == "__main__":
    if len(sys.argv) != 3: # Expecting the script name + 2 arguments
        print("Usage: python", sys.argv[0], "<code_file> <prompt>")
        print("Example: python", sys.argv[0], "codellama:13b gemm.c 'Analise o código'")
        sys.exit(1) # Exit with an error code

    code_file = sys.argv[1]
    prompt = sys.argv[2]
    version = "openmp"
    cpu_info = cpuinfo.get_cpu_info()
    hostname=os.uname()[1]

    models = get_model_list()

    print(models)

    for model in models:
        # Proceed with your logic using param1 and param2
        print(f"Model: {model}")
        print(f"File: {code_file}")
        print(f"prompt: {prompt}")

        base = os.path.basename(code_file)
        benchmark_name = os.path.splitext(base)[0]

        result_file_name = "{}-{}-{}-{}-{}.c".format(benchmark_name, model, version, hostname, cpu_info['brand_raw'])

        print(f"Result file: {result_file_name}")

        prompt = prompt + ":\n```python\n{code}\n```"

        result = process_code_with_llm(code_file, model, prompt)
        
        print(result)

        file = open(result_file_name, "w")
        file.write(result)
        file.close()
