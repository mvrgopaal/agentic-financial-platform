"""
HTTP request and response contracts for the platform API.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MortgageAnalysisRequest(BaseModel):
    """
    Request body for a preliminary mortgage analysis.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    user_goal: str = Field(
        min_length=1,
        description=(
            "The borrower's mortgage question or objective."
        ),
        examples=[
            (
                "I am buying a $600,000 home with 10% down. "
                "Can I qualify?"
            )
        ],
    )

    inputs: dict[str, Any] = Field(
        description=(
            "Structured financial inputs used by deterministic tools."
        ),
        examples=[
            {
                "property_value": 600000,
                "down_payment": 60000,
                "monthly_income": 12000,
                "monthly_debt": 2500,
                "annual_interest_rate": 6.5,
                "loan_term_years": 30,
            }
        ],
    )


class ToolExecutionResponse(BaseModel):
    """
    Public representation of one tool execution.
    """

    tool_name: str
    success: bool
    outputs: dict[str, Any]
    error: str | None = None


class TraceSpanResponse(BaseModel):
    """
    Public representation of one trace span.
    """

    name: str
    duration_ms: float
    status: str
    attributes: dict[str, Any]


class MortgageAnalysisResponse(BaseModel):
    """
    Complete preliminary mortgage-analysis response.
    """

    selected_tools: list[str]
    execution_results: list[ToolExecutionResponse]
    verified_financial_information: dict[str, Any]
    retrieved_item_count: int
    preliminary_assessment: str
    trace_id: str
    trace_spans: list[TraceSpanResponse]
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    service: str


class VersionResponse(BaseModel):
    service: str
    version: str
    phase: str
