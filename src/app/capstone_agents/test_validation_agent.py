"""
Integration test for ValidationAgent.
"""

from app.agents.prompt_builder import PromptBuilder
from app.capstone_agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
)
from app.capstone_agents.knowledge_agent import (
    KnowledgeAgent,
)
from app.capstone_agents.recommendation_agent import (
    RecommendationAgent,
)
from app.capstone_agents.validation_agent import (
    ValidationAgent,
)
from app.configuration.configuration_manager import (
    ConfigurationManager,
)
from app.providers.provider_factory import ProviderFactory
from app.reasoning.reasoning_engine import ReasoningEngine


def main() -> None:
    user_question = (
        "I am buying a $600,000 home with 10% down. "
        "My gross monthly income is $12,000 and my "
        "monthly debt is $2,500. The interest rate is "
        "6.5% for 30 years. Can I qualify?"
    )

    inputs = {
        "property_value": 600000,
        "down_payment": 60000,
        "monthly_income": 12000,
        "monthly_debt": 2500,
        "annual_interest_rate": 6.5,
        "loan_term_years": 30,
    }

    configuration_manager = ConfigurationManager()

    provider = ProviderFactory(
        configuration_manager=configuration_manager
    ).create_llm_provider()

    financial_result = FinancialAnalysisAgent().run(
        user_goal=user_question,
        inputs=inputs,
    )

    knowledge_result = KnowledgeAgent(
        default_top_k=3
    ).run(
        query=user_question
    )

    recommendation_result = RecommendationAgent(
        prompt_builder=PromptBuilder(),
        reasoning_engine=ReasoningEngine(
            provider=provider
        ),
    ).run(
        user_question=user_question,
        financial_analysis=financial_result,
        knowledge_result=knowledge_result,
    )

    validation_result = ValidationAgent().validate(
        financial_analysis=financial_result,
        knowledge_result=knowledge_result,
        recommendation_result=(
            recommendation_result
        ),
    )

    print("Valid:", validation_result.valid)
    print(
        "Error count:",
        validation_result.error_count,
    )
    print(
        "Warning count:",
        validation_result.warning_count,
    )

    print("\nValidation Issues")
    print("-" * 70)

    if not validation_result.issues:
        print("No validation issues.")
        return

    for issue in validation_result.issues:
        print(
            f"[{issue.severity.upper()}] "
            f"{issue.code}: {issue.message}"
        )


if __name__ == "__main__":
    main()
