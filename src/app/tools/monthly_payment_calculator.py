from app.tools.tool_definition import ToolDefinition
"""
Monthly mortgage payment calculator.

Calculates the monthly principal-and-interest payment
for a fixed-rate, fully amortizing mortgage.

This tool does not include:
- Property taxes
- Homeowners insurance
- Mortgage insurance
- HOA dues
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MonthlyPaymentResult:
    """
    Structured output from the monthly-payment calculation.
    """

    loan_amount: float
    annual_interest_rate: float
    loan_term_years: int
    number_of_payments: int
    monthly_interest_rate: float
    monthly_principal_interest: float
    total_payments: float
    total_interest: float


def calculate_monthly_payment(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
) -> MonthlyPaymentResult:
    """
    Calculate the monthly principal-and-interest payment.

    Standard fixed-rate mortgage formula:

        M = P × [r(1 + r)^n] / [(1 + r)^n - 1]

    Where:
        M = monthly payment
        P = principal or loan amount
        r = monthly interest rate
        n = total number of monthly payments
    """

    _validate_inputs(
        loan_amount=loan_amount,
        annual_interest_rate=annual_interest_rate,
        loan_term_years=loan_term_years,
    )

    number_of_payments = loan_term_years * 12

    monthly_interest_rate = (
        annual_interest_rate / 100
    ) / 12

    if monthly_interest_rate == 0:
        monthly_payment = (
            loan_amount / number_of_payments
        )
    else:
        growth_factor = (
            1 + monthly_interest_rate
        ) ** number_of_payments

        monthly_payment = (
            loan_amount
            * monthly_interest_rate
            * growth_factor
            / (growth_factor - 1)
        )

    total_payments = (
        monthly_payment * number_of_payments
    )

    total_interest = (
        total_payments - loan_amount
    )

    return MonthlyPaymentResult(
        loan_amount=round(loan_amount, 2),
        annual_interest_rate=round(
            annual_interest_rate,
            4,
        ),
        loan_term_years=loan_term_years,
        number_of_payments=number_of_payments,
        monthly_interest_rate=round(
            monthly_interest_rate,
            8,
        ),
        monthly_principal_interest=round(
            monthly_payment,
            2,
        ),
        total_payments=round(
            total_payments,
            2,
        ),
        total_interest=round(
            total_interest,
            2,
        ),
    )


def _validate_inputs(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
) -> None:
    """
    Validate calculator inputs before performing the calculation.
    """

    if loan_amount <= 0:
        raise ValueError(
            "Loan amount must be greater than zero."
        )

    if annual_interest_rate < 0:
        raise ValueError(
            "Annual interest rate cannot be negative."
        )

    if annual_interest_rate > 100:
        raise ValueError(
            "Annual interest rate cannot exceed 100 percent."
        )

    if isinstance(loan_term_years, bool):
        raise TypeError(
            "Loan term must be an integer number of years."
        )

    if not isinstance(loan_term_years, int):
        raise TypeError(
            "Loan term must be an integer number of years."
        )

    if loan_term_years <= 0:
        raise ValueError(
            "Loan term must be greater than zero."
        )

    if loan_term_years > 50:
        raise ValueError(
            "Loan term cannot exceed 50 years."
        )


MONTHLY_PAYMENT_TOOL = ToolDefinition(
    name="calculate_monthly_payment",
    version="1.0.0",
    description=(
        "Calculates monthly principal and interest for "
        "a fixed-rate, fully amortizing mortgage."
    ),
    function=calculate_monthly_payment,
    input_schema={
        "type": "object",
        "properties": {
            "loan_amount": {
                "type": "number",
                "exclusiveMinimum": 0,
            },
            "annual_interest_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
            },
            "loan_term_years": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
            },
        },
        "required": [
            "loan_amount",
            "annual_interest_rate",
            "loan_term_years",
        ],
        "additionalProperties": False,
    },
    output_schema={
        "type": "object",
        "properties": {
            "monthly_principal_interest": {
                "type": "number",
            },
            "total_payments": {
                "type": "number",
            },
            "total_interest": {
                "type": "number",
            },
        },
        "required": [
            "monthly_principal_interest",
            "total_payments",
            "total_interest",
        ],
    },
    capabilities=(
        "mortgage_payment_calculation",
        "principal_and_interest_estimation",
        "mortgage_cost_analysis",
    ),
    requires=(
        "loan_amount",
        "annual_interest_rate",
        "loan_term_years",
    ),
    produces=(
        "monthly_principal_interest",
        "total_payments",
        "total_interest",
    ),
    category="mortgage_calculation",
    side_effects=False,
    parallel_safe=True,
    timeout_seconds=5,
    estimated_cost=0.0,
    tags=(
        "mortgage",
        "payment",
        "principal",
        "interest",
    ),
)
if __name__ == "__main__":
    result = calculate_monthly_payment(
        loan_amount=540000,
        annual_interest_rate=6.5,
        loan_term_years=30,
    )

    print(result)
