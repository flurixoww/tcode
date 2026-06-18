from ollama import chat


def route(prompt: str):
    response = chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content
