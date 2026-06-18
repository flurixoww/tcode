from colorama import Back, Fore, Style, init

from ai_init import ask_ai
from prompt import input_handling, make_prompt


def main():
    init(autoreset=True)

    prompt_message, file_choice = input_handling()

    if not prompt_message:
        print(Fore.YELLOW + "No prompt entered.")
        return

    try:
        prompt = make_prompt(prompt_message, file_choice)
        response, token_usage = ask_ai(prompt)
    except Exception as exc:
        print(Fore.RED + f"Failed to process request: {exc}")
        return

    print(Fore.GREEN + f"\n{response}")
    print(Back.RED + f"\n{token_usage}")


if __name__ == "__main__":
    main()
