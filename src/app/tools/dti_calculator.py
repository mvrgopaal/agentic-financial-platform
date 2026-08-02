from app.tools.tool_definition import ToolDefinition

from .mortgage_guidelines import (
    DTI_EXCELLENT,
    DTI_GOOD,
    DTI_ACCEPTABLE,
)

"""
Debt-to-Income (DTI) Calculator

This module calculates a borrower's monthly debt-to-income ratio.
"""

from dataclasses import dataclass


@dataclass
class DTIResult:
    monthly_income: float
    monthly_debt: float
    dti_percent: float
    status: str


def calculate_dti(
    monthly_income: float,
    monthly_debt: float,
) -> DTIResult:
    """
    Calculate Debt-to-Income Ratio.

    Formula:
        DTI = (Monthly Debt / Monthly Income) * 100

    Args:
        monthly_income: Gross monthly income.
        monthly_debt: Total monthly debt obligations.

    Returns:
        DTIResult
    """

    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    if monthly_debt < 0:
        raise ValueError("Monthly debt cannot be negative.")

    dti = round((monthly_debt / monthly_income) * 100, 2)

    if dti <= DTI_EXCELLENT:
        status = "Excellent"
    elif dti <= DTI_GOOD:
        status = "Good"
    elif dti <= DTI_ACCEPTABLE:
        status = "Acceptable"
    else:
        status = "High Risk"

    return DTIResult(
        monthly_income=monthly_income,
        monthly_debt=monthly_debt,
        dti_percent=dti,
        status=status,
    )

DTI_TOOL = ToolDefinition(
    name="calculate_dti",
    version="1.0.0",
    description=(
        "Calculates a borrower's debt-to-income ratio "
        "using gross monthly income and monthly debt."
    ),
    function=calculate_dti,
    input_schema={
        "type": "object",
        "properties": {
            "monthly_income": {
                "type": "number",
                "exclusiveMinimum": 0,
                "description": (
                    "Borrower's gross monthly income."
                ),
            },
            "monthly_debt": {
                "type": "number",
                "minimum": 0,
                "description": (
                    "Borrower's recurring monthly debt."
                ),
            },
        },
        "required": [
            "monthly_income",
            "monthly_debt",
        ],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "monthly_income": {
                "type": "number",
            },
            "monthly_debt": {
                "type": "number",
            },
            "dti_percent": {
                "type": "number",
            },
            "status": {
                "type": "string",
            },
        },
        "required": [
            "dti_percent",
            "status",
        ],
    },
    capabilities=(
        "debt_to_income_analysis",
        "borrower_risk_analysis",
        "mortgage_prequalification",
    ),
    requires=(
        "monthly_income",
        "monthly_debt",
    ),
    produces=(
        "dti_percent",
        "status",
    ),
    category="mortgage_risk",
    side_effects=False,
    parallel_safe=True,
    timeout_seconds=5,
    estimated_cost=0.0,
    tags=(
        "mortgage",
        "underwriting",
        "borrower",
        "dti",
    ),
)

if __name__ == "__main__":
    result = calculate_dti(
        monthly_income=8000,
        monthly_debt=200,
    )

    print(result)
