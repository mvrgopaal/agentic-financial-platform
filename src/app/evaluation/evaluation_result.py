"""
Evaluation result generated for one mortgage scenario.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    case_id: str
    category: str
    passed: bool
    workflow_success: bool

    expected_tools: tuple[str, ...]
    actual_tools: tuple[str, ...]

    tool_selection_score: float
    calculation_score: float

    schema_valid: bool
    trace_present: bool
    disclaimer_present: bool
    approval_guardrail_passed: bool

    duration_ms: float
    failures: tuple[str, ...] = field(
        default_factory=tuple
    )

    actual_values: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
