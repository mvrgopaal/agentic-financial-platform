"""
Coordinator for the capstone multi-agent mortgage workflow.
"""

from typing import Any

from app.capstone_agents.agent_result import (
    AgentError,
    FinancialAnalysisResult,
    FinancialCoordinatorResult,
)
from app.capstone_agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
)
from app.capstone_agents.knowledge_agent import KnowledgeAgent
from app.capstone_agents.recommendation_agent import (
    RecommendationAgent,
)
from app.capstone_agents.validation_agent import ValidationAgent
from app.tracing.tracer import Tracer


class FinancialCoordinatorAgent:
    """
    Coordinate the complete mortgage decision-support workflow.

    This agent delegates work to specialized agents.
    It does not perform calculations, retrieval, reasoning,
    or validation itself.
    """

    def __init__(
        self,
        financial_analysis_agent: FinancialAnalysisAgent,
        knowledge_agent: KnowledgeAgent,
        recommendation_agent: RecommendationAgent,
        validation_agent: ValidationAgent,
    ) -> None:
        self._financial_analysis_agent = financial_analysis_agent
        self._knowledge_agent = knowledge_agent
        self._recommendation_agent = recommendation_agent
        self._validation_agent = validation_agent

    def run(
        self,
        user_question: str,
        inputs: dict[str, Any],
        retrieval_count: int | None = None,
    ) -> FinancialCoordinatorResult:
        """
        Execute the end-to-end multi-agent workflow.
        """

        tracer = Tracer()

        request_error = self._validate_request(
            user_question=user_question,
            inputs=inputs,
            retrieval_count=retrieval_count,
        )

        if request_error is not None:
            return FinancialCoordinatorResult(
                success=False,
                financial_analysis=self._not_started_result(
                    inputs=inputs if isinstance(inputs, dict) else {},
                ),
                knowledge_result=None,
                recommendation_result=None,
                validation_result=None,
                trace_id=tracer.trace_id,
                trace_spans=tracer.spans,
                error=request_error,
            )

        normalized_question = user_question.strip()

        with tracer.span(
            "financial_analysis_agent",
        ):
            financial_result = (
                self._financial_analysis_agent.run(
                    user_goal=normalized_question,
                    inputs=inputs,
                )
            )

        if not financial_result.success:
            return FinancialCoordinatorResult(
                success=False,
                financial_analysis=financial_result,
                knowledge_result=None,
                recommendation_result=None,
                validation_result=None,
                trace_id=tracer.trace_id,
                trace_spans=tracer.spans,
                error=AgentError(
                    code="FINANCIAL_ANALYSIS_FAILED",
                    message=(
                        "The workflow stopped because the "
                        "Financial Analysis Agent failed."
                    ),
                    retryable=False,
                    details={
                        "agent_error": (
                            financial_result.error.message
                            if financial_result.error
                            else None
                        ),
                    },
                ),
            )

        with tracer.span(
            "knowledge_agent",
            requested_top_k=retrieval_count,
        ):
            knowledge_result = self._knowledge_agent.run(
                query=normalized_question,
                top_k=retrieval_count,
            )

        if not knowledge_result.success:
            return FinancialCoordinatorResult(
                success=False,
                financial_analysis=financial_result,
                knowledge_result=knowledge_result,
                recommendation_result=None,
                validation_result=None,
                trace_id=tracer.trace_id,
                trace_spans=tracer.spans,
                error=AgentError(
                    code="KNOWLEDGE_AGENT_FAILED",
                    message=(
                        "The workflow stopped because the "
                        "Knowledge Agent failed."
                    ),
                    retryable=(
                        knowledge_result.error.retryable
                        if knowledge_result.error
                        else False
                    ),
                    details={
                        "agent_error_code": (
                            knowledge_result.error.code
                            if knowledge_result.error
                            else None
                        ),
                    },
                ),
            )

        with tracer.span(
            "recommendation_agent",
            evidence_available=(
                knowledge_result.evidence_available
            ),
        ):
            recommendation_result = (
                self._recommendation_agent.run(
                    user_question=normalized_question,
                    financial_analysis=financial_result,
                    knowledge_result=knowledge_result,
                )
            )

        if not recommendation_result.success:
            return FinancialCoordinatorResult(
                success=False,
                financial_analysis=financial_result,
                knowledge_result=knowledge_result,
                recommendation_result=recommendation_result,
                validation_result=None,
                trace_id=tracer.trace_id,
                trace_spans=tracer.spans,
                error=AgentError(
                    code="RECOMMENDATION_AGENT_FAILED",
                    message=(
                        "The workflow could not produce a "
                        "grounded preliminary recommendation."
                    ),
                    retryable=(
                        recommendation_result.error.retryable
                        if recommendation_result.error
                        else False
                    ),
                    details={
                        "agent_error_code": (
                            recommendation_result.error.code
                            if recommendation_result.error
                            else None
                        ),
                    },
                ),
            )

        with tracer.span(
            "validation_agent",
        ):
            validation_result = self._validation_agent.validate(
                financial_analysis=financial_result,
                knowledge_result=knowledge_result,
                recommendation_result=recommendation_result,
            )

        if not validation_result.valid:
            return FinancialCoordinatorResult(
                success=False,
                financial_analysis=financial_result,
                knowledge_result=knowledge_result,
                recommendation_result=recommendation_result,
                validation_result=validation_result,
                trace_id=tracer.trace_id,
                trace_spans=tracer.spans,
                error=AgentError(
                    code="VALIDATION_FAILED",
                    message=(
                        "The recommendation was generated but "
                        "did not pass validation."
                    ),
                    retryable=False,
                    details={
                        "error_count": validation_result.error_count,
                        "warning_count": validation_result.warning_count,
                        "issue_codes": [
                            issue.code
                            for issue in validation_result.issues
                        ],
                    },
                ),
            )

        return FinancialCoordinatorResult(
            success=True,
            financial_analysis=financial_result,
            knowledge_result=knowledge_result,
            recommendation_result=recommendation_result,
            validation_result=validation_result,
            trace_id=tracer.trace_id,
            trace_spans=tracer.spans,
            error=None,
        )

    def _validate_request(
        self,
        user_question: str,
        inputs: dict[str, Any],
        retrieval_count: int | None,
    ) -> AgentError | None:
        """
        Validate the coordinator request before starting agents.
        """

        if not isinstance(user_question, str):
            return AgentError(
                code="INVALID_USER_QUESTION_TYPE",
                message="The user question must be a string.",
                retryable=False,
            )

        if not user_question.strip():
            return AgentError(
                code="EMPTY_USER_QUESTION",
                message="The user question cannot be empty.",
                retryable=False,
            )

        if not isinstance(inputs, dict):
            return AgentError(
                code="INVALID_FINANCIAL_INPUTS",
                message=(
                    "Financial inputs must be supplied "
                    "as a dictionary."
                ),
                retryable=False,
            )

        if (
            retrieval_count is not None
            and retrieval_count <= 0
        ):
            return AgentError(
                code="INVALID_RETRIEVAL_COUNT",
                message=(
                    "The retrieval count must be "
                    "greater than zero."
                ),
                retryable=False,
                details={
                    "retrieval_count": retrieval_count,
                },
            )

        return None

    def _not_started_result(
        self,
        inputs: dict[str, Any],
    ) -> FinancialAnalysisResult:
        """
        Return a placeholder when analysis never started.
        """

        return FinancialAnalysisResult(
            success=False,
            selected_tools=(),
            execution_results=(),
            verified_facts=dict(inputs),
            error=AgentError(
                code="FINANCIAL_ANALYSIS_NOT_STARTED",
                message=(
                    "Financial analysis was not started "
                    "because request validation failed."
                ),
                retryable=False,
            ),
        )
