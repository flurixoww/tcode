from pathlib import Path

from file_manage import file_opener


def available_files(directory=None):
    base = Path.cwd() if directory is None else Path(directory)
    return sorted(path.name for path in base.iterdir() if path.is_file())


def input_handling():
    files = available_files()

    if files:
        print("Available files:")
        for name in files:
            print(f" - {name}")
    else:
        print("No files found in the current directory.")

    file_choice = input("File to read (leave blank for none): ").strip()
    prompt_message = input("Prompt: ").strip()

    return prompt_message, file_choice


def make_prompt(prompt_message, file_choice):
    context_block = "No file selected."

    if file_choice:
        context_block = f"File: {file_choice}\nContent:\n{file_opener(file_choice)}"

    return f"""
You are assisting with the following context:

{context_block}

Using this information, answer the user's request:

{prompt_message}

Instructions:
1. Answer shortly and clearly.
2. If you write code, begin with: "Working with code: <file name>"
3. Answer only what the user asks for.
""".strip()
