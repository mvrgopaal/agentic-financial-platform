"""
Graph-driven execution engine.

Responsibilities:
- Read execution stages from the dependency graph
- Collect each tool's required inputs from the context
- Execute tools through the registry
- Store tool outputs back into the context
- Return structured execution results
"""

from app.agents.dependency_builder import DependencyGraph
from app.execution.execution_context import ExecutionContext
from app.execution.execution_result import ExecutionResult
from app.tools.tool_registry import execute_tool, get_tool


class ExecutionEngine:
    """
    Execute tools in dependency order.
    """

    def execute(
        self,
        graph: DependencyGraph,
        context: ExecutionContext,
    ) -> list[ExecutionResult]:
        """
        Execute every stage in the dependency graph.

        Tools within a stage are independent. For the MVP,
        they are executed sequentially. Parallel execution
        can be added later without changing the graph.
        """

        execution_results: list[ExecutionResult] = []

        stages = graph.parallel_execution_groups()

        for stage_number, stage in enumerate(stages, start=1):
            print(f"\nStage {stage_number}")
            print("-" * 40)

            for tool_name in stage:
                print(f"Executing: {tool_name}")

                tool = get_tool(tool_name)

                parameters = {
                    input_name: context.get(input_name)
                    for input_name in tool.requires
                }

                print(f"Parameters: {parameters}")

                try:
                    registry_result = execute_tool(
                        tool_name=tool.name,
                        parameters=parameters,
                        version=tool.version,
                    )

                    outputs = registry_result["result"]

                    context.update(outputs)

                    execution_results.append(
                        ExecutionResult(
                            tool_name=tool.name,
                            success=True,
                            outputs=outputs,
                            error=None,
                        )
                    )

                    print(f"Outputs: {outputs}")

                except Exception as exc:
                    execution_results.append(
                        ExecutionResult(
                            tool_name=tool.name,
                            success=False,
                            outputs={},
                            error=str(exc),
                        )
                    )

                    print(f"Error: {exc}")

                    # MVP behavior: stop on the first failure.
                    return execution_results

        return execution_results
