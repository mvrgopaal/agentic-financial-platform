"""
Provider-independent LLM contract.
"""

from abc import ABC, abstractmethod

from app.agents.prompt_definition import PromptDefinition


class LLMProvider(ABC):
    """
    Contract implemented by every supported LLM provider.
    """

    @abstractmethod
    def generate(
        self,
        prompt: PromptDefinition,
    ) -> str:
        """
        Generate a response from a structured prompt.
        """
        raise NotImplementedError
