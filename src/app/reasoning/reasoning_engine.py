"""
Provider-independent reasoning engine.
"""

from app.agents.prompt_definition import PromptDefinition
from app.providers.llm.provider import LLMProvider
from app.reasoning.reasoning_result import ReasoningResult


class ReasoningEngine:
    """
    Generate a grounded response through an injected LLM provider.
    """

    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self.provider = provider

    def reason(
        self,
        prompt: PromptDefinition,
    ) -> ReasoningResult:
        """
        Generate a reasoning response from the structured prompt.
        """

        try:
            answer = self.provider.generate(prompt)

            return ReasoningResult(
                success=True,
                answer=answer.strip(),
                error=None,
            )

        except Exception as exc:
            return ReasoningResult(
                success=False,
                answer="",
                error=str(exc),
            )
