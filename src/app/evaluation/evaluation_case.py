"""
Evaluation-case model for mortgage scenarios.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    case_id: str
    category: str
    user_goal: str
    inputs: dict[str, Any]
    expected_tools: tuple[str, ...]
    expected_values: dict[str, float]
    expected_success: bool

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "EvaluationCase":
        return cls(
            case_id=data["case_id"],
            category=data["category"],
            user_goal=data["user_goal"],
            inputs=dict(data["inputs"]),
            expected_tools=tuple(
                data.get("expected_tools", [])
            ),
            expected_values=dict(
                data.get("expected_values", {})
            ),
            expected_success=bool(
                data.get("expected_success", True)
            ),
        )
