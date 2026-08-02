"""
End-to-end mortgage Financial Agent.

Workflow:
1. Interpret the user's goal.
2. Select financial tools by capability.
3. Build the tool dependency graph.
4. Execute deterministic calculations.
5. Retrieve relevant mortgage guidelines.
6. Build a grounded prompt.
7. Generate a preliminary AI assessment.

This application provides a preliminary assessment only.
It does not issue final underwriting approval or a credit decision.
"""

from dataclasses import dataclass
from typing import Any

from app.agents.capability_planner import (
    CapabilityPlanner,
    PlanningRequest,
)
from app.agents.dependency_builder import DependencyBuilder
from app.agents.prompt_builder import PromptBuilder
from app.execution.execution_context import ExecutionContext
from app.execution.execution_engine import ExecutionEngine
from app.execution.execution_result import ExecutionResult
from app.rag.knowledge_retriever import KnowledgeRetriever
from app.reasoning.reasoning_engine import ReasoningEngine
from app.tools.tool_registry import get_tool
from app.configuration.configuration_manager import ConfigurationManager
from app.providers.provider_factory import ProviderFactory


@dataclass(slots=True)
class FinancialAgentResult:
    """
    Complete result returned by the Financial Agent.
    """

    selected_tools: tuple[str, ...]
    execution_results: list[ExecutionResult]
    final_context: dict[str, Any]
    retrieved_item_count: int
    ai_answer: str


class FinancialAgent:
    """
    Application-level coordinator for mortgage analysis.

    This class coordinates the platform components. It does not
    calculate mortgage values or directly call the LLM.
    """
    def __init__(self) -> None:
        configuration_manager = ConfigurationManager()

        provider_factory = ProviderFactory(
            configuration_manager=configuration_manager
        )

        llm_provider = provider_factory.create_llm_provider()

        self.config = configuration_manager.config
        self.planner = CapabilityPlanner()
        self.dependency_builder = DependencyBuilder()
        self.execution_engine = ExecutionEngine()
        self.knowledge_retriever = KnowledgeRetriever()
        self.prompt_builder = PromptBuilder()
        self.reasoning_engine = ReasoningEngine(
            provider=llm_provider
        )
    def run(
        self,
        user_goal: str,
        inputs: dict[str, Any],
        retrieval_count: int = 5,
    ) -> FinancialAgentResult:
        """
        Run the complete mortgage-analysis workflow.

        Args:
            user_goal:
                The user's mortgage question or objective.
            inputs:
                Structured financial inputs supplied by the user.
            retrieval_count:
                Maximum number of mortgage-guideline excerpts
                requested from the knowledge retriever.

        Returns:
            A FinancialAgentResult containing calculations,
            tool status, retrieved-knowledge count, and the
            preliminary AI assessment.
        """

        self._validate_request(
            user_goal=user_goal,
            inputs=inputs,
	    retrieval_count=self.config.retrieval.top_k
        )

        # 1. Determine the required business capabilities
        # and select matching tools.
        planning_result = self.planner.plan(
            PlanningRequest(
                user_goal=user_goal,
                available_inputs=inputs,
            )
        )

        # 2. Convert selected tool names into complete
        # ToolDefinition objects.
        selected_tool_definitions = [
            get_tool(tool_name)
            for tool_name in planning_result.selected_tools
        ]

        # 3. Build dependencies among only the selected tools.
        dependency_graph = self.dependency_builder.build(
            selected_tool_definitions
        )

        self._print_execution_plan(
            selected_tools=planning_result.selected_tools,
            dependency_graph=dependency_graph,
        )

        # 4. Initialize shared runtime state with user inputs.
        context = ExecutionContext(
            values=dict(inputs)
        )

        # 5. Execute deterministic tools in dependency order.
        execution_results = self.execution_engine.execute(
            graph=dependency_graph,
            context=context,
        )

        failed_results = [
            result
            for result in execution_results
            if not result.success
        ]

        if failed_results:
            failure_details = "; ".join(
                (
                    f"{result.tool_name}: "
                    f"{result.error or 'unknown error'}"
                )
                for result in failed_results
            )

            return FinancialAgentResult(
                selected_tools=planning_result.selected_tools,
                execution_results=execution_results,
                final_context=dict(context.values),
                retrieved_item_count=0,
                ai_answer=(
                    "The preliminary assessment could not be "
                    "completed because one or more verified "
                    "calculations failed. "
                    f"Details: {failure_details}"
                ),
            )

        # 6. Retrieve guideline evidence relevant to the question.
        knowledge = self.knowledge_retriever.retrieve(
            query=user_goal,
            k=self.config.retrieval.top_k,
        )

        # 7. Combine verified calculations, retrieved evidence,
        # and the user's question into a structured prompt.
        prompt = self.prompt_builder.build(
            user_question=user_goal,
            context=context,
            knowledge=knowledge,
        )

        # 8. Ask the reasoning model for a grounded explanation.
        reasoning_result = self.reasoning_engine.reason(
            prompt
        )

        if reasoning_result.success:
            ai_answer = reasoning_result.answer
        else:
            ai_answer = (
                "The verified mortgage calculations and guideline "
                "retrieval completed successfully, but the AI "
                "assessment could not be generated. "
                f"Reason: {reasoning_result.error}"
            )

        return FinancialAgentResult(
            selected_tools=planning_result.selected_tools,
            execution_results=execution_results,
            final_context=dict(context.values),
            retrieved_item_count=len(knowledge.items),
            ai_answer=ai_answer,
        )

    def _validate_request(
        self,
        user_goal: str,
        inputs: dict[str, Any],
        retrieval_count: int,
    ) -> None:
        """
        Validate the application-level request.
        """

        if not isinstance(user_goal, str):
            raise TypeError(
                "user_goal must be a string, "
                f"not {type(user_goal).__name__}."
            )

        if not user_goal.strip():
            raise ValueError(
                "user_goal cannot be empty."
            )

        if not isinstance(inputs, dict):
            raise TypeError(
                "inputs must be a dictionary."
            )

        if retrieval_count <= 0:
            raise ValueError(
                "retrieval_count must be greater than zero."
            )

    def _print_execution_plan(
        self,
        selected_tools: tuple[str, ...],
        dependency_graph,
    ) -> None:
        """
        Display the selected tools and execution stages.

        This is useful for the Version 1 demonstration.
        It can later be replaced with structured logging.
        """

        print("\nSelected Tools")
        print("-" * 60)

        for tool_name in selected_tools:
            print(f"- {tool_name}")

        print("\nExecution Stages")
        print("-" * 60)

        stages = dependency_graph.parallel_execution_groups()

        for stage_number, stage in enumerate(
            stages,
            start=1,
        ):
            print(
                f"Stage {stage_number}: {stage}"
            )


def print_demo_result(
    user_goal: str,
    result: FinancialAgentResult,
) -> None:
    """
    Display a clean, investor-friendly demonstration result.
    """

    print("\n" + "=" * 70)
    print("FINANCIAL AGENT PLATFORM")
    print("Mortgage Qualification Assistant")
    print("=" * 70)

    print("\nQuestion")
    print("-" * 70)
    print(user_goal)

    print("\nVerified Financial Information")
    print("-" * 70)

    for key, value in sorted(
        result.final_context.items()
    ):
        print(f"{key}: {value}")

    print("\nTool Execution Status")
    print("-" * 70)

    for execution_result in result.execution_results:
        status = (
            "SUCCESS"
            if execution_result.success
            else "FAILED"
        )

        print(
            f"{execution_result.tool_name}: {status}"
        )

        if execution_result.error:
            print(
                f"  Error: {execution_result.error}"
            )

    print("\nKnowledge Retrieval")
    print("-" * 70)
    print(
        "Mortgage guideline excerpts retrieved: "
        f"{result.retrieved_item_count}"
    )

    print("\nPreliminary AI Assessment")
    print("-" * 70)
    print(result.ai_answer)

    print("\n" + "-" * 70)
    print(
        "Important: This is a preliminary educational assessment. "
        "Final eligibility depends on the selected loan program, "
        "credit, verified income and employment, assets, reserves, "
        "property eligibility, mortgage insurance, and complete "
        "underwriting review."
    )
    print("-" * 70)


def main() -> None:
    """
    Run the Version 1 mortgage-agent demonstration.
    """

    user_goal = (
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

    agent = FinancialAgent()

    result = agent.run(
        user_goal=user_goal,
        inputs=inputs,
    )

    print_demo_result(
        user_goal=user_goal,
        result=result,
    )


if __name__ == "__main__":
    main()
