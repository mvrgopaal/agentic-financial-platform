from dataclasses import dataclass


@dataclass(slots=True)
class ReasoningResult:
    success: bool
    answer: str
    error: str | None = None
