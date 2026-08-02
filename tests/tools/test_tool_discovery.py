from app.tools.tool_discovery import discover_tools


def test_discovers_expected_tools() -> None:
    tools = discover_tools()

    identities = {
        (tool.name, tool.version)
        for tool in tools
    }

    assert (
        "calculate_dti",
        "1.0.0",
    ) in identities

    assert (
        "calculate_ltv",
        "1.0.0",
    ) in identities

    assert (
        "calculate_loan_amount",
        "1.0.0",
    ) in identities

    assert (
        "calculate_monthly_payment",
        "1.0.0",
    ) in identities


def test_discovered_tools_have_callable_functions() -> None:
    tools = discover_tools()

    assert tools

    for tool in tools:
        assert callable(tool.function)
