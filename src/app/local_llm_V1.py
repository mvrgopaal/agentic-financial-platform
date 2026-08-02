from openai import OpenAI

LOCAL_MODEL = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="local-mlx",
)


def call_local_llm(
    messages: list[dict[str, str]],
    temperature: float = 0.0,
) -> str:
    """Send messages to the locally running MLX model."""

    response = client.chat.completions.create(
        model=LOCAL_MODEL,
        messages=messages,
        temperature=temperature,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The local model returned an empty response.")

    return content
