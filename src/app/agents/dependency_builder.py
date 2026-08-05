"""
Build dependency graphs for selected financial tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.tools.tool_definition import ToolDefinition
from app.tools.tool_registry import list_tool_definitions


@dataclass
class DependencyGraph:
    """
    Represents dependencies between selected tools.

    The dictionary maps:
        tool_name -> tools that must execute first
    """

    dependencies: dict[str, set[str]] = field(default_factory=dict)

    def add_node(self, tool: str) -> None:
        """Add a tool to the graph when it is not already present."""

        self.dependencies.setdefault(tool, set())

    def add_dependency(
        self,
        tool: str,
        depends_on: str,
    ) -> None:
        """Declare that one tool depends on another tool."""

        self.add_node(tool)
        self.add_node(depends_on)
        self.dependencies[tool].add(depends_on)

    def get_dependencies(self, tool: str) -> set[str]:
        """Return a copy of the dependencies for one tool."""

        return set(self.dependencies.get(tool, set()))

    def get_root_nodes(self) -> list[str]:
        """Return all tools that have no dependencies."""

        return sorted(
            tool
            for tool, dependencies in self.dependencies.items()
            if not dependencies
        )

    def get_leaf_nodes(self) -> list[str]:
        """Return all tools that no other tool depends on."""

        leaves = set(self.dependencies)

        for dependencies in self.dependencies.values():
            for dependency in dependencies:
                leaves.discard(dependency)

        return sorted(leaves)

    def topological_sort(self) -> list[str]:
        """
        Return tools in valid dependency order.

        Raise ValueError when the graph contains a cycle.
        """

        remaining = {
            node: set(dependencies)
            for node, dependencies in self.dependencies.items()
        }

        execution_order: list[str] = []

        while remaining:
            roots = sorted(
                node
                for node, dependencies in remaining.items()
                if not dependencies
            )

            if not roots:
                raise ValueError(
                    "Cycle detected in dependency graph."
                )

            execution_order.extend(roots)

            for root in roots:
                remaining.pop(root)

            for dependencies in remaining.values():
                dependencies.difference_update(roots)

        return execution_order

    def parallel_execution_groups(self) -> list[list[str]]:
        """
        Return execution stages.

        Every tool within one stage can execute in parallel.
        """

        remaining = {
            node: set(dependencies)
            for node, dependencies in self.dependencies.items()
        }

        execution_groups: list[list[str]] = []

        while remaining:
            roots = sorted(
                node
                for node, dependencies in remaining.items()
                if not dependencies
            )

            if not roots:
                raise ValueError(
                    "Cycle detected in dependency graph."
                )

            execution_groups.append(roots)

            for root in roots:
                remaining.pop(root)

            for dependencies in remaining.values():
                dependencies.difference_update(roots)

        return execution_groups

    def __str__(self) -> str:
        lines: list[str] = []

        for tool in sorted(self.dependencies):
            dependencies = self.dependencies[tool]

            if not dependencies:
                lines.append(tool)
                continue

            for dependency in sorted(dependencies):
                lines.append(f"{dependency} -> {tool}")

        return "\n".join(lines)


class DependencyBuilder:
    """Build tool dependencies from declared inputs and outputs."""

    def build(
        self,
        tools: list[ToolDefinition],
    ) -> DependencyGraph:
        """
        Build a dependency graph for the selected tools.

        A dependency is created when one selected tool produces
        an input required by another selected tool.
        """

        graph = DependencyGraph()
        produced_outputs: dict[str, str] = {}

        for tool in tools:
            graph.add_node(tool.name)

            for output_name in tool.produces:
                produced_outputs[output_name] = tool.name

        for tool in tools:
            for required_input in tool.requires:
                producer = produced_outputs.get(required_input)

                # The input is supplied externally.
                if producer is None:
                    continue

                # A tool cannot depend on itself.
                if producer == tool.name:
                    continue

                graph.add_dependency(
                    tool=tool.name,
                    depends_on=producer,
                )

        return graph


if __name__ == "__main__":
    builder = DependencyBuilder()

    graph = builder.build(
        list_tool_definitions()
    )

    print("\nDependency Graph")
    print("----------------")
    print(graph)

    print("\nRoot Nodes")
    print("----------")

    for node in graph.get_root_nodes():
        print(node)

    print("\nLeaf Nodes")
    print("----------")

    for node in graph.get_leaf_nodes():
        print(node)

    print("\nTopological Order")
    print("-----------------")

    for tool in graph.topological_sort():
        print(tool)

    print("\nParallel Execution Groups")
    print("-------------------------")

    for index, group in enumerate(
        graph.parallel_execution_groups(),
        start=1,
    ):
        print(f"Stage {index}: {group}")
