from colorama import Back, Fore, Style

from ai_init import ask_ai
from prompt import input_handling, make_prompt


def main():
    prompt_message, file_choice = input_handling()
    response, token_usage = ask_ai(make_prompt(prompt_message, file_choice))
    print(Fore.GREEN + "\n", response, Style.RESET_ALL)
    print(Back.RED + "\n", token_usage, Style.RESET_ALL)


if __name__ == "__main__":
    main()
