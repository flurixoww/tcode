# AI Agent Backend Logic Roadmap

This roadmap outlines the architectural and logic-focused steps to build a robust, autonomous coding agent backend (similar to how Claude Code operates under the hood).

## Phase 1: Object-Oriented Refactoring & Better Retrieval
Right now, the logic is functional and linear. The first step is organizing it into a scalable state.
* **[ ] Create a `CodebaseContext` Class**: Instead of reading everything into a single string (`get_file_content`), build a class that indexes the directory. It should store file paths, token counts, and manage chunking (e.g., splitting code by classes/functions, not just random lines).
* **[ ] Upgrade the RAG Logic**: Raw text RAG struggles with code. Update `file_distance` logic to prioritize exact keyword matches (like function names or class definitions) alongside semantic distance.
* **[ ] State Management Class (`AgentState`)**: Create a class that holds the current state of the request: the original prompt, the chat history, the files retrieved so far, and the remaining token budget.

## Phase 2: The Core Agentic Loop (Iterative Execution)
Currently, the code executes in a single pass: `Route -> Fetch File -> Answer`. An advanced agent uses an **iterative reasoning loop** (ReAct / Tool Calling).
* **[ ] Implement the Execution Loop**: Create a `while not finished:` loop.
  1. Send current `AgentState` to `main_model`.
  2. `main_model` decides: "I can answer now" OR "I need to take an action".
  3. If action: run the specific logic function, append the result to `AgentState`, and loop again.
* **[ ] Deprecate the Rigid Router**: As the `main_model` learns to use tools natively, a separate rigid `router.py` becomes unnecessary. The main model will autonomously decide when to search for files.

## Phase 3: The Tool Execution Engine
Build the backend logic for the actions the agent can take. These should be standalone Python functions that return strings (to be fed back to the LLM).
* **[ ] Information Tools**:
  * `read_file_logic(filepath, start_line, end_line)`: Read specific parts of a file to save tokens.
  * `list_directory_logic(path)`: Get folder structures.
  * `regex_search_logic(pattern)`: Let the model grep the codebase for variables or function usages.
* **[ ] Editing Tools**:
  * `write_file_logic(filepath, content)`: Overwrite a file completely.
  * `apply_diff_logic(filepath, search_block, replace_block)`: Crucial for larger files. The agent edits a file by only supplying the lines that changed.

## Phase 4: Context & Memory Management
Aggressively manage what goes into the prompt to stay within token limits and keep the model focused.
* **[ ] Use `summary_model`**: If a file is too large or the context window is getting full, use this sub-agent to compress the history or summarize a long file into just its function signatures before feeding it to `main_model`.
* **[ ] Codebase Map Generation**: Write logic that runs once on startup to build a structural map of the project (e.g., "File A contains classes X, Y. File B imports X."). Feed this map into the system prompt.

## Phase 5: Self-Correction & Validation Logic
An autonomous agent must be resilient and handle its own errors.
* **[ ] Error Parsing Logic**: If the agent's code edit fails syntax validation (e.g., parsing it with Python's `ast` module throws an error), catch it in the backend and automatically feed the error traceback back to the `main_model` to try again.
* **[ ] Sub-Agent Delegation**: Utilize the `sub_agents` directory for complex tasks. For example, spawning parallel `file_search` agents to investigate different folders simultaneously, then synthesizing their findings.
