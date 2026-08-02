from pprint import pprint

from app.agents.dependency_builder import DependencyBuilder
from app.execution.execution_context import ExecutionContext
from app.execution.execution_engine import ExecutionEngine
from app.tools.tool_registry import list_tool_definitions


def main() -> None:
    tools = list_tool_definitions()

    builder = DependencyBuilder()
    graph = builder.build(tools)

    context = ExecutionContext(
        values={
            "property_value": 600000,
            "down_payment": 60000,
            "monthly_income": 12000,
            "monthly_debt": 2500,
            "annual_interest_rate": 6.5,
            "loan_term_years": 30,
        }
    )

    engine = ExecutionEngine()

    results = engine.execute(
        graph=graph,
        context=context,
    )

    print("\nFinal Execution Results")
    print("=" * 60)
    pprint(results)

    print("\nFinal Execution Context")
    print("=" * 60)
    pprint(context.values)


if __name__ == "__main__":
    main()
