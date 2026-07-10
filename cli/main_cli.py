import sys
from rich.console import Console
from ai_agent.agent import main

console = Console()

def get_agent_response(user_input: str) -> None:
    main(user_input)

def main_cli():
    console.print("[bold cyan]Agent session started. Type 'exit' to quit. [/bold cyan]\n")
    while True:
        try:
            user_input = input("Ask: ").strip()

            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_input:
                continue

            get_agent_response(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]Session closed.[/yellow]")
            sys.exit(0)

if __name__ == "__main__":
    main_cli()
