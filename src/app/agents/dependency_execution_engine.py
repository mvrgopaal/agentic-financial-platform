"""
Dependency-aware execution engine.

Responsibilities:
- Accept an execution graph
- Detect which steps are ready
- Execute independent ready steps concurrently
- Wait for dependencies before starting dependent steps
- Pass outputs from earlier steps into later steps
- Detect invalid or circular dependencies
- Return a structured evidence package
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from app.tools.tool_registry import execute_tool


@dataclass(frozen=True)
class OutputReference:
    """
    References a value produced by an earlier execution step.

    Example:
        OutputReference(
            step_id="loan_amount",
            field_name="loan_amount",
        )
    """

    step_id: str
    field_name: str


@dataclass(frozen=True)
class ExecutionStep:
    """
    Represents one node in the execution graph.
    """

    step_id: str
    tool_name: str
    parameters: dict[str, Any]
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Represents the complete workflow requested by the planner.
    """

    user_question: str
    steps: tuple[ExecutionStep, ...]


@dataclass
class EvidencePackage:
    """
    Contains successful results and execution errors.
    """

    user_question: str
    step_results: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )
    step_errors: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )
    execution_order: list[str] = field(
        default_factory=list
    )


class DependencyExecutionEngine:
    """
    Executes tools according to their dependency relationships.
    """

    def __init__(self, max_workers: int = 4) -> None:
        if max_workers <= 0:
            raise ValueError(
                "max_workers must be greater than zero."
            )

        self.max_workers = max_workers

    def execute(
        self,
        plan: ExecutionPlan,
    ) -> EvidencePackage:
        """
        Execute all steps in dependency order.

        Independent ready steps are executed concurrently.
        """

        self._validate_plan(plan)

        evidence = EvidencePackage(
            user_question=plan.user_question
        )

        pending_steps = {
            step.step_id: step
            for step in plan.steps
        }

        completed_steps: set[str] = set()
        failed_steps: set[str] = set()

        while pending_steps:
            ready_steps = self._find_ready_steps(
                pending_steps=pending_steps,
                completed_steps=completed_steps,
                failed_steps=failed_steps,
            )

            if not ready_steps:
                self._record_blocked_steps(
                    pending_steps=pending_steps,
                    failed_steps=failed_steps,
                    evidence=evidence,
                )
                break

            wave_results, wave_errors = (
                self._execute_ready_steps(
                    ready_steps=ready_steps,
                    previous_results=evidence.step_results,
                )
            )

            for step_id, result in wave_results.items():
                evidence.step_results[step_id] = result
                evidence.execution_order.append(step_id)
                completed_steps.add(step_id)
                pending_steps.pop(step_id, None)

            for step_id, error in wave_errors.items():
                evidence.step_errors[step_id] = error
                evidence.execution_order.append(step_id)
                failed_steps.add(step_id)
                pending_steps.pop(step_id, None)

        return evidence

    def _find_ready_steps(
        self,
        pending_steps: dict[str, ExecutionStep],
        completed_steps: set[str],
        failed_steps: set[str],
    ) -> list[ExecutionStep]:
        """
        Return steps whose dependencies have completed successfully.
        """

        ready_steps: list[ExecutionStep] = []

        for step in pending_steps.values():
            dependency_set = set(step.depends_on)

            has_failed_dependency = bool(
                dependency_set & failed_steps
            )

            dependencies_completed = (
                dependency_set <= completed_steps
            )

            if (
                dependencies_completed
                and not has_failed_dependency
            ):
                ready_steps.append(step)

        return ready_steps

    def _execute_ready_steps(
        self,
        ready_steps: list[ExecutionStep],
        previous_results: dict[str, dict[str, Any]],
    ) -> tuple[
        dict[str, dict[str, Any]],
        dict[str, dict[str, Any]],
    ]:
        """
        Execute one wave of independent ready steps concurrently.
        """

        results: dict[str, dict[str, Any]] = {}
        errors: dict[str, dict[str, Any]] = {}

        worker_count = min(
            self.max_workers,
            len(ready_steps),
        )

        with ThreadPoolExecutor(
            max_workers=worker_count
        ) as executor:

            future_to_step = {}

            for step in ready_steps:
                try:
                    resolved_parameters = (
                        self._resolve_parameters(
                            parameters=step.parameters,
                            previous_results=previous_results,
                        )
                    )
                except Exception as exc:
                    errors[step.step_id] = {
                        "tool": step.tool_name,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                    continue

                future = executor.submit(
                    execute_tool,
                    step.tool_name,
                    resolved_parameters,
                )

                future_to_step[future] = step

            for future in as_completed(future_to_step):
                step = future_to_step[future]

                try:
                    result = future.result()
                    results[step.step_id] = result

                except Exception as exc:
                    errors[step.step_id] = {
                        "tool": step.tool_name,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }

        return results, errors

    def _resolve_parameters(
        self,
        parameters: dict[str, Any],
        previous_results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Replace OutputReference objects with actual values
        produced by earlier steps.
        """

        resolved: dict[str, Any] = {}

        for parameter_name, parameter_value in parameters.items():

            if isinstance(
                parameter_value,
                OutputReference,
            ):
                resolved[parameter_name] = (
                    self._resolve_output_reference(
                        reference=parameter_value,
                        previous_results=previous_results,
                    )
                )
            else:
                resolved[parameter_name] = parameter_value

        return resolved

    def _resolve_output_reference(
        self,
        reference: OutputReference,
        previous_results: dict[str, dict[str, Any]],
    ) -> Any:
        """
        Retrieve one field from an earlier tool result.
        """

        source_result = previous_results.get(
            reference.step_id
        )

        if source_result is None:
            raise ValueError(
                f"No result exists for step "
                f"'{reference.step_id}'."
            )

        tool_result = source_result.get("result")

        if not isinstance(tool_result, dict):
            raise ValueError(
                f"Step '{reference.step_id}' did not "
                "produce a dictionary result."
            )

        if reference.field_name not in tool_result:
            raise ValueError(
                f"Field '{reference.field_name}' was not "
                f"found in step '{reference.step_id}'."
            )

        return tool_result[reference.field_name]

    def _record_blocked_steps(
        self,
        pending_steps: dict[str, ExecutionStep],
        failed_steps: set[str],
        evidence: EvidencePackage,
    ) -> None:
        """
        Record steps that cannot run because dependencies failed
        or because the graph cannot make further progress.
        """

        for step_id, step in pending_steps.items():
            failed_dependencies = [
                dependency
                for dependency in step.depends_on
                if dependency in failed_steps
            ]

            if failed_dependencies:
                message = (
                    "Step was blocked because these "
                    f"dependencies failed: "
                    f"{failed_dependencies}"
                )
            else:
                message = (
                    "Step could not be scheduled. "
                    "The plan may contain a circular dependency."
                )

            evidence.step_errors[step_id] = {
                "tool": step.tool_name,
                "error_type": "BlockedStepError",
                "message": message,
            }

    def _validate_plan(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Validate step IDs and dependency references.
        """

        step_ids = [
            step.step_id
            for step in plan.steps
        ]

        if len(step_ids) != len(set(step_ids)):
            raise ValueError(
                "Every execution step must have a unique step_id."
            )

        known_step_ids = set(step_ids)

        for step in plan.steps:
            for dependency in step.depends_on:
                if dependency not in known_step_ids:
                    raise ValueError(
                        f"Step '{step.step_id}' depends on "
                        f"unknown step '{dependency}'."
                    )

                if dependency == step.step_id:
                    raise ValueError(
                        f"Step '{step.step_id}' cannot depend "
                        "on itself."
                    )


if __name__ == "__main__":
    from pprint import pprint

    plan = ExecutionPlan(
        user_question=(
            "I am buying a $600,000 home with 10% down. "
            "My gross monthly income is $12,000 and my "
            "monthly debt is $2,500. Can I qualify?"
        ),
        steps=(
            ExecutionStep(
                step_id="loan_amount",
                tool_name="calculate_loan_amount",
                parameters={
                    "property_value": 600000,
                    "down_payment": 60000,
                },
            ),
            ExecutionStep(
                step_id="dti",
                tool_name="calculate_dti",
                parameters={
                    "monthly_income": 12000,
                    "monthly_debt": 2500,
                },
            ),
            ExecutionStep(
                step_id="ltv",
                tool_name="calculate_ltv",
                parameters={
                    "property_value": 600000,
                    "loan_amount": OutputReference(
                        step_id="loan_amount",
                        field_name="loan_amount",
                    ),
                },
                depends_on=("loan_amount",),
            ),
        ),
    )

    engine = DependencyExecutionEngine(
        max_workers=4
    )

    evidence = engine.execute(plan)

    print("\nDependency-aware execution evidence:")
    pprint(evidence)
