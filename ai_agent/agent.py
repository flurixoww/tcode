from ai_agent.sub_agents.agent_prompts import router_prompt
from ai_agent.sub_agents.file_search import (
    chroma_client_initialization,
    file_distance,
    file_info,
    likely_files,
)
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
    # 1. Get the prompt and connect them
    # 2. Send the connected prompts to the routing model
    # 3. If it is the file
    #   1. We initialize the chroma client
    #   2. We find info about files
    #   3. We find distance of the prompt to the files
    #   4. We find likely files to the prompt.
    #   5. We send likely files content and the prompt directly to the model
    #
    # 4. If it is the general ques
    #   1. We send it directly to the model
    user_prompt = input("Ask: ")
    unified_prompts = prompts_connection(user_prompt, router_prompt())
    raw_model_response = route(unified_prompts)
    json_model_response = parse_llm_json(raw_model_response)

    if json_model_response["decision"] == "file":
        file_ids_content = file_info()

        chroma_files_collection_architecture = chroma_client_initialization(
            file_ids_content[0], file_ids_content[1]
        )

        distance_to_the_files = file_distance(
            chroma_files_collection_architecture, user_prompt
        )

        files_possibility = likely_files(
            distance_to_the_files[0], distance_to_the_files[1]
        )

        # Then it is passed to the main model

    else:
        None
        # Then it is passed to the main model


if __name__ == "__main__":
    main()
