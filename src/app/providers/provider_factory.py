"""
Factory responsible for creating the configured LLM provider.
"""

from app.configuration.configuration_manager import (
    ConfigurationManager,
)
from app.providers.llm.provider import LLMProvider
from app.providers.llm.openai_provider import OpenAIProvider
from app.providers.llm.mlx_provider import MLXProvider


class ProviderFactory:
    """
    Creates the configured LLM provider.
    """

    def __init__(
        self,
        configuration_manager: ConfigurationManager,
    ) -> None:

        self.configuration_manager = configuration_manager

    def create_llm_provider(
        self,
    ) -> LLMProvider:

        provider_name = (
            self.configuration_manager
            .config
            .llm
            .provider
            .lower()
        )

        if provider_name == "openai":
            return OpenAIProvider()

        if provider_name == "mlx":
            return MLXProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider_name}"
        )
