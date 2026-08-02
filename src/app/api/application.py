"""
REST API for the Agentic Financial Platform.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, status

from app.agents.financial_agent import FinancialAgent
from app.api.models import (
    HealthResponse,
    MortgageAnalysisRequest,
    MortgageAnalysisResponse,
    ToolExecutionResponse,
    TraceSpanResponse,
    VersionResponse,
)


SERVICE_NAME = "Agentic Financial Platform"
SERVICE_VERSION = "2.0.0"


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """
    Create application-scoped platform dependencies once.

    The FinancialAgent is initialized during startup and reused
    across requests instead of being rebuilt for every call.
    """

    application.state.financial_agent = FinancialAgent()

    yield


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description=(
        "Provider-independent Agentic AI platform for "
        "preliminary financial and mortgage analysis."
    ),
    lifespan=lifespan,
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Platform"],
)
def health() -> HealthResponse:
    """
    Confirm that the API process is running.
    """

    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
    )


@app.get(
    "/version",
    response_model=VersionResponse,
    tags=["Platform"],
)
def version() -> VersionResponse:
    """
    Return the deployed platform version.
    """

    return VersionResponse(
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        phase="Phase 2 — Enterprise Platform",
    )


@app.post(
    "/api/v1/mortgage/analyze",
    response_model=MortgageAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Mortgage"],
)
def analyze_mortgage(
    request: MortgageAnalysisRequest,
) -> MortgageAnalysisResponse:
    """
    Run the complete mortgage-analysis workflow.
    """

    try:
        agent: FinancialAgent = (
            app.state.financial_agent
        )

        result = agent.run(
            user_goal=request.user_goal,
            inputs=request.inputs,
        )

        return MortgageAnalysisResponse(
            selected_tools=list(result.selected_tools),
            execution_results=[
                ToolExecutionResponse(
                    tool_name=item.tool_name,
                    success=item.success,
                    outputs=item.outputs,
                    error=item.error,
                )
                for item in result.execution_results
            ],
            verified_financial_information=(
                result.final_context
            ),
            retrieved_item_count=(
                result.retrieved_item_count
            ),
            preliminary_assessment=result.ai_answer,
            trace_id=result.trace_id,
            trace_spans=[
                TraceSpanResponse(
                    name=span.name,
                    duration_ms=span.duration_ms,
                    status=span.status,
                    attributes=span.attributes,
                )
                for span in result.trace_spans
            ],
            disclaimer=(
                "This response is a preliminary educational "
                "assessment and is not a final underwriting "
                "approval or credit decision."
            ),
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The mortgage analysis could not be completed."
            ),
        ) from exc
