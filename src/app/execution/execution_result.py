from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    """
    Represents the outcome of executing a single tool.
    """

    tool_name: str
    success: bool
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
