"""
Provides access to the application configuration.
"""

from app.configuration.application_config import (
    ApplicationConfig,
)
from app.configuration.configuration_loader import (
    ConfigurationLoader,
)


class ConfigurationManager:
    """
    Loads configuration once and exposes it
    throughout the application.
    """

    def __init__(self) -> None:

        self._configuration = (
            ConfigurationLoader().load()
        )

    @property
    def config(self) -> ApplicationConfig:
        """
        Return the application configuration.
        """

        return self._configuration
