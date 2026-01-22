import ollama

def process_code_with_llm(code_file_path, prompt_template):
    """
    Reads code from a file and processes it using an Ollama language model.

    Args:
        code_file_path (str): Path to the code file.
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

    response = ollama.chat(model='codellama:13b', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

# Example usage
code_file = 'gemm.c'
prompt = "Anote o código com diretivas openmp:\n```python\n{code}\n```"
result = process_code_with_llm(code_file, prompt)
print(result)
