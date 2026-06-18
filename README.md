# tcode

A small local AI assistant demo for answering questions from either general reasoning or local files.

## What it does

- Prompts for a file and a question
- Builds a context-aware prompt
- Sends it to a local Ollama model
- Prints the response and approximate token usage

## Project files

- `main.py` - CLI entry point
- `prompt.py` - collects input and builds prompts
- `file_manage.py` - safe file reading
- `ai_init.py` - Ollama chat wrapper
- `ai_agent/` - routing demo code

## Notes

This project expects Ollama to be installed and running locally.
