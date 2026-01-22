import subprocess


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

    models = get_model_list()

    print(models)

    for model in models:
        print(model)
