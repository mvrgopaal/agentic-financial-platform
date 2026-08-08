"""
Manual integration test for KnowledgeAgent.
"""

from app.capstone_agents.knowledge_agent import (
    KnowledgeAgent,
)


def main() -> None:
    agent = KnowledgeAgent(
        default_top_k=3
    )

    result = agent.run(
        query=(
            "What mortgage guidance is relevant "
            "to debt-to-income qualification?"
        )
    )

    print("Success:", result.success)
    print(
        "Retrieved item count:",
        result.retrieved_item_count,
    )

    if result.error:
        print("Error code:", result.error.code)
        print("Error message:", result.error.message)
        print("Retryable:", result.error.retryable)

        if result.error.details:
            print("Error details:", result.error.details)

    print(
        "Evidence available:",
        result.evidence_available,
    )

    print(
        "Requested item count:",
        result.requested_item_count,
    )

    print(
        "Retrieved item count:",
        result.retrieved_item_count,
    )
    if result.knowledge is None:
        print("No knowledge returned.")
        return

    for index, item in enumerate(
        result.knowledge.items,
        start=1,
    ):
        print()
        print(f"Item {index}")
        print("-" * 60)
        print(item)


if __name__ == "__main__":
    main()
