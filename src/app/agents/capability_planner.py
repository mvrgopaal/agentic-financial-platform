"""
Capability-based planning for the Financial AI Agent.

This first version maps a user goal to business capabilities,
then discovers matching tools from the registry.

It does not execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.dependency_execution_engine import (
    ExecutionPlan,
    ExecutionStep,
)
from app.tools.tool_definition import ToolDefinition
from app.tools.tool_registry import (
    find_tools_by_capability,
)


@dataclass(frozen=True)
class PlanningRequest:
    """
    Information supplied to the planner.
    """

    user_goal: str
    available_inputs: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class CapabilityRequirement:
    """
    A business capability needed to satisfy the user goal.
    """

    name: str
    reason: str
    required: bool = True


@dataclass(frozen=True)
class PlanningResult:
    """
    Planner output before execution.
    """

    goal: str
    capabilities: tuple[CapabilityRequirement, ...]
    selected_tools: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    execution_plan: ExecutionPlan | None


class CapabilityPlanner:
    """
    Builds execution plans from business capabilities.
    """

    def plan(
        self,
        request: PlanningRequest,
    ) -> PlanningResult:
        capabilities = self._infer_capabilities(
            request.user_goal
        )

        selected_tools = self._select_tools(
            capabilities
        )

        missing_inputs = self._find_missing_inputs(
            tools=selected_tools,
            available_inputs=request.available_inputs,
        )

        execution_plan = None

        if not missing_inputs:
            execution_plan = self._build_execution_plan(
		user_question=request.user_goal,
                tools=selected_tools,
                available_inputs=request.available_inputs,
            )

        return PlanningResult(
            goal=request.user_goal,
            capabilities=tuple(capabilities),
            selected_tools=tuple(
                tool.name
                for tool in selected_tools
            ),
            missing_inputs=tuple(
                sorted(missing_inputs)
            ),
            execution_plan=execution_plan,
        )

    def _infer_capabilities(
        self,
        user_goal: str,
    ) -> list[CapabilityRequirement]:
        """
        Infer business capabilities from the user's goal.

        Version 1 uses simple goal classification.
        A later version can use an LLM with structured output.
        """

        normalized_goal = user_goal.lower()

        requirements: list[
            CapabilityRequirement
        ] = []

        if any(
            phrase in normalized_goal
            for phrase in (
                "qualify",
                "qualification",
                "prequalify",
                "prequalification",
                "can i afford",
            )
        ):
            requirements.extend(
                [
                    CapabilityRequirement(
                        name="loan_amount_calculation",
                        reason=(
                            "Determine the requested "
                            "mortgage balance."
                        ),
                    ),
                    CapabilityRequirement(
                        name="loan_to_value_analysis",
                        reason=(
                            "Measure collateral leverage."
                        ),
                    ),
                    CapabilityRequirement(
                        name="debt_to_income_analysis",
                        reason=(
                            "Measure borrower repayment "
                            "capacity."
                        ),
                    ),
                    CapabilityRequirement(
                        name="mortgage_payment_calculation",
                        reason=(
                            "Estimate monthly principal "
                            "and interest."
                        ),
                    ),
                ]
            )

        elif any(
            phrase in normalized_goal
            for phrase in (
                "monthly payment",
                "mortgage payment",
                "principal and interest",
            )
        ):
            requirements.append(
                CapabilityRequirement(
                    name="mortgage_payment_calculation",
                    reason=(
                        "Estimate monthly principal "
                        "and interest."
                    ),
                )
            )

        elif "dti" in normalized_goal:
            requirements.append(
                CapabilityRequirement(
                    name="debt_to_income_analysis",
                    reason=(
                        "Calculate the borrower's "
                        "debt-to-income ratio."
                    ),
                )
            )

        elif "ltv" in normalized_goal:
            requirements.append(
                CapabilityRequirement(
                    name="loan_to_value_analysis",
                    reason=(
                        "Calculate the property's "
                        "loan-to-value ratio."
                    ),
                )
            )

        else:
            raise ValueError(
                "The planner could not infer a supported "
                "financial capability from the user goal."
            )

        return requirements

    def _select_tools(
        self,
        capabilities: list[CapabilityRequirement],
    ) -> list[ToolDefinition]:
        """
        Select one active tool for each required capability.
        """

        selected: dict[
            tuple[str, str],
            ToolDefinition,
        ] = {}

        for requirement in capabilities:
            matches = find_tools_by_capability(
                requirement.name
            )

            if not matches:
                if requirement.required:
                    raise LookupError(
                        "No active tool supports capability "
                        f"'{requirement.name}'."
                    )

                continue

            chosen_tool = matches[0]

            selected[
                (
                    chosen_tool.name,
                    chosen_tool.version,
                )
            ] = chosen_tool

        return list(selected.values())

    def _find_missing_inputs(
        self,
        tools: list[ToolDefinition],
        available_inputs: dict[str, Any],
    ) -> set[str]:
        """
        Find tool inputs not supplied by the user and not
        produced by another selected tool.
        """

        supplied = set(available_inputs)

        produced = {
            output_name
            for tool in tools
            for output_name in tool.produces
        }

        required = {
            input_name
            for tool in tools
            for input_name in tool.requires
        }

        return required - supplied - produced

    def _build_execution_plan(
        self,
	user_question: str,
        tools: list[ToolDefinition],
        available_inputs: dict[str, Any],
    ) -> ExecutionPlan:
        """
        Build the first metadata-driven execution plan.

        Dependency wiring will be improved in the next step.
        """

        steps: list[ExecutionStep] = []

        for tool in tools:
            parameters = {
                input_name: available_inputs[input_name]
                for input_name in tool.requires
                if input_name in available_inputs
            }

            steps.append(
                ExecutionStep(
                    step_id=tool.name,
                    tool_name=tool.name,
                    parameters=parameters,
                    depends_on=(),
                )
            )

        return ExecutionPlan(
	    user_question=user_question,
            steps=tuple(steps),
        )

if __name__ == "__main__":
    from pprint import pprint

    planner = CapabilityPlanner()

    result = planner.plan(
        PlanningRequest(
            user_goal=(
                "Can this borrower qualify for a "
                "$600,000 property?"
            ),
            available_inputs={
                "property_value": 600000,
                "down_payment": 60000,
                "monthly_income": 15000,
                "monthly_debt": 3200,
                "annual_interest_rate": 6.5,
                "loan_term_years": 30,
            },
        )
    )

    pprint(result)
