import os
import sys
import queue
import threading
from typing import List, Tuple

# Rich imports for beautiful CLI layout, panels, syntax highlighting, and live status
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from rich.theme import Theme
from rich.tree import Tree

# Try importing prompt_toolkit for interactive terminal history & auto-suggestions
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style as PtStyle
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

# Import the core agent logic
from ai_agent.agent import main

# Theme colors following the specified scheme
THEME_COLORS = {
    "primary": "#6096B4",      # Steel Blue
    "secondary": "#93BFCF",    # Light Steel Blue
    "accent": "#BDCDD6",       # Pale Blue/Gray
    "text": "#EEE9DA",         # Beige / Off-White
    "dark_bg": "#1e1e2e"
}

# Create a cohesive theme for Rich output
custom_theme = Theme({
    "markdown.h1": f"bold {THEME_COLORS['primary']}",
    "markdown.h2": f"bold {THEME_COLORS['secondary']}",
    "markdown.h3": f"bold {THEME_COLORS['accent']}",
    "markdown.text": THEME_COLORS['text'],
    "markdown.item": THEME_COLORS['text'],
    "markdown.block_code": f"{THEME_COLORS['primary']}",
    "markdown.code": f"{THEME_COLORS['secondary']}",
    "markdown.link": f"underline {THEME_COLORS['secondary']}",
    "info": f"{THEME_COLORS['accent']}",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "command": f"bold {THEME_COLORS['secondary']}",
})

original_stdout = sys.stdout
console = Console(file=original_stdout, theme=custom_theme)

# Initialize prompt_toolkit session if available
if HAS_PROMPT_TOOLKIT:
    pt_completer = WordCompleter([
        '/help', '/clear', '/info', '/files', '/exit', '/quit'
    ], ignore_case=True)

    pt_style = PtStyle.from_dict({
        'prompt': f"{THEME_COLORS['primary']} bold",
        'arrow': f"{THEME_COLORS['secondary']} bold",
        'input': THEME_COLORS['text'],
    })

    pt_session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=pt_completer,
        style=pt_style
    )


class QueueWriter:
    """Helper class to capture stdout and redirect it into a thread-safe Queue."""
    def __init__(self, q: queue.Queue):
        self.q = q
        self.encoding = 'utf-8'

    def write(self, s: str):
        if s:
            self.q.put(s)
        return len(s)

    def flush(self):
        pass


def print_welcome_banner():
    """Prints a beautiful welcome banner and info panel matching the color scheme and active details."""
    logo = [
        "   [#6096B4]███████████        ██████        ███████        ███████       ███████[/#6096B4]",
        "       [#6096B4]██           ██            ██       ██      ██     ██     ██[/#6096B4]",
        "       [#93BFCF]██         ██            ██           ██    ██      ██    ███████[/#93BFCF]",
        "       [#BDCDD6]██           ██            ██       ██      ██     ██     ██[/#BDCDD6]",
        "       [#EEE9DA]██             ██████        ███████        ███████       ███████[/#EEE9DA]"
    ]
    logo_str = "\n".join(logo)
    console.print(logo_str)

    model_name = "gemma3:4b"
    curr_dir = os.getcwd()
    if len(curr_dir) > 60:
        curr_dir = "..." + curr_dir[-57:]

    info_content = (
        f"[bold #6096B4]tcode CLI Pre-Alpha[/bold #6096B4]\n"
        f"[#93BFCF]Model:[/#93BFCF] [#EEE9DA]{model_name}[/#EEE9DA]  •  [#93BFCF]Workspace:[/#93BFCF] [#EEE9DA]{curr_dir}[/#EEE9DA]\n\n"
        "[bold #6096B4]⚡ Quick Commands ⚡[/bold #6096B4]\n"
        "  [#93BFCF]/help[/#93BFCF]      - Display detailed command usage\n"
        "  [#93BFCF]/clear[/#93BFCF]     - Clear screen and reprint welcome banner\n"
        "  [#93BFCF]/files[/#93BFCF]     - Visual tree of files in the workspace\n"
        "  [#93BFCF]/exit[/#93BFCF]      - Quit the session"
    )

    panel = Panel(
        info_content.strip(),
        border_style="#6096B4",
        padding=(1, 2),
        expand=False
    )
    console.print(panel)



def build_workspace_tree(dir_path: str, ignored: List[str]) -> Tree:
    """Builds a beautiful tree of the workspace structure excluding ignored paths."""
    tree = Tree(f"[bold #6096B4]📁 {os.path.basename(dir_path)}[/bold #6096B4]")

    def add_nodes(current_dir: str, current_node: Tree, depth: int = 0):
        if depth > 3:  # Prevent excessive depth traversal
            return
        try:
            entries = sorted(os.listdir(current_dir))
        except Exception:
            return

        dirs = []
        files = []
        for entry in entries:
            if entry.startswith('.') or entry in ignored or entry == "__pycache__":
                continue
            full_path = os.path.join(current_dir, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)

        for d in dirs:
            node = current_node.add(f"[#93BFCF]📁 {d}[/#93BFCF]")
            add_nodes(os.path.join(current_dir, d), node, depth + 1)

        for f in files:
            current_node.add(f"[#BDCDD6]📄 {f}[/#BDCDD6]")

    add_nodes(dir_path, tree)
    return tree


def show_help():
    """Prints a beautiful table explaining commands."""
    table = Table(title="[bold #6096B4]tcode Commands Help[/bold #6096B4]", border_style="#6096B4", box=box.ROUNDED)
    table.add_column("Command", style="#93BFCF", no_wrap=True)
    table.add_column("Shortcut", style="#BDCDD6", no_wrap=True)
    table.add_column("Description", style="#EEE9DA")

    table.add_row("/help", "-h", "Show this help screen")
    table.add_row("/clear", "-c", "Clear the terminal window")
    table.add_row("/info", "-i", "Display RAG index status and active environment info")
    table.add_row("/files", "-f", "Display a visual tree of non-ignored workspace files")
    table.add_row("/exit", "/quit", "Close the tcode CLI session")

    console.print(table)


def show_info():
    """Prints detailed diagnostic and workspace details."""
    try:
        from ai_agent.sub_agents.file_search import chroma_client_initialization, ignored_files_info
        collection = chroma_client_initialization()
        chunk_count = collection.count()
    except Exception:
        chunk_count = "N/A"

    try:
        ignored = ignored_files_info()
        ignored_str = ", ".join(ignored)
    except Exception:
        ignored_str = "None"

    info_table = Table(title="[bold #6096B4]System & Workspace Status[/bold #6096B4]", show_header=False, border_style="#93BFCF", box=box.ROUNDED)
    info_table.add_column("Property", style="bold #93BFCF")
    info_table.add_column("Value", style="#EEE9DA")

    info_table.add_row("Workspace Root", os.getcwd())
    info_table.add_row("Chroma DB Path", "./chroma_db")
    info_table.add_row("Chroma Chunk Count", str(chunk_count))
    info_table.add_row("Ignored Folders/Files", ignored_str)
    info_table.add_row("Active Model", "gemma3:4b")
    info_table.add_row("Python Executable", sys.executable)
    info_table.add_row("OS Platform", sys.platform)

    console.print(info_table)


def show_files():
    """Prints a beautiful file tree of the workspace."""
    try:
        from ai_agent.sub_agents.file_search import ignored_files_info
        ignored = ignored_files_info()
    except Exception:
        ignored = []

    tree = build_workspace_tree(os.getcwd(), ignored)
    console.print(Panel(tree, title="[bold #6096B4]Workspace Files[/bold #6096B4]", border_style="#6096B4", padding=(1, 2)))


def extract_response_and_logs(captured_stdout: str) -> Tuple[List[str], str]:
    """Parses captured output to separate diagnostic logs from the final agent response."""
    lines = captured_stdout.splitlines()
    logs = []
    response_lines = []

    progress_markers = [
        "Using files referenced in the prompt.",
        "Using access to the files to give an answer...",
        "Using general knowledge to asnwer the question.",
        "Successfully indexed "
    ]

    in_prefix = True
    for line in lines:
        stripped = line.strip()
        if in_prefix:
            is_marker = False
            for marker in progress_markers:
                if marker in stripped:
                    logs.append(stripped)
                    is_marker = True
                    break
            if not is_marker:
                if stripped:
                    in_prefix = False
                    response_lines.append(line)
        else:
            response_lines.append(line)

    response = "\n".join(response_lines).strip()
    return logs, response


def make_status_layout(step: int, message: str) -> Panel:
    """Generates the checklist layout representing the current state of request processing."""
    steps = [
        "Classifying request routing",
        "Gathering context & searching files",
        "Generating model response"
    ]

    content = ""
    for idx, s in enumerate(steps, 1):
        if idx < step:
            content += f"[bold green]✔[/bold green] [#BDCDD6]{s}[/]\n"
        elif idx == step:
            content += f"[#6096B4]● {s}... ({message})[/]\n"
        else:
            content += f"[#BDCDD6]○ {s}[/]\n"

    spinner = Spinner("dots12", text="[#93BFCF]tcode agent is processing...[/#93BFCF]", style="#6096B4")

    layout_table = Table.grid(expand=True)
    layout_table.add_row(content.strip())
    layout_table.add_row("")
    layout_table.add_row(spinner)

    return Panel(
        layout_table,
        title="[bold #6096B4] Agent Progress [/bold #6096B4]",
        border_style="#93BFCF",
        padding=(1, 2),
        expand=False
    )


def execute_agent_with_live_status(user_input: str) -> str:
    """Runs the agent inside a background thread while animating a step-by-step progress checklist."""
    q = queue.Queue()

    def worker():
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(q)
        try:
            main(user_input)
        except Exception as e:
            q.put(f"ERROR: {str(e)}")
        finally:
            sys.stdout = old_stdout
            q.put(None)

    t = threading.Thread(target=worker)
    t.start()

    step = 1
    message = "Routing query..."

    with Live(make_status_layout(step, message), console=console, auto_refresh=True) as live:
        accumulated_chunks = []
        while True:
            try:
                chunk = q.get(timeout=0.1)
                if chunk is None:
                    break
                accumulated_chunks.append(chunk)

                stripped = chunk.strip()

                if "Using files referenced" in stripped:
                    step = 2
                    message = "Reading referenced files"
                elif "Using access to the files" in stripped:
                    step = 2
                    message = "Semantic search active"
                elif "Successfully indexed" in stripped:
                    step = 2
                    message = "RAG Index updated"
                elif "Using general knowledge" in stripped:
                    step = 2
                    message = "Direct reasoning active"

                # If we've completed classification and start seeing other text, transition to generation step
                if step == 2 and not any(marker in stripped for marker in ["Using", "Successfully"]):
                    step = 3
                    message = "Generating answer"

                live.update(make_status_layout(step, message))

            except queue.Empty:
                if not t.is_alive():
                    break

    full_output = "".join(accumulated_chunks)

    if "ERROR:" in full_output:
        # Extract and print error cleanly
        for line in full_output.splitlines():
            if line.startswith("ERROR:"):
                console.print(f"\n[bold red]✖ Agent Error: {line[6:]}[/bold red]\n")
                return ""

    logs, response = extract_response_and_logs(full_output)
    return response


def enhance_markdown_headers(text: str) -> str:
    """Prefixes key response sections with beautiful styled headers and emojis."""
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == "General Answer" or stripped == "## General Answer" or stripped == "### General Answer":
            new_lines.append("## 💡 General Answer")
        elif stripped == "What Was Done" or stripped == "## What Was Done" or stripped == "### What Was Done":
            new_lines.append("## 🔧 What Was Done")
        elif stripped == "Code Changes" or stripped == "## Code Changes" or stripped == "### Code Changes":
            new_lines.append("## 📝 Code Changes")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def render_response(response_text: str) -> None:
    """Splits response text into prose and code, rendering code block sections inside dedicated styled panels."""
    if not response_text:
        return

    enhanced_text = enhance_markdown_headers(response_text)

    console.print()
    console.print(f"[{THEME_COLORS['accent']}]" + "━" * console.width + "[/]")
    console.print()

    parts = enhanced_text.split("```")
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Markdown prose
            content = part.strip()
            if content:
                console.print(Markdown(content))
        else:
            # Code blocks
            lines = part.splitlines()
            lang = "python"
            code_lines = []

            if lines:
                first_line = lines[0].strip()
                if first_line in ["python", "py", "javascript", "js", "html", "css", "json", "bash", "sh", "yaml", "yml", "markdown", "md", "sql", "rust", "rs", "cpp", "c"]:
                    lang = first_line
                    code_lines = lines[1:]
                else:
                    if len(first_line) < 15 and not any(c in first_line for c in ["=", "(", ")", ":", "{", "}", "import ", "from "]):
                        lang = first_line
                        code_lines = lines[1:]
                    else:
                        code_lines = lines

            code_content = "\n".join(code_lines).strip()

            syntax = Syntax(
                code_content,
                lang or "text",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
                background_color="default"
            )

            code_panel = Panel(
                syntax,
                border_style=THEME_COLORS['primary'],
                title=f"[bold {THEME_COLORS['secondary']}] 🛠️ {lang.upper()} [/bold {THEME_COLORS['secondary']}]",
                subtitle=f"[italic {THEME_COLORS['accent']}]tcode agent code block[/italic {THEME_COLORS['accent']}]",
                subtitle_align="right",
                padding=(1, 2),
                expand=True
            )
            console.print()
            console.print(code_panel)
            console.print()

    console.print()
    console.print(f"[{THEME_COLORS['accent']}]" + "━" * console.width + "[/]")
    console.print()


def get_user_input() -> str:
    """Reads input with autocomplete and history features using prompt_toolkit, falling back to standard input if needed."""
    if HAS_PROMPT_TOOLKIT:
        try:
            return pt_session.prompt([
                ('class:prompt', 'tcode'),
                ('class:arrow', ' ❯ '),
            ]).strip()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except EOFError:
            return "/exit"
    else:
        try:
            console.print(f"[bold {THEME_COLORS['primary']}]tcode[/] [bold {THEME_COLORS['secondary']}]❯[/] ", end="")
            return input().strip()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except EOFError:
            return "/exit"


def handle_slash_command(cmd: str) -> bool:
    """Processes special assistant actions. Returns True to continue prompt loop, False to exit."""
    cmd_lower = cmd.lower()

    if cmd_lower in ["/exit", "/quit"]:
        console.print(f"[bold {THEME_COLORS['secondary']}]Goodbye! Have a great day coding. 👋[/]")
        return False
    elif cmd_lower in ["/clear", "-c"]:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_welcome_banner()
    elif cmd_lower in ["/help", "-h"]:
        show_help()
    elif cmd_lower in ["/info", "-i"]:
        show_info()
    elif cmd_lower in ["/files", "-f"]:
        show_files()
    else:
        console.print(f"[bold red]Unknown command: {cmd}[/bold red]. Type [bold #93BFCF]/help[/bold #93BFCF] to see available commands.")

    return True


def main_cli():
    """Main CLI entrypoint control loop."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_welcome_banner()

    while True:
        try:
            user_input = get_user_input()
            if not user_input:
                continue

            if user_input.startswith("/"):
                should_continue = handle_slash_command(user_input)
                if not should_continue:
                    break
                continue

            # Regular question handling
            response = execute_agent_with_live_status(user_input)
            render_response(response)

        except KeyboardInterrupt:
            console.print(f"\n[bold {THEME_COLORS['secondary']}]Session closed. Goodbye! 👋[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]\n")


if __name__ == "__main__":
    main_cli()
