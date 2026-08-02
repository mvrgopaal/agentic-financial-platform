from app.tools.tool_definition import ToolDefinition
"""
Loan amount calculator.

Calculates the requested mortgage loan amount from
property value and down-payment amount.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoanAmountResult:
    property_value: float
    down_payment: float
    loan_amount: float
    down_payment_percent: float


def calculate_loan_amount(
    property_value: float,
    down_payment: float,
) -> LoanAmountResult:
    """
    Calculate the mortgage loan amount.

    Formula:
        loan_amount = property_value - down_payment
    """

    if property_value <= 0:
        raise ValueError("Property value must be greater than zero.")

    if down_payment < 0:
        raise ValueError("Down payment cannot be negative.")

    if down_payment > property_value:
        raise ValueError(
            "Down payment cannot exceed the property value."
        )

    loan_amount = property_value - down_payment

    down_payment_percent = (
        down_payment / property_value
    ) * 100

    return LoanAmountResult(
        property_value=property_value,
        down_payment=down_payment,
        loan_amount=round(loan_amount, 2),
        down_payment_percent=round(
            down_payment_percent,
            2,
        ),
    )

LOAN_AMOUNT_TOOL = ToolDefinition(
    name="calculate_loan_amount",
    version="1.0.0",
    description=(
        "Calculates the requested mortgage loan amount "
        "from property value and down payment."
    ),
    function=calculate_loan_amount,
    input_schema={
        "type": "object",
        "properties": {
            "property_value": {
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "down_payment": {
                "type": "number",
                "minimum": 0,
            },
        },
        "required": [
            "property_value",
            "down_payment",
        ],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "property_value": {
                "type": "number",
            },
            "down_payment": {
                "type": "number",
            },
            "loan_amount": {
                "type": "number",
            },
            "down_payment_percent": {
                "type": "number",
            },
        },
        "required": [
            "loan_amount",
            "down_payment_percent",
        ],
    },
    capabilities=(
        "loan_amount_calculation",
        "down_payment_analysis",
        "mortgage_prequalification",
    ),
    requires=(
        "property_value",
        "down_payment",
    ),
    produces=(
        "loan_amount",
        "down_payment_percent",
    ),
    category="mortgage_calculation",
    side_effects=False,
    parallel_safe=True,
    timeout_seconds=5,
    estimated_cost=0.0,
    tags=(
        "mortgage",
        "loan_amount",
        "down_payment",
    ),
)
if __name__ == "__main__":
    result = calculate_loan_amount(
        property_value=600000,
        down_payment=60000,
    )

    print(result)
