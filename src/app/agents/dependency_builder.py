from dataclasses import dataclass, field
from app.tools.tool_registry import list_tool_definitions
from app.tools.tool_definition import ToolDefinition

@dataclass
class DependencyGraph:
    """
    Represents dependencies between selected tools.
    """

    dependencies: dict[str, set[str]] = field(default_factory=dict)

    def add_dependency(
        self,
        tool: str,
        depends_on: str,
    ) -> None:

        self.dependencies.setdefault(tool, set()).add(depends_on)

    def get_dependencies(
        self,
        tool: str,
    ) -> set[str]:

        return self.dependencies.get(tool, set())

    def __str__(self):

        lines = []

        for tool, deps in self.dependencies.items():

            if not deps:
                lines.append(f"{tool}")

            for dep in sorted(deps):
                lines.append(f"{dep} -> {tool}")

        return "\n".join(lines)

    def get_root_nodes(self) -> list[str]:
        """
        Return all nodes with no dependencies.
        """

        roots = []

        for tool, deps in self.dependencies.items():

            if not deps:
                roots.append(tool)

        return sorted(roots)
    def get_leaf_nodes(self) -> list[str]:
        """
        Return all nodes that nothing depends on.
        """

        leaves = set(self.dependencies.keys())

        #
        # Every dependency is not a leaf
        #
        for deps in self.dependencies.values():

            for dependency in deps:
                leaves.discard(dependency)

        return sorted(leaves)

    def topological_sort(self) -> list[str]:

        remaining = {
            node: set(deps)
            for node, deps in self.dependencies.items()
        }

        execution_order = []

        while remaining:

            roots = sorted(
                node
                for node, deps in remaining.items()
                if not deps
            )

            if not roots:
                raise ValueError("Cycle detected in dependency graph")

            execution_order.extend(roots)

            #
            # Remove completed nodes
            #
            for root in roots:
                remaining.pop(root)

            #
            # Remove dependencies on completed nodes
            #
            for deps in remaining.values():
                deps.difference_update(roots)

        return execution_order

    def parallel_execution_groups(self) -> list[list[str]]:
        """
        Return execution stages where each stage contains
        tools that can run in parallel.
        """

        # Work on a copy so the original graph is unchanged
        remaining = {
            node: set(deps)
            for node, deps in self.dependencies.items()
        }

        execution_groups = []

        while remaining:

            # Find all tools that have no remaining dependencies
                roots = sorted(
                node
                for node, deps in remaining.items()
                if not deps
            )

                if not roots:
                    raise ValueError("Cycle detected in dependency graph")

                # This entire group can execute in parallel
                execution_groups.append(roots)

            # Remove executed nodes
                for root in roots:
                    remaining.pop(root)

            # Remove satisfied dependencies
                for deps in remaining.values():
                    deps.difference_update(roots)

        return execution_groups

class DependencyBuilder:

    def build(
        self,
        tools: list[ToolDefinition],
    ) -> DependencyGraph:

        graph = DependencyGraph()

        #
        # Build a map:
        #
        # output_name -> producing tool
        #
        produced_outputs = {}

        for tool in tools:

            for output in tool.produces:

                produced_outputs[output] = tool.name

        #
        # Build dependencies
        #
        for tool in tools:

            graph.dependencies.setdefault(tool.name, set())

            for required_input in tool.requires:

                producer = produced_outputs.get(required_input)

                #
                # Ignore inputs coming from user
                #
                if producer is None:
                    continue

                #
                # Don't depend on yourself
                #
                if producer == tool.name:
                    continue

                graph.add_dependency(
                    tool.name,
                    producer,
                )

        return graph


if __name__ == "__main__":


    builder = DependencyBuilder()

    graph = builder.build(
	list_tool_definitions()
    )

    print(graph)
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

for i, group in enumerate(graph.parallel_execution_groups(), start=1):
    print(f"Stage {i}: {group}")
