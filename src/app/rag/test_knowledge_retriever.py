from app.rag.knowledge_retriever import (
    KnowledgeRetriever,
)


def main() -> None:
    retriever = KnowledgeRetriever()

    knowledge = retriever.retrieve(
        query=(
            "What debts must be included in the "
            "mortgage qualifying ratio?"
        ),
        k=3,
    )

    print(
        f"\nRetrieved {len(knowledge.items)} "
        "knowledge item(s)"
    )

    for index, item in enumerate(
        knowledge.items,
        start=1,
    ):
        print("\n" + "=" * 70)
        print(f"Knowledge Item {index}")
        print(f"Source: {item.source}")
        print(f"Page: {item.page}")
        print("\nContent:")
        print(item.content[:700])


if __name__ == "__main__":
    main()
