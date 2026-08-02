"""
Knowledge retrieved from the vector store.

This isolates the rest of the application
from LangChain-specific document objects.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class KnowledgeItem:
    """
    One retrieved knowledge snippet.
    """

    source: str

    page: int | None

    content: str

    relevance_score: float | None = None


@dataclass(slots=True)
class RetrievedKnowledge:
    """
    Collection of retrieved knowledge.
    """

    items: list[KnowledgeItem] = field(
        default_factory=list
    )

    def is_empty(self) -> bool:
        return len(self.items) == 0
