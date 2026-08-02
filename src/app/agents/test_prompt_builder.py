from pprint import pprint

from app.agents.prompt_builder import PromptBuilder
from app.execution.execution_context import ExecutionContext
from app.rag.retrieved_knowledge import (
    KnowledgeItem,
    RetrievedKnowledge,
)


def main() -> None:
    context = ExecutionContext(
        values={
            "property_value": 600000,
            "down_payment": 60000,
            "loan_amount": 540000,
            "dti_percent": 20.83,
            "ltv_percent": 90.0,
            "monthly_principal_interest": 3413.27,
        }
    )

    knowledge = RetrievedKnowledge(
        items=[
            KnowledgeItem(
                source="FHA Single Family Housing Policy Handbook",
                page=1079,
                content=(
                    "All applicable monthly liabilities must "
                    "be included in the qualifying ratio."
                ),
            ),
            KnowledgeItem(
                source="Mortgage guideline test source",
                page=25,
                content=(
                    "Final eligibility depends on the selected "
                    "loan program and complete underwriting review."
                ),
            ),
        ]
    )

    builder = PromptBuilder()

    prompt = builder.build(
        user_question=(
            "Can this borrower qualify for the mortgage?"
        ),
        context=context,
        knowledge=knowledge,
    )

    print("\nStructured Prompt")
    print("=" * 70)
    pprint(prompt)

    print("\nContext Summary")
    print("=" * 70)
    print(prompt.context_summary)

    print("\nRetrieved Guidelines")
    print("=" * 70)

    for guideline in prompt.retrieved_guidelines:
        print(guideline)
        print("-" * 70)


if __name__ == "__main__":
    main()
