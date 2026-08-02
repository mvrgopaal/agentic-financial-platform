"""
Version-aware registry for Financial AI Agent tools.

Responsibilities:
- Register tool definitions
- Discover available tools
- Resolve a requested version
- Execute a tool implementation
- Return planner-safe metadata
"""

from dataclasses import asdict, is_dataclass
from typing import Any

from app.tools.tool_definition import ToolDefinition
from app.tools.tool_discovery import discover_tools

# Structure:
#
# {
#     "calculate_dti": {
#         "1.0.0": ToolDefinition(...)
#     }
# }
TOOL_REGISTRY: dict[
    str,
    dict[str, ToolDefinition],
] = {}

def load_discovered_tools() -> None:
    """
    Discover and register all installed application tools.
    """

    for tool in discover_tools():
        register_tool(tool)

def register_tool(
    tool: ToolDefinition,
) -> None:
    """
    Register one version of a tool.

    Duplicate name-and-version combinations are rejected.
    """

    versions = TOOL_REGISTRY.setdefault(
        tool.name,
        {},
    )

    if tool.version in versions:
        raise ValueError(
            f"Tool '{tool.name}' version "
            f"'{tool.version}' is already registered."
        )

    versions[tool.version] = tool


def _version_key(
    version: str,
) -> tuple[int, ...]:
    """
    Convert a semantic version string into a sortable tuple.

    Example:
        "1.2.10" -> (1, 2, 10)
    """

    try:
        return tuple(
            int(part)
            for part in version.split(".")
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid semantic version: '{version}'."
        ) from exc


def get_tool(
    name: str,
    version: str | None = None,
) -> ToolDefinition:
    """
    Retrieve a tool by name and optional version.

    When version is omitted, the latest non-deprecated
    registered version is returned.
    """

    versions = TOOL_REGISTRY.get(name)

    if versions is None:
        available = ", ".join(
            sorted(TOOL_REGISTRY)
        )

        raise KeyError(
            f"Unknown tool '{name}'. "
            f"Available tools: {available}"
        )

    if version is not None:
        tool = versions.get(version)

        if tool is None:
            available_versions = ", ".join(
                sorted(
                    versions,
                    key=_version_key,
                )
            )

            raise KeyError(
                f"Tool '{name}' does not have version "
                f"'{version}'. Available versions: "
                f"{available_versions}"
            )

        return tool

    active_tools = [
        tool
        for tool in versions.values()
        if not tool.deprecated
    ]

    if not active_tools:
        raise LookupError(
            f"Tool '{name}' has no active versions."
        )

    return max(
        active_tools,
        key=lambda tool: _version_key(
            tool.version
        ),
    )


def execute_tool(
    tool_name: str,
    parameters: dict[str, Any],
    version: str | None = None,
) -> dict[str, Any]:
    """
    Execute a registered tool.

    The existing execution-engine contract remains compatible:
        execute_tool(tool_name, parameters)

    A specific version may optionally be requested.
    """

    tool = get_tool(
        name=tool_name,
        version=version,
    )

    try:
        result = tool.function(**parameters)

        if is_dataclass(result):
            serialized_result = asdict(result)
        elif isinstance(result, dict):
            serialized_result = result
        else:
            serialized_result = {
                "value": result,
            }

        return {
            "tool": tool.name,
            "version": tool.version,
            "success": True,
            "result": serialized_result,
        }

    except Exception as exc:
        raise RuntimeError(
            f"Tool '{tool.name}' version "
            f"'{tool.version}' failed: {exc}"
        ) from exc


def list_tools() -> list[dict[str, Any]]:
    """
    Return planner-safe metadata for latest active tools.
    """

    return [
        get_tool(name).planner_metadata()
        for name in sorted(TOOL_REGISTRY)
    ]


def list_tool_versions(
    name: str,
) -> list[str]:
    """
    Return all registered versions for a tool.
    """

    versions = TOOL_REGISTRY.get(name)

    if versions is None:
        raise KeyError(
            f"Unknown tool '{name}'."
        )

    return sorted(
        versions,
        key=_version_key,
    )


def _register_builtin_tools() -> None:
    """
    Register tools shipped with the application.
    """

    builtin_tools = (
        DTI_TOOL,
        LTV_TOOL,
        LOAN_AMOUNT_TOOL,
        MONTHLY_PAYMENT_TOOL,
    )

    for tool in builtin_tools:
        register_tool(tool)

def find_tools_by_capability(
    capability: str,
) -> list[ToolDefinition]:
    """
    Return active tools that advertise the requested capability.
    """

    normalized_capability = capability.strip().lower()

    if not normalized_capability:
        raise ValueError(
            "Capability cannot be empty."
        )

    matching_tools: list[ToolDefinition] = []

    for tool_name in TOOL_REGISTRY:
        tool = get_tool(tool_name)

        normalized_capabilities = {
            item.strip().lower()
            for item in tool.capabilities
        }

        if normalized_capability in normalized_capabilities:
            matching_tools.append(tool)

    return sorted(
        matching_tools,
        key=lambda tool: (
            tool.estimated_cost,
            tool.name,
        ),
    )


def search_tools(
    *,
    capabilities: tuple[str, ...] = (),
    category: str | None = None,
    tags: tuple[str, ...] = (),
) -> list[ToolDefinition]:
    """
    Search active tools using planner-visible metadata.

    All supplied filters must match.
    """

    normalized_capabilities = {
        item.strip().lower()
        for item in capabilities
    }

    normalized_tags = {
        item.strip().lower()
        for item in tags
    }

    normalized_category = (
        category.strip().lower()
        if category
        else None
    )

    matches: list[ToolDefinition] = []

    for tool_name in TOOL_REGISTRY:
        tool = get_tool(tool_name)

        tool_capabilities = {
            item.strip().lower()
            for item in tool.capabilities
        }

        tool_tags = {
            item.strip().lower()
            for item in tool.tags
        }

        tool_category = tool.category.strip().lower()

        if (
            normalized_capabilities
            and not normalized_capabilities.issubset(
                tool_capabilities
            )
        ):
            continue

        if (
            normalized_tags
            and not normalized_tags.issubset(
                tool_tags
            )
        ):
            continue

        if (
            normalized_category
            and tool_category != normalized_category
        ):
            continue

        matches.append(tool)

    return sorted(
        matches,
        key=lambda tool: (
            tool.estimated_cost,
            tool.name,
        ),
    )

def list_tool_definitions() -> list[ToolDefinition]:
    """
    Return the latest active ToolDefinition for every registered tool.

    Intended for internal orchestration components such as
    dependency builders and execution engines.
    """
    definitions: list[ToolDefinition] = []

    for tool_name in sorted(TOOL_REGISTRY):
        tool = get_tool(tool_name)

        if tool.deprecated:
            continue

        definitions.append(tool)

    return definitions

load_discovered_tools()

if __name__ == "__main__":
    from pprint import pprint

    print("\nRegistered tools:")
    pprint(list_tools())

    print("\nDTI versions:")
    pprint(
        list_tool_versions(
            "calculate_dti"
        )
    )

    print("\nExecute latest DTI:")
    pprint(
        execute_tool(
            "calculate_dti",
            {
                "monthly_income": 12000,
                "monthly_debt": 2500,
            },
        )
    )

    print("\nExecute DTI version 1.0.0:")
    pprint(
        execute_tool(
            "calculate_dti",
            {
                "monthly_income": 12000,
                "monthly_debt": 2500,
            },
            version="1.0.0",
        )
    )
print("\nMortgage prequalification tools:")

for tool in find_tools_by_capability(
    "mortgage_prequalification"
):
    print(
        f"- {tool.name} "
        f"v{tool.version}"
    )
