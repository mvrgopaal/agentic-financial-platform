"""
Agent responsible for generating a grounded preliminary
mortgage recommendation.
"""

from app.capstone_agents.agent_result import (
    AgentError,
    FinancialAnalysisResult,
    KnowledgeAgentResult,
    RecommendationAgentResult,
)
from app.agents.prompt_builder import PromptBuilder
from app.execution.execution_context import ExecutionContext
from app.reasoning.reasoning_engine import ReasoningEngine


class RecommendationAgent:
    """
    Generate a preliminary mortgage assessment from:

    - verified deterministic financial facts,
    - retrieved mortgage evidence,
    - the original user question.

    This agent does not execute financial tools and does not
    retrieve documents directly.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        reasoning_engine: ReasoningEngine,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._reasoning_engine = reasoning_engine

    def run(
        self,
        user_question: str,
        financial_analysis: FinancialAnalysisResult,
        knowledge_result: KnowledgeAgentResult,
    ) -> RecommendationAgentResult:
        """
        Build a grounded prompt and generate a preliminary
        recommendation.
        """

        normalized_question = user_question.strip()

        if not normalized_question:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="EMPTY_RECOMMENDATION_QUESTION",
                    message=(
                        "The recommendation question cannot "
                        "be empty."
                    ),
                    retryable=False,
                ),
            )

        if not financial_analysis.success:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="FINANCIAL_ANALYSIS_UNAVAILABLE",
                    message=(
                        "A recommendation cannot be generated "
                        "because verified financial analysis "
                        "did not complete successfully."
                    ),
                    retryable=False,
                    details={
                        "analysis_error": (
                            financial_analysis.error.message
                            if financial_analysis.error
                            else None
                        ),
                    },
                ),
            )

        if not knowledge_result.success:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="KNOWLEDGE_RETRIEVAL_UNAVAILABLE",
                    message=(
                        "A grounded recommendation cannot be "
                        "generated because knowledge retrieval "
                        "did not complete successfully."
                    ),
                    retryable=(
                        knowledge_result.error.retryable
                        if knowledge_result.error
                        else False
                    ),
                    details={
                        "knowledge_error_code": (
                            knowledge_result.error.code
                            if knowledge_result.error
                            else None
                        ),
                    },
                ),
            )

        if not knowledge_result.evidence_available:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="SUPPORTING_EVIDENCE_UNAVAILABLE",
                    message=(
                        "Knowledge retrieval completed, but no "
                        "supporting mortgage evidence was found. "
                        "The platform will not generate an "
                        "ungrounded recommendation."
                    ),
                    retryable=False,
                    details={
                        "requested_item_count": (
                            knowledge_result.requested_item_count
                        ),
                        "retrieved_item_count": (
                            knowledge_result.retrieved_item_count
                        ),
                    },
                ),
            )

        if knowledge_result.knowledge is None:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="KNOWLEDGE_RESULT_INCONSISTENT",
                    message=(
                        "Evidence was marked available, but the "
                        "retrieved knowledge object was missing."
                    ),
                    retryable=False,
                ),
            )

        try:
            context = ExecutionContext(
                values=dict(
                    financial_analysis.verified_facts
                )
            )

            prompt = self._prompt_builder.build(
                user_question=normalized_question,
                context=context,
                knowledge=knowledge_result.knowledge,
            )

            reasoning_result = (
                self._reasoning_engine.reason(
                    prompt
                )
            )

            if not reasoning_result.success:
                return RecommendationAgentResult(
                    success=False,
                    answer="",
                    prompt=prompt,
                    error=AgentError(
                        code="REASONING_PROVIDER_FAILED",
                        message=(
                            reasoning_result.error
                            or (
                                "The reasoning provider failed "
                                "without returning an error."
                            )
                        ),
                        retryable=True,
                    ),
                )

            answer = reasoning_result.answer.strip()

            if not answer:
                return RecommendationAgentResult(
                    success=False,
                    answer="",
                    prompt=prompt,
                    error=AgentError(
                        code="EMPTY_REASONING_RESPONSE",
                        message=(
                            "The reasoning provider returned "
                            "an empty recommendation."
                        ),
                        retryable=True,
                    ),
                )

            return RecommendationAgentResult(
                success=True,
                answer=answer,
                prompt=prompt,
                error=None,
            )

        except ValueError as exc:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="RECOMMENDATION_INPUT_INVALID",
                    message=str(exc),
                    retryable=False,
                ),
            )

        except Exception as exc:
            return RecommendationAgentResult(
                success=False,
                answer="",
                error=AgentError(
                    code="UNEXPECTED_RECOMMENDATION_ERROR",
                    message=(
                        "An unexpected error occurred while "
                        "generating the recommendation."
                    ),
                    retryable=False,
                    details={
                        "exception_type": type(exc).__name__,
                    },
                ),
            )
