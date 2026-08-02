"""
Execution engine for the Financial AI Agent.

Responsibilities:
- Accept an execution plan
- Execute independent financial tools in parallel
- Collect structured results
- Return an evidence package

The engine coordinates tools but does not perform
financial calculations itself.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from app.tools.tool_registry import execute_tool


@dataclass(frozen=True)
class ToolCall:
    """
    Represents one tool invocation requested by the planner.
    """

    tool_name: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Represents the work required to answer a user request.
    """

    user_question: str
    tool_calls: list[ToolCall]
    requires_rag: bool = False
    rag_query: str | None = None


@dataclass
class EvidencePackage:
    """
    Contains all evidence collected during execution.

    The final LLM will later use this package to produce
    a grounded natural-language response.
    """

    user_question: str
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    tool_errors: list[dict[str, Any]] = field(default_factory=list)
    retrieved_documents: list[Any] = field(default_factory=list)


class ExecutionEngine:
    """
    Coordinates execution of a financial-agent plan.
    """

    def __init__(self, max_workers: int = 4) -> None:
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than zero.")

        self.max_workers = max_workers

    def execute(self, plan: ExecutionPlan) -> EvidencePackage:
        """
        Execute the supplied plan and return collected evidence.
        """

        evidence = EvidencePackage(
            user_question=plan.user_question,
        )

        if plan.tool_calls:
            tool_results, tool_errors = self._execute_tools_parallel(
                plan.tool_calls
            )

            evidence.tool_results.extend(tool_results)
            evidence.tool_errors.extend(tool_errors)

        # RAG execution will be connected in the next iteration.
        if plan.requires_rag:
            print(
                "RAG requested but not yet connected. "
                f"Query: {plan.rag_query}"
            )

        return evidence

    def _execute_tools_parallel(
        self,
        tool_calls: list[ToolCall],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Execute independent tool calls concurrently.

        A failure in one tool does not prevent other tools
        from completing.
        """

        results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        worker_count = min(
            self.max_workers,
            len(tool_calls),
        )

        with ThreadPoolExecutor(
            max_workers=worker_count
        ) as executor:

            future_to_call = {
                executor.submit(
                    execute_tool,
                    tool_call.tool_name,
                    tool_call.parameters,
                ): tool_call
                for tool_call in tool_calls
            }

            for future in as_completed(future_to_call):
                tool_call = future_to_call[future]

                try:
                    result = future.result()
                    results.append(result)

                except Exception as exc:
                    errors.append(
                        {
                            "tool": tool_call.tool_name,
                            "parameters": tool_call.parameters,
                            "error_type": type(exc).__name__,
                            "message": str(exc),
                        }
                    )

        return results, errors


if __name__ == "__main__":
    from pprint import pprint

    plan = ExecutionPlan(
        user_question=(
            "I am buying a $600,000 home with 10% down. "
            "My gross monthly income is $12,000 and my "
            "monthly debt is $2,500. Can I qualify?"
        ),
        tool_calls=[
            ToolCall(
                tool_name="calculate_ltv",
                parameters={
                    "property_value": 600000,
                    "loan_amount": 540000,
                },
            ),
            ToolCall(
                tool_name="calculate_dti",
                parameters={
                    "monthly_income": 12000,
                    "monthly_debt": 2500,
                },
            ),
        ],
        requires_rag=True,
        rag_query=(
            "Mortgage qualification requirements for a borrower "
            "with 90 percent LTV and approximately 20.83 percent DTI"
        ),
    )

    engine = ExecutionEngine()

    evidence = engine.execute(plan)

    print("\nExecution evidence:")
    pprint(evidence)
