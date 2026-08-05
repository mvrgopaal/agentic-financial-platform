"""
Agent responsible for retrieving supporting mortgage knowledge.
"""

from app.capstone_agents.agent_result import (
    AgentError,
    KnowledgeAgentResult,
)
from app.rag.knowledge_retriever import KnowledgeRetriever
from app.rag.vectorstore_validator import (
    VectorStoreValidationError,
)


class KnowledgeAgent:
    """
    Retrieve relevant mortgage guidance.

    This agent does not perform financial calculations and
    does not generate recommendations.
    """

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        default_top_k: int = 5,
    ) -> None:
        if default_top_k <= 0:
            raise ValueError(
                "default_top_k must be greater than zero."
            )

        self._retriever = (
            retriever or KnowledgeRetriever()
        )

        self._default_top_k = default_top_k

    def run(
        self,
        query: str,
        top_k: int | None = None,
    ) -> KnowledgeAgentResult:
        """
        Retrieve mortgage knowledge for one user request.
        """

        normalized_query = query.strip()

        retrieval_count = (
            top_k
            if top_k is not None
            else self._default_top_k
        )

        if not normalized_query:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="EMPTY_KNOWLEDGE_QUERY",
                    message=(
                        "The knowledge query cannot be empty."
                    ),
                    retryable=False,
                ),
            )

        if retrieval_count <= 0:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="INVALID_RETRIEVAL_COUNT",
                    message=(
                        "The retrieval count must be "
                        "greater than zero."
                    ),
                    retryable=False,
                    details={
                        "requested_top_k": retrieval_count,
                    },
                ),
            )

        try:
            knowledge = self._retriever.retrieve(
                query=normalized_query,
                k=retrieval_count,
            )

            item_count = len(
                knowledge.items
            )

            evidence_available = item_count > 0

            if not evidence_available:
                return KnowledgeAgentResult(
                    success=True,
                    knowledge=knowledge,
                    evidence_available=False,
                    requested_item_count=retrieval_count,
                    retrieved_item_count=0,
                    error=AgentError(
                        code="NO_RELEVANT_EVIDENCE",
                        message=(
                            "The retrieval operation completed, "
                            "but no supporting mortgage evidence "
                            "was found."
                        ),
                        retryable=False,
                        details={
                            "query": normalized_query,
                            "requested_top_k": retrieval_count,
                        },
                    ),
                )

            return KnowledgeAgentResult(
                success=True,
                knowledge=knowledge,
                evidence_available=True,
                requested_item_count=retrieval_count,
                retrieved_item_count=item_count,
                error=None,
            )

        except VectorStoreValidationError as exc:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="VECTOR_STORE_NOT_READY",
                    message=str(exc),
                    retryable=False,
                ),
            )

        except ValueError as exc:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="KNOWLEDGE_REQUEST_INVALID",
                    message=str(exc),
                    retryable=False,
                ),
            )

        except RuntimeError as exc:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="KNOWLEDGE_RETRIEVAL_FAILED",
                    message=str(exc),
                    retryable=True,
                ),
            )

        except Exception as exc:
            return KnowledgeAgentResult(
                success=False,
                knowledge=None,
                evidence_available=False,
                requested_item_count=retrieval_count,
                retrieved_item_count=0,
                error=AgentError(
                    code="UNEXPECTED_KNOWLEDGE_AGENT_ERROR",
                    message=(
                        "An unexpected error occurred during "
                        "knowledge retrieval."
                    ),
                    retryable=False,
                    details={
                        "exception_type": type(exc).__name__,
                    },
                ),
            )
