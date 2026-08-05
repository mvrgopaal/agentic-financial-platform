"""
Manual integration test for FinancialAnalysisAgent.
"""

from app.capstone_agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
)


def main() -> None:
    agent = FinancialAnalysisAgent()

    result = agent.run(
        user_goal=(
            "Calculate DTI, loan amount, LTV, "
            "and monthly payment."
        ),
        inputs={
            "property_value": 600000,
            "down_payment": 60000,
            "monthly_income": 12000,
            "monthly_debt": 2500,
            "annual_interest_rate": 6.5,
            "loan_term_years": 30,
        },
    )

    print("Success:", result.success)
    print("Selected tools:", result.selected_tools)
    print("Verified facts:")

    for key, value in sorted(
        result.verified_facts.items()
    ):
        print(f"  {key}: {value}")

    if result.error:
        print("Error:", result.error)


if __name__ == "__main__":
    main()
