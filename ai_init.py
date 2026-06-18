from ollama import chat


def ask_ai(prompt):
    token_limit = 4096
    response = chat(
        model="qwen2.5:0.5b",
        messages=[{"role": "user", "content": prompt}],
        options={"num_ctx": token_limit},
    )

    input_tokens = response.prompt_eval_count or 0
    output_tokens = response.eval_count or 0
    current_tokens = input_tokens + output_tokens
    percent_used = round((current_tokens / token_limit) * 100) if token_limit else 0

    token_usage = f"Tokens used {current_tokens} out of {token_limit}\n{percent_used}%"

    return response.message.content, token_usage
