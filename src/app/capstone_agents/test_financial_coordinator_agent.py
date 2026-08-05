"""
End-to-end integration test for FinancialCoordinatorAgent.
"""

from app.agents.prompt_builder import PromptBuilder
from app.capstone_agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
)
from app.capstone_agents.financial_coordinator_agent import (
    FinancialCoordinatorAgent,
)
from app.capstone_agents.knowledge_agent import KnowledgeAgent
from app.capstone_agents.recommendation_agent import (
    RecommendationAgent,
)
from app.capstone_agents.validation_agent import ValidationAgent
from app.configuration.configuration_manager import (
    ConfigurationManager,
)
from app.providers.provider_factory import ProviderFactory
from app.reasoning.reasoning_engine import ReasoningEngine


def main() -> None:
    configuration_manager = ConfigurationManager()

    provider = ProviderFactory(
        configuration_manager=configuration_manager
    ).create_llm_provider()

    coordinator = FinancialCoordinatorAgent(
        financial_analysis_agent=FinancialAnalysisAgent(),
        knowledge_agent=KnowledgeAgent(
            default_top_k=3,
        ),
        recommendation_agent=RecommendationAgent(
            prompt_builder=PromptBuilder(),
            reasoning_engine=ReasoningEngine(
                provider=provider,
            ),
        ),
        validation_agent=ValidationAgent(),
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

    result = coordinator.run(
        user_question=user_question,
        inputs=inputs,
        retrieval_count=3,
    )

    print("\nCoordinator Result")
    print("=" * 70)
    print("Success:", result.success)
    print("Trace ID:", result.trace_id)

    print("\nTrace Spans")
    print("-" * 70)

    for span in result.trace_spans:
        print(
            f"{span.name}: "
            f"{span.duration_ms:.2f} ms "
            f"[{span.status}]"
        )

    if result.error:
        print("\nCoordinator Error")
        print("-" * 70)
        print("Code:", result.error.code)
        print("Message:", result.error.message)
        print("Retryable:", result.error.retryable)
        print("Details:", result.error.details)

    print("\nFinancial Analysis")
    print("-" * 70)
    print(
        "Success:",
        result.financial_analysis.success,
    )
    print(
        "Selected tools:",
        result.financial_analysis.selected_tools,
    )
    print(
        "Verified facts:",
        result.financial_analysis.verified_facts,
    )

    if result.knowledge_result:
        print("\nKnowledge Agent")
        print("-" * 70)
        print(
            "Success:",
            result.knowledge_result.success,
        )
        print(
            "Evidence available:",
            result.knowledge_result.evidence_available,
        )
        print(
            "Retrieved items:",
            result.knowledge_result.retrieved_item_count,
        )

    if result.recommendation_result:
        print("\nRecommendation Agent")
        print("-" * 70)
        print(
            "Success:",
            result.recommendation_result.success,
        )
        print(
            result.recommendation_result.answer,
        )

    if result.validation_result:
        print("\nValidation Agent")
        print("-" * 70)
        print(
            "Valid:",
            result.validation_result.valid,
        )
        print(
            "Errors:",
            result.validation_result.error_count,
        )
        print(
            "Warnings:",
            result.validation_result.warning_count,
        )

        for issue in result.validation_result.issues:
            print(
                f"[{issue.severity.upper()}] "
                f"{issue.code}: {issue.message}"
            )


if __name__ == "__main__":
    main()
