"""
Typed application configuration for the Agentic Financial Platform.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class LLMConfig:
    """
    Configuration for the selected LLM provider.
    """

    provider: str = "openai"
    model: str = "gpt-4.1"
    temperature: float = 0.0
    base_url: str | None = None


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    """
    Configuration for mortgage-knowledge retrieval.
    """

    top_k: int = 5


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """
    Basic logging configuration.
    """

    level: str = "INFO"


@dataclass(frozen=True, slots=True)
class ApplicationConfig:
    """
    Root configuration object for the platform.
    """

    environment: str = "development"
    llm: LLMConfig = field(default_factory=LLMConfig)
    retrieval: RetrievalConfig = field(
        default_factory=RetrievalConfig
    )
    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )
