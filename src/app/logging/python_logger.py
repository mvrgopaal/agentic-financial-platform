"""
Python standard-library logging adapter.
"""

import json
import logging
from typing import Any

from app.logging.platform_logger import PlatformLogger


class PythonLogger(PlatformLogger):
    """
    Platform logger backed by Python's logging module.
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
    ) -> None:
        self._logger = logging.getLogger(name)

        normalized_level = level.strip().upper()
        numeric_level = getattr(
            logging,
            normalized_level,
            None,
        )

        if not isinstance(numeric_level, int):
            raise ValueError(
                f"Unsupported logging level: {level!r}"
            )

        self._logger.setLevel(numeric_level)
        self._logger.propagate = False

        if not self._logger.handlers:
            handler = logging.StreamHandler()

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            )

            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def debug(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._logger.debug(
            self._format_message(message, context)
        )

    def info(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._logger.info(
            self._format_message(message, context)
        )

    def warning(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._logger.warning(
            self._format_message(message, context)
        )

    def error(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._logger.error(
            self._format_message(message, context)
        )

    def exception(
        self,
        message: str,
        **context: Any,
    ) -> None:
        self._logger.exception(
            self._format_message(message, context)
        )

    def _format_message(
        self,
        message: str,
        context: dict[str, Any],
    ) -> str:
        """
        Append structured context as JSON.
        """

        if not context:
            return message

        serialized_context = json.dumps(
            context,
            default=str,
            sort_keys=True,
        )

        return f"{message} | context={serialized_context}"
