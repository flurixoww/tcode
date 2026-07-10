# tcode

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Local%20AI-Ollama-orange.svg" alt="Local AI Engine">
  <img src="https://img.shields.io/badge/Model-Gemma3%3A4b-red.svg" alt="Model Gemma3">
  <img src="https://img.shields.io/badge/UI-Rich%20TUI-green.svg" alt="UI Theme">
</p>

A premium, local AI-powered codebase search and chat companion. **tcode** provides a beautiful, interactive Terminal User Interface (TUI) to analyze, search, and chat with your local codebase using a local LLM—with zero external API calls or data leaks.

---

## 🌟 Key Features

* **🧠 Smart Router Classifier:** Automatically classifies incoming requests. It decides whether to answer via general reasoning or dynamically search and ingest relevant code chunks from your local files.
* **⚡ Semantic RAG Search:** Indexes your project files into a local ChromaDB collection using a language-aware Python text splitter, searching for codebase context only when needed.
* **🎨 Premium Rich TUI:** Displays progress via a real-time checklists board and wraps codebase answers in gorgeous, syntax-highlighted panels with line numbers.
* **⌨️ Interactive CLI Shell:** Powered by `prompt_toolkit`, featuring command history (up/down arrow keys), auto-suggestions, and command autocompletion when typing `/`.
* **🔒 100% Private & Local:** Runs entirely on your local machine using Ollama and ChromaDB.

---

## 🏗️ Project Architecture

```
tcode/
├── ai_agent/                 # Core AI agent logic
│   ├── agent.py              # Main orchestrator (routes and queries)
│   └── sub_agents/           # Modular assistant sub-components
│       ├── agent_prompts.py  # System prompts (Router & Main Model)
│       ├── file_address.py   # Code referencing utilities
│       ├── file_search.py    # ChromaDB indexing & semantic search
│       ├── main_model.py     # Ollama main model interface
│       └── router.py         # Routing classification models
├── cli/                      # Interactive terminal user interface
│   ├── main_cli.py           # Premium TUI runner
│   └── documentation.md      # Detailed TUI documentation
├── chroma_db/                # Local database for indexed code chunks
├── ignore_rules.txt          # Directories and file types to ignore in RAG
└── README.md                 # Project overview and guide
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
* **Python 3.9+**
* **Ollama** installed and running on your system. Download it from [ollama.com](https://ollama.com).
* Pull the Gemma3 model:
  ```bash
  ollama pull gemma3:4b
  ```

### 2. Clone and Setup Environment
Navigate to your project directory and set up a virtual environment:
```bash
# Create virtual environment
python3 -m venv tcode_env

# Activate virtual environment
source tcode_env/bin/activate  # On Windows: tcode_env\Scripts\activate

# Install required dependencies
pip install rich prompt_toolkit chromadb langchain-text-splitters ollama
```

---

## 🚀 Running the TUI

To launch the interactive TUI shell, run the following command from the project root:
```bash
PYTHONPATH=. tcode_env/bin/python3 cli/main_cli.py
```

---

## 🛠️ TUI Commands Reference

When inside the CLI shell, you can prefix commands with `/` for special utility actions:

| Command | Shortcut | Description |
| :--- | :--- | :--- |
| **`/help`** | `-h` | Prints a structured commands help table |
| **`/clear`** | `-c` | Clears the terminal screen and reprints the logo banner |
| **`/info`** | `-i` | Displays diagnostic information (active folder, Chroma DB chunk counts, and model status) |
| **`/files`** | `-f` | Visualizes the project directories and files in a beautiful tree |
| **`/exit`** | `/quit` | Closes the CLI session |

---

## 📝 Customization

### Ignoring Directories & Files
You can configure which directories and files to exclude from search indexing (e.g., node modules, virtual environments, configuration files) in [ignore_rules.txt](file:///Users/flurixoww/Documents/Projects/tcode/ignore_rules.txt). The file loader uses this file to prune paths during walks.
