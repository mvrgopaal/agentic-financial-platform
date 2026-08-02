import json
from typing import Any

from app.local_llm import call_local_llm
from app.rag.retriever import search_documents
from app.tools.dti_calculator import calculate_dti


AGENT_SYSTEM_PROMPT = """
You are a local mortgage AI assistant.

You can choose exactly one of these actions:

1. calculate_dti
   Use when the user provides monthly debt and gross monthly income.

2. search_guidelines
   Use when the user asks about mortgage or underwriting rules.

3. answer_directly
   Use for greetings or general explanations that do not require a tool.

Return valid JSON only.

For calculate_dti:
{
  "action": "calculate_dti",
  "arguments": {
    "monthly_debt": 3400,
    "gross_monthly_income": 8000
  }
}

For search_guidelines:
{
  "action": "search_guidelines",
  "arguments": {
    "query": "debts included in the qualifying ratio"
  }
}

For answer_directly:
{
  "action": "answer_directly",
  "arguments": {
    "answer": "Your answer"
  }
}

Do not include Markdown or text outside the JSON.
"""


def parse_agent_decision(raw_response: str) -> dict[str, Any]:
    """Validate the model's requested action."""

    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json")
        cleaned = cleaned.removeprefix("```")
        cleaned = cleaned.removesuffix("```").strip()

    try:
        decision = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON: {raw_response}"
        ) from exc

    action = decision.get("action")
    arguments = decision.get("arguments", {})

    allowed_actions = {
        "calculate_dti",
        "search_guidelines",
        "answer_directly",
    }

    if action not in allowed_actions:
        raise ValueError(f"Unsupported agent action: {action}")

    if not isinstance(arguments, dict):
        raise ValueError("Agent arguments must be a JSON object.")

    return {
        "action": action,
        "arguments": arguments,
    }


def format_documents(documents: list[Any]) -> str:
    """Convert retrieved LangChain documents into readable context."""

    sections = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get(
            "page_label",
            document.metadata.get("page", "Unknown page"),
        )

        sections.append(
            f"Source {index}\n"
            f"File: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{document.page_content}"
        )

    return "\n\n".join(sections)


def execute_action(
    action: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Execute only approved local tools."""

    if action == "calculate_dti":
        return calculate_dti(
            monthly_debt=float(arguments["monthly_debt"]),
            gross_monthly_income=float(
                arguments["gross_monthly_income"]
            ),
        )

    if action == "search_guidelines":
        query = str(arguments["query"])
        documents = search_documents(query, k=5)

        return {
            "query": query,
            "context": format_documents(documents),
        }

    if action == "answer_directly":
        return {
            "answer": str(arguments["answer"]),
        }

    raise ValueError(f"Unknown action: {action}")


def run_agent(user_question: str) -> str:
    """Plan, execute a tool when needed, and produce the final answer."""

    planning_messages = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_question,
        },
    ]

    raw_decision = call_local_llm(planning_messages)
    decision = parse_agent_decision(raw_decision)

    action = decision["action"]

    if action == "answer_directly":
        return str(decision["arguments"]["answer"])

    tool_result = execute_action(
        action=action,
        arguments=decision["arguments"],
    )

    final_messages = [
        {
            "role": "system",
            "content": (
                "You are a mortgage assistant. "
                "Answer using only the supplied tool result. "
                "Do not invent guideline rules. "
                "When document sources are supplied, cite their pages. "
                "Clearly state when the evidence is insufficient."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original question:\n{user_question}\n\n"
                f"Tool used:\n{action}\n\n"
                f"Tool result:\n"
                f"{json.dumps(tool_result, indent=2)}"
            ),
        },
    ]

    return call_local_llm(final_messages)
