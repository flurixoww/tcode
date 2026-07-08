"""Module for routing user prompts using a classifier model and parsing JSON responses."""

import json
import re
from typing import Any

from ollama import chat


def route(prompt: str) -> str:
    """Routes the given prompt using the router model.

    Args:
        prompt: The user's prompt to route.

    Returns:
        The raw text response from the LLM (expected to contain JSON).

    Raises:
        RuntimeError: If the local LLM communication fails.
    """
    try:
        response = chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        return response["message"]["content"]
    except Exception as exc:
        raise RuntimeError(f"Failed to communicate with LLM: {exc}") from exc


def parse_llm_json(raw: str) -> dict[str, Any]:
    """Parses the raw LLM response into a valid JSON dictionary.

    Handles optional markdown code fences surrounding the JSON object.

    Args:
        raw: The raw LLM response string.

    Returns:
        The parsed JSON dictionary.

    Raises:
        ValueError: If the raw response is not valid JSON.
    """
    cleaned = raw.strip()

    fence_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    json_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Router returned invalid JSON: {cleaned}") from exc
