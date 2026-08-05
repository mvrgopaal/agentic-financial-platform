"""
Integration test for the Recommendation Agent.

This test uses the configured LLM provider and may make
an OpenAI or local MLX request.
"""

from app.configuration.configuration_manager import (
    ConfigurationManager,
)
from app.providers.provider_factory import ProviderFactory
from app.reasoning.reasoning_engine import ReasoningEngine
from app.agents.prompt_builder import PromptBuilder

from app.capstone_agents.agent_result import (
    FinancialAnalysisResult,
)
from app.capstone_agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
)
from app.capstone_agents.knowledge_agent import (
    KnowledgeAgent,
)
from app.capstone_agents.recommendation_agent import (
    RecommendationAgent,
)


def main() -> None:
    configuration_manager = ConfigurationManager()

    provider = ProviderFactory(
        configuration_manager=configuration_manager
    ).create_llm_provider()

    recommendation_agent = RecommendationAgent(
        prompt_builder=PromptBuilder(),
        reasoning_engine=ReasoningEngine(
            provider=provider
        ),
    )

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

    financial_analysis = (
        FinancialAnalysisAgent().run(
            user_goal=user_question,
            inputs=inputs,
        )
    )

    knowledge_result = KnowledgeAgent(
        default_top_k=3
    ).run(
        query=user_question
    )

    result = recommendation_agent.run(
        user_question=user_question,
        financial_analysis=financial_analysis,
        knowledge_result=knowledge_result,
    )

    print("Success:", result.success)

    if result.error:
        print("Error code:", result.error.code)
        print(
            "Error message:",
            result.error.message,
        )
        print(
            "Retryable:",
            result.error.retryable,
        )

        if result.error.details:
            print(
                "Error details:",
                result.error.details,
            )

        return

    print("\nRecommendation")
    print("-" * 70)
    print(result.answer)

    print("\nPrompt Context")
    print("-" * 70)

    if result.prompt:
        print(result.prompt.context_summary)

        print(
            "\nRetrieved guideline count:",
            len(
                result.prompt.retrieved_guidelines
            ),
        )


if __name__ == "__main__":
    main()
