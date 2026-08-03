"""
Run the Agentic Financial Platform capstone evaluation suite.
"""

import json
from pathlib import Path
from statistics import mean
from typing import Any

from app.agents.financial_agent import FinancialAgent
from app.evaluation.evaluation_case import EvaluationCase
from app.evaluation.financial_evaluator import FinancialEvaluator


CASES_PATH = Path(
    "evaluation/cases/mortgage_cases.json"
)

RESULTS_PATH = Path(
    "evaluation/results/evaluation_results.json"
)

REPORT_PATH = Path(
    "evaluation/reports/evaluation_summary.md"
)


def load_cases() -> list[EvaluationCase]:
    with CASES_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_cases: list[dict[str, Any]] = json.load(file)

    return [
        EvaluationCase.from_dict(item)
        for item in raw_cases
    ]


def build_summary(
    results: list,
) -> dict[str, Any]:
    total = len(results)
    passed = sum(result.passed for result in results)

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "pass_rate": (
            passed / total
            if total
            else 0.0
        ),
        "tool_selection_accuracy": mean(
            result.tool_selection_score
            for result in results
        ),
        "calculation_accuracy": mean(
            result.calculation_score
            for result in results
        ),
        "schema_compliance": mean(
            float(result.schema_valid)
            for result in results
        ),
        "trace_coverage": mean(
            float(result.trace_present)
            for result in results
        ),
        "guardrail_compliance": mean(
            float(result.approval_guardrail_passed)
            for result in results
        ),
        "average_latency_ms": mean(
            result.duration_ms
            for result in results
        ),
    }


def write_markdown_report(
    summary: dict[str, Any],
    results: list,
) -> None:
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# Evaluation Summary",
        "",
        "## Aggregate Results",
        "",
        "| Metric | Result |",
        "|---|---:|",
        (
            f"| Total cases | "
            f"{summary['total_cases']} |"
        ),
        (
            f"| Passed cases | "
            f"{summary['passed_cases']} |"
        ),
        (
            f"| Failed cases | "
            f"{summary['failed_cases']} |"
        ),
        (
            f"| Pass rate | "
            f"{summary['pass_rate']:.2%} |"
        ),
        (
            f"| Tool-selection accuracy | "
            f"{summary['tool_selection_accuracy']:.2%} |"
        ),
        (
            f"| Calculation accuracy | "
            f"{summary['calculation_accuracy']:.2%} |"
        ),
        (
            f"| Schema compliance | "
            f"{summary['schema_compliance']:.2%} |"
        ),
        (
            f"| Trace coverage | "
            f"{summary['trace_coverage']:.2%} |"
        ),
        (
            f"| Guardrail compliance | "
            f"{summary['guardrail_compliance']:.2%} |"
        ),
        (
            f"| Average latency | "
            f"{summary['average_latency_ms']:.2f} ms |"
        ),
        "",
        "## Case Results",
        "",
        "| Case | Category | Status | Latency |",
        "|---|---|---|---:|",
    ]

    for result in results:
        status = "PASS" if result.passed else "FAIL"

        lines.append(
            f"| {result.case_id} | "
            f"{result.category} | "
            f"{status} | "
            f"{result.duration_ms:.2f} ms |"
        )

    failed_results = [
        result
        for result in results
        if not result.passed
    ]

    if failed_results:
        lines.extend(
            [
                "",
                "## Failures",
                "",
            ]
        )

        for result in failed_results:
            lines.append(
                f"### {result.case_id}"
            )
            lines.append("")

            for failure in result.failures:
                lines.append(
                    f"- {failure}"
                )

            lines.append("")

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    agent = FinancialAgent()
    evaluator = FinancialEvaluator(agent)
    cases = load_cases()

    results = []

    print("\nCAPSTONE EVALUATION")
    print("=" * 70)

    for case in cases:
        print(
            f"Running {case.case_id}: "
            f"{case.category}"
        )

        result = evaluator.evaluate(case)
        results.append(result)

        status = (
            "PASS"
            if result.passed
            else "FAIL"
        )

        print(
            f"  {status} "
            f"({result.duration_ms:.2f} ms)"
        )

    summary = build_summary(results)

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTS_PATH.write_text(
        json.dumps(
            {
                "summary": summary,
                "results": [
                    result.to_dict()
                    for result in results
                ],
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    write_markdown_report(
        summary=summary,
        results=results,
    )

    print("\nSUMMARY")
    print("-" * 70)

    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    print(
        "\nResults written to "
        f"{RESULTS_PATH}"
    )

    print(
        "Report written to "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()
