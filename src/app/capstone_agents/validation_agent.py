"""
Agent responsible for validating the final mortgage
decision-support output.
"""

from typing import Any

from app.capstone_agents.agent_result import (
    FinancialAnalysisResult,
    KnowledgeAgentResult,
    RecommendationAgentResult,
    ValidationAgentResult,
    ValidationIssue,
)


class ValidationAgent:
    """
    Validate completeness, evidence availability, consistency,
    and mortgage decision-support guardrails.

    This agent does not calculate values, retrieve documents,
    or generate recommendations.
    """

    def validate(
        self,
        financial_analysis: FinancialAnalysisResult,
        knowledge_result: KnowledgeAgentResult,
        recommendation_result: RecommendationAgentResult,
    ) -> ValidationAgentResult:
        """
        Validate outputs produced by the specialized agents.
        """

        issues: list[ValidationIssue] = []

        self._validate_financial_analysis(
            financial_analysis,
            issues,
        )

        self._validate_knowledge(
            knowledge_result,
            issues,
        )

        self._validate_recommendation(
            recommendation_result,
            issues,
        )

        if recommendation_result.success:
            self._validate_guardrails(
                recommendation_result.answer,
                issues,
            )

            self._validate_calculation_references(
                answer=recommendation_result.answer,
                verified_facts=(
                    financial_analysis.verified_facts
                ),
                issues=issues,
            )

        valid = not any(
            issue.severity == "error"
            for issue in issues
        )

        return ValidationAgentResult(
            valid=valid,
            issues=tuple(issues),
        )

    def _validate_financial_analysis(
        self,
        result: FinancialAnalysisResult,
        issues: list[ValidationIssue],
    ) -> None:
        """
        Validate deterministic financial analysis.
        """

        if not result.success:
            issues.append(
                ValidationIssue(
                    code="FINANCIAL_ANALYSIS_FAILED",
                    message=(
                        "Verified financial analysis did not "
                        "complete successfully."
                    ),
                    severity="error",
                )
            )

            return

        if not result.selected_tools:
            issues.append(
                ValidationIssue(
                    code="NO_FINANCIAL_TOOLS_SELECTED",
                    message=(
                        "No deterministic financial tools "
                        "were selected."
                    ),
                    severity="error",
                )
            )

        failed_tools = [
            execution_result.tool_name
            for execution_result
            in result.execution_results
            if not execution_result.success
        ]

        if failed_tools:
            issues.append(
                ValidationIssue(
                    code="FINANCIAL_TOOL_FAILURES",
                    message=(
                        "One or more financial tools failed: "
                        + ", ".join(failed_tools)
                    ),
                    severity="error",
                )
            )

        if not result.verified_facts:
            issues.append(
                ValidationIssue(
                    code="VERIFIED_FACTS_MISSING",
                    message=(
                        "The financial analysis did not return "
                        "verified facts."
                    ),
                    severity="error",
                )
            )

    def _validate_knowledge(
        self,
        result: KnowledgeAgentResult,
        issues: list[ValidationIssue],
    ) -> None:
        """
        Validate retrieval and evidence availability.
        """

        if not result.success:
            issues.append(
                ValidationIssue(
                    code="KNOWLEDGE_RETRIEVAL_FAILED",
                    message=(
                        "Knowledge retrieval did not complete "
                        "successfully."
                    ),
                    severity="error",
                )
            )

            return

        if not result.evidence_available:
            issues.append(
                ValidationIssue(
                    code="SUPPORTING_EVIDENCE_MISSING",
                    message=(
                        "No supporting mortgage evidence "
                        "was available."
                    ),
                    severity="error",
                )
            )

        if result.retrieved_item_count <= 0:
            issues.append(
                ValidationIssue(
                    code="NO_RETRIEVED_ITEMS",
                    message=(
                        "Knowledge retrieval returned no items."
                    ),
                    severity="error",
                )
            )

        if result.knowledge is None:
            issues.append(
                ValidationIssue(
                    code="KNOWLEDGE_OBJECT_MISSING",
                    message=(
                        "Evidence was expected, but the "
                        "knowledge object was missing."
                    ),
                    severity="error",
                )
            )

    def _validate_recommendation(
        self,
        result: RecommendationAgentResult,
        issues: list[ValidationIssue],
    ) -> None:
        """
        Validate the recommendation result contract.
        """

        if not result.success:
            issues.append(
                ValidationIssue(
                    code="RECOMMENDATION_FAILED",
                    message=(
                        "The Recommendation Agent did not "
                        "produce a successful assessment."
                    ),
                    severity="error",
                )
            )

            return

        if not result.answer.strip():
            issues.append(
                ValidationIssue(
                    code="EMPTY_RECOMMENDATION",
                    message=(
                        "The recommendation answer was empty."
                    ),
                    severity="error",
                )
            )

        if result.prompt is None:
            issues.append(
                ValidationIssue(
                    code="PROMPT_TRACE_MISSING",
                    message=(
                        "The generated prompt was not preserved "
                        "for traceability."
                    ),
                    severity="warning",
                )
            )

    def _validate_guardrails(
        self,
        answer: str,
        issues: list[ValidationIssue],
    ) -> None:
        """
        Detect prohibited or unsafe mortgage language.
        """

        normalized_answer = answer.lower()

        prohibited_phrases = (
            "you are approved",
            "your loan is approved",
            "final approval granted",
            "approval is guaranteed",
            "guaranteed approval",
            "you definitely qualify",
            "you are denied",
            "your loan is denied",
        )

        for phrase in prohibited_phrases:
            if phrase in normalized_answer:
                issues.append(
                    ValidationIssue(
                        code="PROHIBITED_DECISION_LANGUAGE",
                        message=(
                            "The recommendation contains "
                            f"prohibited language: '{phrase}'."
                        ),
                        severity="error",
                    )
                )

        disclaimer_signals = (
            "preliminary",
            "not a final",
            "underwriting",
            "credit decision",
            "subject to",
        )

        if not any(
            signal in normalized_answer
            for signal in disclaimer_signals
        ):
            issues.append(
                ValidationIssue(
                    code="DISCLAIMER_MISSING",
                    message=(
                        "The recommendation does not clearly "
                        "state that it is preliminary."
                    ),
                    severity="error",
                )
            )

        limitation_signals = (
            "missing",
            "additional",
            "subject to",
            "depends on",
            "requires verification",
            "underwriting review",
        )

        if not any(
            signal in normalized_answer
            for signal in limitation_signals
        ):
            issues.append(
                ValidationIssue(
                    code="LIMITATIONS_NOT_DISCLOSED",
                    message=(
                        "The recommendation does not identify "
                        "limitations or additional review needs."
                    ),
                    severity="warning",
                )
            )

    def _validate_calculation_references(
        self,
        answer: str,
        verified_facts: dict[str, Any],
        issues: list[ValidationIssue],
    ) -> None:
        """
        Check whether important verified facts are referenced
        in the recommendation.

        This is a lightweight capstone validation. It does not
        attempt full semantic claim verification.
        """

        normalized_answer = answer.lower()

        important_fact_labels = {
            "dti": (
                "dti",
                "debt-to-income",
                "debt to income",
            ),
            "ltv": (
                "ltv",
                "loan-to-value",
                "loan to value",
            ),
            "loan_amount": (
                "loan amount",
                "mortgage amount",
            ),
            "monthly_payment": (
                "monthly payment",
                "principal and interest",
                "payment",
            ),
        }

        for fact_name, labels in important_fact_labels.items():
            if fact_name not in verified_facts:
                continue

            if not any(
                label in normalized_answer
                for label in labels
            ):
                issues.append(
                    ValidationIssue(
                        code="VERIFIED_FACT_NOT_REFERENCED",
                        message=(
                            f"The verified fact '{fact_name}' "
                            "was not referenced in the "
                            "recommendation."
                        ),
                        severity="warning",
                    )
                )
