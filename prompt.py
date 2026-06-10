import os

from file_manage import file_opener


def input_handling():
    # Asking which file to read
    file_choice = input(f"{os.listdir()} \n")
    print(f"file_choice: {file_choice}")

    # Asking user for a prompt message
    prompt_message = input("Prompt:")

    return prompt_message, file_choice


def make_prompt(prompt_message, file_choice):

    # Full prompt
    prompt = f"""
    You are given a file: {file_choice}
    which contains the following content:
    {file_opener(file_choice)}

    Using this information, answer the following:
        {prompt_message}
    Answering follow these instructions:
        1. Asnwer the question shortly, user needs a meaningful response.
        2. If you are writing code, before writing it, write the following "Working with a code (file name).
        3. Answer only what user asks for, nothing extra.
    """
    return prompt
