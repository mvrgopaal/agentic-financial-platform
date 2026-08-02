from app.tools.tool_definition import ToolDefinition

"""
Loan-to-Value (LTV) Calculator
"""

from dataclasses import dataclass

from .mortgage_guidelines import (
    LTV_ACCEPTABLE,
    LTV_EXCELLENT,
    LTV_GOOD,
)


@dataclass
class LTVResult:
    property_value: float
    loan_amount: float
    ltv_percent: float
    status: str


def calculate_ltv(
    property_value: float,
    loan_amount: float,
) -> LTVResult:
    """
    Calculate Loan-to-Value ratio.

    Formula:
        LTV = (Loan Amount / Property Value) * 100
    """

    if property_value <= 0:
        raise ValueError(
            "Property value must be greater than zero."
        )

    if loan_amount < 0:
        raise ValueError(
            "Loan amount cannot be negative."
        )

    if loan_amount > property_value * 1.5:
        raise ValueError(
            "Loan amount appears unrealistic."
        )

    ltv = round(
        (loan_amount / property_value) * 100,
        2,
    )

    if ltv <= LTV_EXCELLENT:
        status = "Excellent"
    elif ltv <= LTV_GOOD:
        status = "Good"
    elif ltv <= LTV_ACCEPTABLE:
        status = "Acceptable"
    else:
        status = "High Risk"

    return LTVResult(
        property_value=property_value,
        loan_amount=loan_amount,
        ltv_percent=ltv,
        status=status,
    )

LTV_TOOL = ToolDefinition(
    name="calculate_ltv",
    version="1.0.0",
    description=(
        "Calculates the loan-to-value ratio using the "
        "mortgage loan amount and property value."
    ),
    function=calculate_ltv,
    input_schema={
        "type": "object",
        "properties": {
            "property_value": {
                "type": "number",
                "exclusiveMinimum": 0,
                "description": (
                    "Appraised value or purchase price "
                    "of the property."
                ),
            },
            "loan_amount": {
                "type": "number",
                "minimum": 0,
                "description": (
                    "Requested mortgage loan amount."
                ),
            },
        },
        "required": [
            "property_value",
            "loan_amount",
        ],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "property_value": {
                "type": "number",
            },
            "loan_amount": {
                "type": "number",
            },
            "ltv_percent": {
                "type": "number",
            },
            "status": {
                "type": "string",
            },
        },
        "required": [
            "ltv_percent",
            "status",
        ],
    },
    capabilities=(
        "loan_to_value_analysis",
        "collateral_risk_analysis",
        "mortgage_prequalification",
    ),
    requires=(
        "property_value",
        "loan_amount",
    ),
    produces=(
        "ltv_percent",
        "status",
    ),
    category="mortgage_risk",
    side_effects=False,
    parallel_safe=True,
    timeout_seconds=5,
    estimated_cost=0.0,
    tags=(
        "mortgage",
        "property",
        "collateral",
        "ltv",
    ),
)
if __name__ == "__main__":

    result = calculate_ltv(
        property_value=500000,
        loan_amount=400000,
    )

    print(result)
