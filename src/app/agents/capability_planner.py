"""
Capability-based planning for the Financial AI Agent.

This planner maps a user goal to business capabilities,
discovers matching tools from the registry, expands required
producer capabilities, validates missing inputs, and builds
an execution plan.

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
from app.tools.tool_registry import find_tools_by_capability


@dataclass(frozen=True)
class PlanningRequest:
    """Information supplied to the planner."""

    user_goal: str
    available_inputs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityRequirement:
    """A business capability needed to satisfy the user goal."""

    name: str
    reason: str
    required: bool = True


@dataclass(frozen=True)
class PlanningResult:
    """Planner output before execution."""

    goal: str
    capabilities: tuple[CapabilityRequirement, ...]
    selected_tools: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    execution_plan: ExecutionPlan | None


class CapabilityPlanner:
    """Build execution plans from business capabilities."""

    def plan(self, request: PlanningRequest) -> PlanningResult:
        capabilities = self._infer_capabilities(request.user_goal)

        capabilities = self._expand_dependencies(
            capabilities=capabilities,
            available_inputs=request.available_inputs,
        )

        selected_tools = self._select_tools(capabilities)

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
            selected_tools=tuple(tool.name for tool in selected_tools),
            missing_inputs=tuple(sorted(missing_inputs)),
            execution_plan=execution_plan,
        )

    def _infer_capabilities(
        self,
        user_goal: str,
    ) -> list[CapabilityRequirement]:
        """
        Infer all supported business capabilities from the user goal.

        Version 1 uses deterministic phrase matching.
        A later version may use an LLM with structured output.
        """

        normalized_goal = user_goal.strip().lower()

        if not normalized_goal:
            raise ValueError("The user goal cannot be empty.")

        requirements: list[CapabilityRequirement] = []

        qualification_phrases = (
            "qualify",
            "qualification",
            "prequalify",
            "prequalification",
            "can i afford",
        )

        if any(
            phrase in normalized_goal
            for phrase in qualification_phrases
        ):
            requirements.extend(
                [
                    CapabilityRequirement(
                        name="loan_amount_calculation",
                        reason="Determine the requested mortgage balance.",
                    ),
                    CapabilityRequirement(
                        name="loan_to_value_analysis",
                        reason="Measure collateral leverage.",
                    ),
                    CapabilityRequirement(
                        name="debt_to_income_analysis",
                        reason="Measure borrower repayment capacity.",
                    ),
                    CapabilityRequirement(
                        name="mortgage_payment_calculation",
                        reason="Estimate monthly principal and interest.",
                    ),
                ]
            )
        else:
            if any(
                phrase in normalized_goal
                for phrase in (
                    "dti",
                    "debt-to-income",
                    "debt to income",
                )
            ):
                requirements.append(
                    CapabilityRequirement(
                        name="debt_to_income_analysis",
                        reason=(
                            "Calculate the borrower's debt-to-income ratio."
                        ),
                    )
                )

            if any(
                phrase in normalized_goal
                for phrase in (
                    "loan amount",
                    "mortgage amount",
                    "borrow amount",
                )
            ):
                requirements.append(
                    CapabilityRequirement(
                        name="loan_amount_calculation",
                        reason="Calculate the mortgage balance.",
                    )
                )

            if any(
                phrase in normalized_goal
                for phrase in (
                    "ltv",
                    "loan-to-value",
                    "loan to value",
                )
            ):
                requirements.append(
                    CapabilityRequirement(
                        name="loan_to_value_analysis",
                        reason=(
                            "Calculate the property's loan-to-value ratio."
                        ),
                    )
                )

            if any(
                phrase in normalized_goal
                for phrase in (
                    "monthly payment",
                    "mortgage payment",
                    "principal and interest",
                    "payment",
                )
            ):
                requirements.append(
                    CapabilityRequirement(
                        name="mortgage_payment_calculation",
                        reason="Estimate monthly principal and interest.",
                    )
                )

        if not requirements:
            raise ValueError(
                "The planner could not infer a supported "
                "financial capability from the user goal."
            )

        return self._deduplicate_capabilities(requirements)

    def _expand_dependencies(
        self,
        capabilities: list[CapabilityRequirement],
        available_inputs: dict[str, Any],
    ) -> list[CapabilityRequirement]:
        """
        Add producer capabilities when selected capabilities
        require data that the user did not supply directly.
        """

        expanded = list(capabilities)

        capability_names = {
            capability.name
            for capability in expanded
        }

        requires_loan_amount = any(
            capability_name in capability_names
            for capability_name in (
                "loan_to_value_analysis",
                "mortgage_payment_calculation",
            )
        )

        if (
            requires_loan_amount
            and "loan_amount" not in available_inputs
            and "loan_amount_calculation" not in capability_names
        ):
            expanded.append(
                CapabilityRequirement(
                    name="loan_amount_calculation",
                    reason=(
                        "Produce the loan amount required by "
                        "a dependent financial calculation."
                    ),
                )
            )

        return self._deduplicate_capabilities(expanded)

    def _deduplicate_capabilities(
        self,
        capabilities: list[CapabilityRequirement],
    ) -> list[CapabilityRequirement]:
        """Remove duplicates while preserving order."""

        unique: dict[str, CapabilityRequirement] = {}

        for capability in capabilities:
            unique.setdefault(capability.name, capability)

        return list(unique.values())

    def _select_tools(
        self,
        capabilities: list[CapabilityRequirement],
    ) -> list[ToolDefinition]:
        """Select one active tool for each required capability."""

        selected: dict[tuple[str, str], ToolDefinition] = {}

        for requirement in capabilities:
            matches = find_tools_by_capability(requirement.name)

            if not matches:
                if requirement.required:
                    raise LookupError(
                        "No active tool supports capability "
                        f"'{requirement.name}'."
                    )
                continue

            chosen_tool = matches[0]
            selected[(chosen_tool.name, chosen_tool.version)] = chosen_tool

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
        Build the metadata-driven execution plan.

        Dependency execution is handled by the dependency graph
        during runtime. This object preserves the selected steps.
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
                "Calculate DTI, loan amount, LTV, "
                "and monthly payment."
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
