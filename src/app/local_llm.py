from typing import Any

from openai import OpenAI


LOCAL_MODEL = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="local-mlx",
)


def normalize_messages_for_mistral(
    messages: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Convert OpenAI-style system messages into a Mistral-compatible
    user/assistant alternating conversation.
    """

    system_instructions: list[str] = []
    normalized: list[dict[str, str]] = []

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role == "system":
            system_instructions.append(content)
        else:
            normalized.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    if system_instructions:
        combined_system_prompt = "\n\n".join(system_instructions)

        if normalized and normalized[0]["role"] == "user":
            normalized[0]["content"] = (
                "INSTRUCTIONS:\n"
                f"{combined_system_prompt}\n\n"
                "USER REQUEST:\n"
                f"{normalized[0]['content']}"
            )
        else:
            normalized.insert(
                0,
                {
                    "role": "user",
                    "content": (
                        "INSTRUCTIONS:\n"
                        f"{combined_system_prompt}"
                    ),
                },
            )

    validate_message_roles(normalized)

    return normalized


def validate_message_roles(
    messages: list[dict[str, str]],
) -> None:
    """
    Verify that messages follow:
    user -> assistant -> user -> assistant...
    """

    expected_role = "user"

    for index, message in enumerate(messages):
        actual_role = message.get("role")

        if actual_role != expected_role:
            raise ValueError(
                f"Invalid role at message {index}: "
                f"expected '{expected_role}', received '{actual_role}'."
            )

        expected_role = (
            "assistant"
            if expected_role == "user"
            else "user"
        )


def call_local_llm(
    messages: list[dict[str, str]],
    temperature: float = 0.0,
) -> str:
    """Send a Mistral-compatible request to the local MLX server."""

    normalized_messages = normalize_messages_for_mistral(messages)

    response: Any = client.chat.completions.create(
        model=LOCAL_MODEL,
        messages=normalized_messages,
        temperature=temperature,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The local model returned an empty response.")

    return content
