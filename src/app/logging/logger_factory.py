"""
Factory for creating configured platform loggers.
"""

from app.configuration.application_config import (
    ApplicationConfig,
)
from app.logging.platform_logger import PlatformLogger
from app.logging.python_logger import PythonLogger


class LoggerFactory:
    """
    Create platform loggers using application configuration.
    """

    def create(
        self,
        name: str,
        config: ApplicationConfig,
    ) -> PlatformLogger:
        if not name.strip():
            raise ValueError(
                "Logger name cannot be empty."
            )

        return PythonLogger(
            name=name.strip(),
            level=config.logging.level,
        )
