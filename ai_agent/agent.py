from ai_agent.sub_agents.agent_prompts import router_prompt
from ai_agent.sub_agents.file_search import file_distance, file_info
from ai_agent.sub_agents.router import parse_llm_json, route


def main():
    user_prompt = "What deadline did I set for the history presentation?"

    response = parse_llm_json(route(router_prompt() + user_prompt))

    if response["decision"] == "file":
        files = file_info()
        file_prediction = file_distance(files[0], files[1], user_prompt)


if __name__ == "__main__":
    main()
