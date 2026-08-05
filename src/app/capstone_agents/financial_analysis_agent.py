"""
Agent responsible for deterministic financial analysis.
"""

from typing import Any

from app.agents.capability_planner import (
    CapabilityPlanner,
    PlanningRequest,
)
from app.agents.dependency_builder import DependencyBuilder
from app.capstone_agents.agent_result import FinancialAnalysisResult
from app.execution.execution_context import ExecutionContext
from app.execution.execution_engine import ExecutionEngine
from app.tools.tool_registry import get_tool


class FinancialAnalysisAgent:
    """
    Select and execute deterministic financial tools.

    This agent does not retrieve knowledge and does not call an LLM.
    """

    def __init__(
        self,
        planner: CapabilityPlanner | None = None,
        dependency_builder: DependencyBuilder | None = None,
        execution_engine: ExecutionEngine | None = None,
    ) -> None:
        self._planner = planner or CapabilityPlanner()
        self._dependency_builder = (
            dependency_builder or DependencyBuilder()
        )
        self._execution_engine = (
            execution_engine or ExecutionEngine()
        )

    def run(
        self,
        user_goal: str,
        inputs: dict[str, Any],
    ) -> FinancialAnalysisResult:
        """
        Plan and execute the required financial calculations.
        """

        try:
            planning_result = self._planner.plan(
                PlanningRequest(
                    user_goal=user_goal,
                    available_inputs=inputs,
                )
            )
            selected_tools = tuple(
                planning_result.selected_tools
            )

            tool_definitions = [
                get_tool(tool_name)
                for tool_name in selected_tools
            ]

            graph = self._dependency_builder.build(
                tool_definitions
            )

            context = ExecutionContext(
                values=dict(inputs)
            )

            print("DEBUG selected tools:", selected_tools)
            print(
                "DEBUG execution groups:",
                graph.parallel_execution_groups(),
            )
            print("DEBUG initial context:", context.values)
            execution_results = tuple(
                self._execution_engine.execute(
                    graph=graph,
                    context=context,
                )
            )

            failed_results = [
                result
                for result in execution_results
                if not result.success
            ]

            if failed_results:
                failure_summary = "; ".join(
                    (
                        f"{result.tool_name}: "
                        f"{result.error or 'unknown error'}"
                    )
                    for result in failed_results
                )

                return FinancialAnalysisResult(
                    success=False,
                    selected_tools=selected_tools,
                    execution_results=execution_results,
                    verified_facts=dict(context.values),
                    error=failure_summary,
                )

            return FinancialAnalysisResult(
                success=True,
                selected_tools=selected_tools,
                execution_results=execution_results,
                verified_facts=dict(context.values),
            )

        except Exception as exc:
            return FinancialAnalysisResult(
                success=False,
                selected_tools=(),
                execution_results=(),
                verified_facts=dict(inputs),
                error=str(exc),
            )
