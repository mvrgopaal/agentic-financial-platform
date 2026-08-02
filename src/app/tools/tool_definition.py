"""
Shared definition model for tools exposed by the Financial AI Agent.

A ToolDefinition is the single source of truth for:
- Tool identity
- Version
- Description
- Input and output schemas
- Business capabilities
- Execution behavior
- Lifecycle information
- Python implementation
"""

from dataclasses import dataclass, field
from typing import Any, Callable


ToolFunction = Callable[..., Any]


@dataclass(frozen=True)
class ToolDefinition:
    """
    Describes a tool that can be discovered by a planner
    and executed by the tool registry.
    """

    name: str
    version: str
    description: str
    function: ToolFunction = field(repr=False)

    input_schema: dict[str, Any] = field(
        default_factory=dict
    )
    output_schema: dict[str, Any] = field(
        default_factory=dict
    )

    capabilities: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()

    category: str = "general"

    side_effects: bool = False
    parallel_safe: bool = True

    timeout_seconds: int = 30
    estimated_cost: float = 0.0

    deprecated: bool = False
    replacement_tool: str | None = None

    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the tool definition when it is created.
        """

        if not self.name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        if not self.version.strip():
            raise ValueError(
                "Tool version cannot be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "Tool description cannot be empty."
            )

        if not callable(self.function):
            raise TypeError(
                "Tool function must be callable."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "Tool timeout must be greater than zero."
            )

        if self.estimated_cost < 0:
            raise ValueError(
                "Estimated cost cannot be negative."
            )

        if (
            self.deprecated
            and not self.replacement_tool
        ):
            raise ValueError(
                "A deprecated tool must identify its "
                "replacement tool."
            )

    def planner_metadata(self) -> dict[str, Any]:
        """
        Return metadata that may safely be exposed to a planner.

        The Python function itself is intentionally excluded.
        """

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "capabilities": list(
                self.capabilities
            ),
            "requires": list(self.requires),
            "produces": list(self.produces),
            "category": self.category,
            "side_effects": self.side_effects,
            "parallel_safe": self.parallel_safe,
            "timeout_seconds": self.timeout_seconds,
            "estimated_cost": self.estimated_cost,
            "deprecated": self.deprecated,
            "replacement_tool": self.replacement_tool,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }
