"""
Provider-independent logging contract.
"""

from abc import ABC, abstractmethod
from typing import Any


class PlatformLogger(ABC):
    """
    Logging capability used by platform components.

    Business code depends on this abstraction rather than
    directly depending on Python's logging implementation.
    """

    @abstractmethod
    def debug(
        self,
        message: str,
        **context: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def info(
        self,
        message: str,
        **context: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(
        self,
        message: str,
        **context: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(
        self,
        message: str,
        **context: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def exception(
        self,
        message: str,
        **context: Any,
    ) -> None:
        raise NotImplementedError
