"""
Local MLX implementation of the LLMProvider contract.
"""

from app.agents.prompt_definition import PromptDefinition
from app.local_llm import call_local_llm
from app.providers.llm.provider import LLMProvider


class MLXProvider(LLMProvider):
    """
    Generate reasoning responses using the local MLX server.
    """

    def generate(
        self,
        prompt: PromptDefinition,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": prompt.system_prompt,
            },
            {
                "role": "user",
                "content": self._build_user_content(prompt),
            },
        ]

        return call_local_llm(
            messages=messages,
            temperature=0.0,
        )

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
