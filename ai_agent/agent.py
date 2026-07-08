import os
from typing import Dict, List

from ai_agent.sub_agents.agent_prompts import MAIN_MODEL_PROMPT, ROUTER_PROMPT
from ai_agent.sub_agents.file_address import exact_file_address, exact_file_path
from ai_agent.sub_agents.file_search import (
    chroma_client_initialization,
    chromadb_batch_upsert,
    code_aware_splitter,
    file_info,
    find_closest_files,
    ignored_files_info,
    likely_files,
)
from ai_agent.sub_agents.main_model import main_model
from ai_agent.sub_agents.router import parse_llm_json, route


def prompts_connection(user_prompt: str, model_prompt: str) -> str:
    """Connects user prompt with a specific model prompt.

    Args:
        user_prompt: User's prompt.
        model_prompt: Basic model prompt.

    Returns:
        Unified prompt.

    Raises:
        RuntimeError: If there was a problem during a connection of both prompts.
    """
    try:
        unified_prompt = f"Model prompt: {model_prompt} User prompt: {user_prompt}"
        return unified_prompt
    except Exception as e:
        raise RuntimeError(f"Error occured when working with the prompts {e}") from e


def _handle_referenced_files(user_prompt: str, addressed_files: List[str]) -> None:
    """Reads specific files referenced in the prompt and queries the main model.

    Args:
        user_prompt: The user's prompt.
        addressed_files: List of referenced file names/addresses.
    """
    print("Using files referenced in the prompt.")
    files_content: Dict[str, str] = {}
    path_to_files = exact_file_path(addressed_files, ignored_files_info())
    for file_path in path_to_files:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            files_content[file_path] = file_content

    response = main_model(
        f"{MAIN_MODEL_PROMPT} User prompt: {user_prompt} Code chunks: {files_content}"
    )
    print(response)


def _handle_file_search(user_prompt: str) -> None:
    """Performs semantic search over files using Chroma and queries the main model.

    Args:
        user_prompt: The user's prompt.
    """
    print("Using access to the files to give an answer...")
    initialized_chroma_client = chroma_client_initialization()
    initialized_code_splitter = code_aware_splitter()
    files_in_chunks = file_info(
        os.getcwd(), initialized_code_splitter, ignored_files_info()
    )
    chromadb_batch_upsert(
        files_in_chunks[0],
        files_in_chunks[1],
        files_in_chunks[2],
        initialized_chroma_client,
    )

    ids, distances, documents = find_closest_files(
        initialized_chroma_client, user_prompt
    )

    ids_for_model = likely_files(ids, distances, documents)

    response = main_model(
        f"{MAIN_MODEL_PROMPT} User prompt: {user_prompt} Code chunks: {ids_for_model}"
    )
    print(response)


def _handle_general_knowledge(user_prompt: str) -> None:
    """Queries the main model using general knowledge without local file context.

    Args:
        user_prompt: The user's prompt.
    """
    print("Using general knowledge to asnwer the question.")
    response = main_model(user_prompt)
    print(response)


def main() -> None:
    """Prompts the user, routes the request, and executes the appropriate flow."""
    user_prompt = input("Ask: ")
    unified_prompts = prompts_connection(user_prompt, ROUTER_PROMPT)
    raw_model_response = route(unified_prompts)
    json_model_response = parse_llm_json(raw_model_response)
    addressed_files = exact_file_address(user_prompt)

    if len(addressed_files) > 0:
        _handle_referenced_files(user_prompt, addressed_files)
    elif json_model_response["decision"] == "file":
        _handle_file_search(user_prompt)
    else:
        _handle_general_knowledge(user_prompt)


if __name__ == "__main__":
    main()
