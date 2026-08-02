"""
Application-facing mortgage knowledge retriever.

This module adapts LangChain Document objects returned by the
existing FAISS retriever into RetrievedKnowledge domain objects.
"""

from app.rag.retrieved_knowledge import (
    KnowledgeItem,
    RetrievedKnowledge,
)
from app.rag.retriever import search_documents
from app.rag.vectorstore_validator import VectorStoreValidator


class KnowledgeRetriever:
    """
    Retrieve mortgage guideline excerpts and convert them into
    application-level knowledge objects.
    """
    def __init__(
          self,
          validator: VectorStoreValidator | None = None,
      ) -> None:
          self.validator = validator or VectorStoreValidator()

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> RetrievedKnowledge:
        """
        Retrieve the most relevant mortgage guideline excerpts.
        """

        if not query.strip():
            raise ValueError(
                "Retrieval query cannot be empty."
            )

        if k <= 0:
            raise ValueError(
                "k must be greater than zero."
            )

        self.validator.validate()

        documents = search_documents(
            question=query.strip(),
            k=k,
        )

        items = [
            self._convert_document(document)
            for document in documents
        ]

        return RetrievedKnowledge(
            items=items
        )

    def _convert_document(
        self,
        document,
    ) -> KnowledgeItem:
        """
        Convert one LangChain Document into a KnowledgeItem.
        """

        metadata = document.metadata or {}

        source = (
            metadata.get("title")
            or metadata.get("source")
            or "Unknown source"
        )

        page = self._extract_page(metadata)

        return KnowledgeItem(
            source=str(source),
            page=page,
            content=document.page_content.strip(),
            relevance_score=None,
        )

    def _extract_page(
        self,
        metadata: dict,
    ) -> int | None:
        """
        Return a human-readable page number when available.
        """

        page_label = metadata.get("page_label")

        if page_label is not None:
            try:
                return int(page_label)
            except (TypeError, ValueError):
                pass

        zero_based_page = metadata.get("page")

        if zero_based_page is not None:
            try:
                return int(zero_based_page) + 1
            except (TypeError, ValueError):
                pass

        return None
