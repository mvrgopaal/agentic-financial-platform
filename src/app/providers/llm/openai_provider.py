"""
OpenAI implementation of the LLMProvider contract.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompt_definition import PromptDefinition
from app.llm import llm
from app.providers.llm.provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Generate reasoning responses using the configured ChatOpenAI model.
    """

    def generate(
        self,
        prompt: PromptDefinition,
    ) -> str:
        messages = [
            SystemMessage(
                content=prompt.system_prompt
            ),
            HumanMessage(
                content=self._build_user_content(prompt)
            ),
        ]

        response = llm.invoke(messages)

        content = getattr(response, "content", None)

        if not content:
            raise RuntimeError(
                "OpenAI returned an empty response."
            )

        if isinstance(content, str):
            return content.strip()

        return str(content).strip()

    def _build_user_content(
        self,
        prompt: PromptDefinition,
    ) -> str:
        guidelines = self._format_guidelines(
            prompt.retrieved_guidelines
        )

        return (
            f"USER QUESTION\n"
            f"{prompt.user_prompt}\n\n"
            f"VERIFIED FINANCIAL INFORMATION\n"
            f"{prompt.context_summary}\n\n"
            f"RETRIEVED MORTGAGE GUIDELINES\n"
            f"{guidelines}\n\n"
            f"REASONING INSTRUCTIONS\n"
            f"{prompt.reasoning_instructions}\n\n"
            f"OUTPUT INSTRUCTIONS\n"
            f"{prompt.output_instructions}"
        )

    def _format_guidelines(
        self,
        guidelines: list[str],
    ) -> str:
        if not guidelines:
            return "No guideline excerpts were retrieved."

        return "\n\n".join(
            f"Guideline {index}\n{guideline}"
            for index, guideline in enumerate(
                guidelines,
                start=1,
            )
        )
