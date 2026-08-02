"""
Simple rule-based planner.

The planner decides which financial tool should
handle a user's request.
"""

from dataclasses import dataclass


@dataclass
class Plan:
    tool_name: str | None
    reasoning: str


class Planner:

    def create_plan(self, user_question: str) -> Plan:

        question = user_question.lower()

        if "dti" in question or "debt" in question:
            return Plan(
                tool_name="calculate_dti",
                reasoning="Detected debt-to-income related request.",
            )

        if "ltv" in question or "loan-to-value" in question:
            return Plan(
                tool_name="calculate_ltv",
                reasoning="Detected loan-to-value request.",
            )

        return Plan(
            tool_name=None,
            reasoning="No matching financial tool found.",
        )


if __name__ == "__main__":

    planner = Planner()

    questions = [
        "Calculate my DTI",
        "What is my LTV?",
        "Explain FHA loans",
    ]

    for question in questions:

        plan = planner.create_plan(question)

        print("-" * 60)
        print(question)
        print(plan)
