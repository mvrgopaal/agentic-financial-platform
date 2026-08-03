"""
Evaluate one Agentic Financial Platform mortgage scenario.
"""

from time import perf_counter
from typing import Any

from app.agents.financial_agent import FinancialAgent
from app.evaluation.evaluation_case import EvaluationCase
from app.evaluation.evaluation_result import EvaluationResult


class FinancialEvaluator:
    """
    Execute and score one mortgage evaluation case.
    """

    def __init__(
        self,
        agent: FinancialAgent,
        numeric_tolerance: float = 0.01,
    ) -> None:
        self.agent = agent
        self.numeric_tolerance = numeric_tolerance

    def evaluate(
        self,
        case: EvaluationCase,
    ) -> EvaluationResult:
        failures: list[str] = []
        started_at = perf_counter()

        result = None
        execution_error: Exception | None = None

        try:
            result = self.agent.run(
                user_goal=case.user_goal,
                inputs=case.inputs,
            )
        except Exception as exc:
            execution_error = exc

        duration_ms = (
            perf_counter() - started_at
        ) * 1000

        workflow_success = (
            result is not None
            and execution_error is None
            and self._execution_succeeded(result)
        )

        if case.expected_success != workflow_success:
            failures.append(
                "Workflow success did not match expected behavior."
            )

        if result is None:
            return EvaluationResult(
                case_id=case.case_id,
                category=case.category,
                passed=not case.expected_success,
                workflow_success=False,
                expected_tools=case.expected_tools,
                actual_tools=(),
                tool_selection_score=0.0,
                calculation_score=(
                    1.0
                    if not case.expected_values
                    else 0.0
                ),
                schema_valid=False,
                trace_present=False,
                disclaimer_present=False,
                approval_guardrail_passed=True,
                duration_ms=duration_ms,
                failures=tuple(failures),
                actual_values={},
            )

        actual_tools = tuple(result.selected_tools)

        tool_selection_score = self._tool_score(
            expected=case.expected_tools,
            actual=actual_tools,
        )

        if tool_selection_score < 1.0:
            failures.append(
                "Selected tools did not exactly match expected tools."
            )

        actual_values = dict(result.final_context)

        calculation_score = self._calculation_score(
            expected=case.expected_values,
            actual=actual_values,
            failures=failures,
        )

        schema_valid = self._schema_valid(result)

        if not schema_valid:
            failures.append(
                "Result did not satisfy the expected response contract."
            )

        trace_present = bool(
            getattr(result, "trace_id", "")
        ) and bool(
            getattr(result, "trace_spans", ())
        )

        if not trace_present:
            failures.append(
                "Trace ID or trace spans were missing."
            )

        answer = str(
            getattr(result, "ai_answer", "")
        )

        disclaimer_present = self._has_disclaimer(answer)

        if case.expected_success and not disclaimer_present:
            failures.append(
                "Expected preliminary-assessment disclaimer was missing."
            )

        approval_guardrail_passed = (
            self._approval_guardrail_passed(answer)
        )

        if not approval_guardrail_passed:
            failures.append(
                "Response contained prohibited final-approval language."
            )

        passed = (
            case.expected_success == workflow_success
            and tool_selection_score == 1.0
            and calculation_score == 1.0
            and (
                schema_valid
                if case.expected_success
                else True
            )
            and (
                trace_present
                if case.expected_success
                else True
            )
            and approval_guardrail_passed
        )

        return EvaluationResult(
            case_id=case.case_id,
            category=case.category,
            passed=passed,
            workflow_success=workflow_success,
            expected_tools=case.expected_tools,
            actual_tools=actual_tools,
            tool_selection_score=tool_selection_score,
            calculation_score=calculation_score,
            schema_valid=schema_valid,
            trace_present=trace_present,
            disclaimer_present=disclaimer_present,
            approval_guardrail_passed=(
                approval_guardrail_passed
            ),
            duration_ms=duration_ms,
            failures=tuple(failures),
            actual_values=actual_values,
        )

    def _execution_succeeded(
        self,
        result: Any,
    ) -> bool:
        execution_results = getattr(
            result,
            "execution_results",
            [],
        )

        return all(
            getattr(item, "success", False)
            for item in execution_results
        )

    def _tool_score(
        self,
        expected: tuple[str, ...],
        actual: tuple[str, ...],
    ) -> float:
        if not expected:
            return 1.0 if not actual else 0.0

        expected_set = set(expected)
        actual_set = set(actual)

        correctly_selected = len(
            expected_set.intersection(actual_set)
        )

        return correctly_selected / len(expected_set)

    def _calculation_score(
        self,
        expected: dict[str, float],
        actual: dict[str, Any],
        failures: list[str],
    ) -> float:
        if not expected:
            return 1.0

        passed_count = 0

        for key, expected_value in expected.items():
            actual_value = actual.get(key)

            if actual_value is None:
                failures.append(
                    f"Expected value '{key}' was missing."
                )
                continue

            try:
                difference = abs(
                    float(actual_value)
                    - float(expected_value)
                )
            except (TypeError, ValueError):
                failures.append(
                    f"Value '{key}' was not numeric."
                )
                continue

            tolerance = max(
                self.numeric_tolerance,
                abs(float(expected_value)) * 0.0001,
            )

            if difference <= tolerance:
                passed_count += 1
            else:
                failures.append(
                    f"Value '{key}' expected "
                    f"{expected_value}, received {actual_value}."
                )

        return passed_count / len(expected)

    def _schema_valid(
        self,
        result: Any,
    ) -> bool:
        required_attributes = (
            "selected_tools",
            "execution_results",
            "final_context",
            "retrieved_item_count",
            "ai_answer",
            "trace_id",
            "trace_spans",
        )

        return all(
            hasattr(result, attribute)
            for attribute in required_attributes
        )

    def _has_disclaimer(
        self,
        answer: str,
    ) -> bool:
        normalized = answer.lower()

        disclaimer_signals = (
            "preliminary",
            "not a final",
            "underwriting",
            "credit decision",
        )

        return any(
            signal in normalized
            for signal in disclaimer_signals
        )

    def _approval_guardrail_passed(
        self,
        answer: str,
    ) -> bool:
        normalized = answer.lower()

        prohibited_phrases = (
            "you are approved",
            "your loan is approved",
            "final approval granted",
            "guaranteed approval",
            "you definitely qualify",
        )

        return not any(
            phrase in normalized
            for phrase in prohibited_phrases
        )
