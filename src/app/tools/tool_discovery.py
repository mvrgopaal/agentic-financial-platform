"""
Dynamic discovery of ToolDefinition objects.

This version scans the app.tools package, imports tool modules,
finds ToolDefinition instances, and returns them to the registry.

The registry does not need to know individual tool names.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

import app.tools
from app.tools.tool_definition import ToolDefinition


EXCLUDED_MODULES = {
    "__init__",
    "tool_definition",
    "tool_discovery",
    "tool_registry",
    "tool_metadata",
}


class ToolDiscoveryError(RuntimeError):
    """Raised when tool discovery cannot complete safely."""


def discover_tools() -> list[ToolDefinition]:
    """
    Discover every ToolDefinition in the app.tools package.

    Returns:
        A list of discovered tool definitions.

    Raises:
        ToolDiscoveryError:
            If a module cannot be imported or duplicate tool
            definitions are discovered.
    """

    discovered_tools: list[ToolDefinition] = []

    for module_name in _discover_module_names():
        module = _import_tool_module(module_name)
        discovered_tools.extend(
            _find_tool_definitions(module)
        )

    _validate_unique_definitions(discovered_tools)

    return discovered_tools


def _discover_module_names() -> list[str]:
    """
    Return importable module names inside app.tools.
    """

    package_path = app.tools.__path__
    package_prefix = f"{app.tools.__name__}."

    module_names: list[str] = []

    for module_info in pkgutil.iter_modules(
        package_path,
        package_prefix,
    ):
        short_name = module_info.name.rsplit(".", 1)[-1]

        if short_name in EXCLUDED_MODULES:
            continue

        if short_name.startswith("_"):
            continue

        if short_name.endswith("_V1"):
            continue

        if short_name.endswith("_V2"):
            continue

        module_names.append(module_info.name)

    return sorted(module_names)


def _import_tool_module(
    module_name: str,
) -> ModuleType:
    """
    Import one tool module.
    """

    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        raise ToolDiscoveryError(
            f"Failed to import tool module "
            f"'{module_name}': {exc}"
        ) from exc


def _find_tool_definitions(
    module: ModuleType,
) -> list[ToolDefinition]:
    """
    Find ToolDefinition objects declared directly in a module.

    Imported ToolDefinition objects are ignored so the same tool
    is not discovered repeatedly.
    """

    tools: list[ToolDefinition] = []

    for _, value in inspect.getmembers(module):
        if not isinstance(value, ToolDefinition):
            continue

        function_module = getattr(
            value.function,
            "__module__",
            None,
        )

        if function_module != module.__name__:
            continue

        tools.append(value)

    return tools


def _validate_unique_definitions(
    tools: list[ToolDefinition],
) -> None:
    """
    Reject duplicate tool name-and-version combinations.
    """

    seen: set[tuple[str, str]] = set()

    for tool in tools:
        identity = (
            tool.name,
            tool.version,
        )

        if identity in seen:
            raise ToolDiscoveryError(
                f"Duplicate tool discovered: "
                f"'{tool.name}' version '{tool.version}'."
            )

        seen.add(identity)


if __name__ == "__main__":
    for discovered_tool in discover_tools():
        print(
            f"{discovered_tool.name} "
            f"v{discovered_tool.version}"
        )
