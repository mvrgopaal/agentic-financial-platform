"""
Loads the application configuration from YAML.
"""

from pathlib import Path

import yaml

from app.configuration.application_config import (
    ApplicationConfig,
    LLMConfig,
    LoggingConfig,
    RetrievalConfig,
)


class ConfigurationLoader:
    """
    Loads application configuration.
    """

    def load(
        self,
        path: str = "application.yaml",
    ) -> ApplicationConfig:

        config_path = Path(path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {path}"
            )

        with config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            raw = yaml.safe_load(file)

        return ApplicationConfig(
            environment=raw.get(
                "environment",
                "development",
            ),
            llm=LLMConfig(**raw.get("llm", {})),
            retrieval=RetrievalConfig(
                **raw.get("retrieval", {})
            ),
            logging=LoggingConfig(
                **raw.get("logging", {})
            ),
        )
