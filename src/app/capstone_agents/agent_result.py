"""
Structured contracts exchanged between capstone agents.
"""

from dataclasses import dataclass, field
from typing import Any

from app.agents.prompt_definition import PromptDefinition
from app.execution.execution_result import ExecutionResult
from app.rag.retrieved_knowledge import RetrievedKnowledge


@dataclass(frozen=True, slots=True)
class AgentError:
    """
    Structured error returned by an agent.

    code:
        Stable machine-readable identifier.

    message:
        Human-readable explanation.

    retryable:
        Indicates whether retrying may reasonably succeed.

    details:
        Optional diagnostic context that does not expose secrets.
    """

    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class FinancialAnalysisResult:
    """
    Verified deterministic results produced by the
    Financial Analysis Agent.
    """

    success: bool
    selected_tools: tuple[str, ...]
    execution_results: tuple[ExecutionResult, ...]
    verified_facts: dict[str, Any]
    error: AgentError | None = None


@dataclass(frozen=True, slots=True)
class KnowledgeAgentResult:
    """
    Supporting mortgage knowledge produced by the Knowledge Agent.
    """

    success: bool

    knowledge: RetrievedKnowledge | None

    evidence_available: bool

    requested_item_count: int

    retrieved_item_count: int

    error: AgentError | None = None


@dataclass(frozen=True, slots=True)
class RecommendationAgentResult:
    """
    Preliminary recommendation produced by the
    Recommendation Agent.
    """

    success: bool
    answer: str
    prompt: PromptDefinition | None = None
    error: AgentError | None = None


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """
    One validation or guardrail issue.
    """

    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class ValidationAgentResult:
    """
    Final validation status for a recommendation.
    """

    valid: bool
    issues: tuple[ValidationIssue, ...] = field(
        default_factory=tuple
    )

    @property
    def error_count(self) -> int:
        return sum(
            1
            for issue in self.issues
            if issue.severity == "error"
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1
            for issue in self.issues
            if issue.severity == "warning"
        )
@dataclass(frozen=True, slots=True)
class FinancialCoordinatorResult:
    """
    Complete result returned by the Financial Coordinator Agent.
    """

    success: bool

    financial_analysis: FinancialAnalysisResult

    knowledge_result: KnowledgeAgentResult | None

    recommendation_result: RecommendationAgentResult | None

    validation_result: ValidationAgentResult | None

    trace_id: str

    trace_spans: tuple

    error: AgentError | None = None
@dataclass(frozen=True, slots=True)
class FinancialCoordinatorResult:
    """
    Complete result returned by the Financial Coordinator Agent.
    """

    success: bool
    financial_analysis: FinancialAnalysisResult
    knowledge_result: KnowledgeAgentResult | None
    recommendation_result: RecommendationAgentResult | None
    validation_result: ValidationAgentResult | None
    trace_id: str
    trace_spans: tuple
    error: AgentError | None = None
