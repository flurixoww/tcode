import os

from ai_agent.sub_agents.agent_prompts import main_model_prompt, router_prompt
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
    """
    Function that connects user prompt with a specific model prompt.

    Args:
        user_prompt (str): User's prompt.
        model_prompt (str): Basic model prompt.

    Returns:
        str: Unified prompt.

    Raises:
        RuntimeError: If there was a problem during a connection of both prompts.
    """

    try:
        unified_prompt = f"Model prompt: {model_prompt} User prompt: {user_prompt}"
        return unified_prompt
    except Exception as e:
        raise RuntimeError(f"Error occured when working with the prompts {e}") from e


def main():
    user_prompt = input("Ask: ")
    unified_prompts = prompts_connection(user_prompt, router_prompt())
    raw_model_response = route(unified_prompts)
    json_model_response = parse_llm_json(raw_model_response)
    addressed_files = exact_file_address(user_prompt)

    if len(addressed_files) > 0:
        print("Using files referenced in the prompt.")
        files_content = {}
        path_to_files = exact_file_path(addressed_files, ignored_files_info())
        for file_path in path_to_files:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                files_content[file_path] = file_content

        response = main_model(
            f"{main_model_prompt} User prompt: {user_prompt} Code chunks: {files_content}"
        )
        print(response)

    elif json_model_response["decision"] == "file":
        print("Using access to the files to give an answer...")
        initialized_chroma_client = chroma_client_initialization()
        intialized_code_splitter = code_aware_splitter()
        files_in_chunks = file_info(
            os.getcwd(), intialized_code_splitter, ignored_files_info()
        )
        chromadb_batch_upsert(
            files_in_chunks[0],
            files_in_chunks[1],
            files_in_chunks[2],
            initialized_chroma_client,
        )

        found_file_distance = (
            find_closest_files(initialized_chroma_client, user_prompt),
        )

        ids_for_model = likely_files(
            found_file_distance[0][0],
            found_file_distance[0][1],
            found_file_distance[0][2],
        )

        response = main_model(
            f"{main_model_prompt} User prompt: {user_prompt} Code chunks: {ids_for_model}"
        )
        print(response)

    else:
        print("Using general knowledge to asnwer the question?")
        response = main_model(user_prompt)
        print(response)


def test():
    initialized_chroma_client = chroma_client_initialization()
    intialized_code_splitter = code_aware_splitter()
    files_in_chunks = file_info(
        os.getcwd(), intialized_code_splitter, ignored_files_file_info()
    )
    chromadb_batch_upsert(
        files_in_chunks[0],
        files_in_chunks[1],
        files_in_chunks[2],
        initialized_chroma_client,
    )

    found_file_distance = (
        find_closest_files(
            initialized_chroma_client, "How do I fix the likely files function? "
        ),
    )

    ids_for_model = likely_files(
        found_file_distance[0][0], found_file_distance[0][1], found_file_distance[0][2]
    )

    for id in ids_for_model:
        print(id, ids_for_model[id])


if __name__ == "__main__":
    main()
