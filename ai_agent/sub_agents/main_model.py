"""Module for interacting with the main Ollama chat model."""

from ollama import chat


def main_model(prompt: str) -> str:
    """Sends a prompt to the main chat model and returns the response content.

    Args:
        prompt: The prompt message to send to the model.

    Returns:
        The text response content from the model.
    """
    response = chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content or ""
