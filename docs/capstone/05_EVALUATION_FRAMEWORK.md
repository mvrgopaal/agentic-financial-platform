# 05 — Evaluation Framework

## Project

**Agentic Financial Platform — Mortgage Qualification and Decision Support**

---

## 1. Purpose

The evaluation framework measures whether the platform produces accurate,
grounded, useful, reliable, and explainable mortgage decision-support outputs.

Evaluation is not limited to the final LLM response.

The platform evaluates the complete workflow:

```text
User Request
    ↓
Capability Planning
    ↓
Financial Tool Execution
    ↓
Knowledge Retrieval
    ↓
Recommendation Generation
    ↓
Response Validation
    ↓
Business Outcome
```

The framework is designed to answer four questions:

1. Did the platform select the correct capabilities?
2. Did deterministic tools calculate the correct values?
3. Was the recommendation grounded in retrieved evidence?
4. Did evaluation results lead to measurable system improvement?

---

## 2. Evaluation Dimensions

The platform is evaluated across seven dimensions.

| Dimension | Primary Question |
|---|---|
| Tool Selection | Did the planner choose the correct financial capabilities? |
| Financial Accuracy | Were deterministic calculations correct? |
| Retrieval Quality | Did the system retrieve relevant mortgage guidance? |
| Groundedness | Is the recommendation supported by verified facts and evidence? |
| Output Quality | Is the response useful, clear, and actionable? |
| Reliability | Did the workflow complete without hidden failures? |
| Performance | Did the platform respond within an acceptable time? |

---

## 3. Evaluation Dataset

The capstone dataset should contain representative borrower and property
scenarios rather than a single demonstration case.

### Scenario Categories

- Standard conventional purchase
- High debt-to-income scenario
- High loan-to-value scenario
- Large down-payment scenario
- Missing required input
- Invalid negative input
- Investment-property scenario
- Refinance scenario
- Guideline retrieval scenario
- Unsupported eligibility question
- LLM provider failure scenario
- Missing vector-store scenario

Each evaluation case includes:

```json
{
  "case_id": "MORTGAGE-001",
  "category": "standard_purchase",
  "user_goal": "Can this borrower qualify for the proposed mortgage?",
  "inputs": {
    "property_value": 600000,
    "down_payment": 60000,
    "monthly_income": 12000,
    "monthly_debt": 2500,
    "annual_interest_rate": 6.5,
    "loan_term_years": 30
  },
  "expected_tools": [
    "calculate_dti",
    "calculate_loan_amount",
    "calculate_ltv",
    "calculate_monthly_payment"
  ],
  "expected_values": {
    "loan_amount": 540000,
    "ltv": 90.0
  },
  "expected_behavior": {
    "requires_evidence": true,
    "must_include_disclaimer": true,
    "must_not_approve_loan": true
  }
}
```

---

## 4. Metric Definitions

### 4.1 Tool-Selection Accuracy

Measures whether the capability planner selects the expected tools.

```text
Tool-Selection Accuracy =
Correctly Selected Expected Tools
÷
Total Expected Tools
```

### Target

```text
≥ 95%
```

### Failure Examples

- Required DTI tool not selected
- Monthly-payment tool selected when no rate or term is available
- Irrelevant tools selected

---

### 4.2 Financial-Calculation Accuracy

Deterministic calculations are evaluated independently from the LLM.

Evaluated tools:

- Debt-to-Income
- Loan-to-Value
- Loan Amount
- Monthly Payment

### Target

```text
100% accuracy on evaluation cases
```

### Tolerance

For floating-point or payment calculations:

```text
Absolute or relative tolerance must be explicitly defined.
```

Example:

```text
Monthly-payment tolerance: ± $1.00
Percentage tolerance: ± 0.01 percentage points
```

---

### 4.3 Retrieval Relevance

Measures whether retrieved evidence is relevant to the user request.

Each retrieved item is labeled:

- Relevant
- Partially relevant
- Not relevant

```text
Retrieval Precision =
Relevant Retrieved Items
÷
Total Retrieved Items
```

### Target

```text
≥ 90%
```

Additional checks:

- Source metadata is present
- Page metadata is present when available
- Duplicate chunks are minimized
- Requested `top_k` is respected

---

### 4.4 Groundedness

Measures whether recommendation claims are supported by:

- Verified financial calculations
- Retrieved mortgage guidance
- Explicit user inputs

A response is considered grounded when material factual claims can be traced
to one of those sources.

### Target

```text
≥ 90% grounded claims
```

### Unsupported Claim Target

```text
< 5%
```

Examples of unsupported claims:

- Claiming final qualification
- Inventing a credit score
- Claiming a loan program is available without evidence
- Introducing facts absent from user inputs or retrieved guidance

---

### 4.5 Output Schema Compliance

Measures whether the API response contains all required fields and valid types.

Required fields include:

- Selected tools
- Execution results
- Verified financial information
- Retrieved-item count
- Preliminary assessment
- Trace ID
- Trace spans
- Disclaimer

### Target

```text
100% schema compliance
```

Pydantic response models enforce this contract.

---

### 4.6 Guardrail Compliance

Each response is checked for prohibited behavior.

Required checks:

- No final approval or denial
- No unsupported eligibility claims
- No invented borrower data
- Missing information is acknowledged
- Disclaimer is included
- Tool failures are surfaced
- Evidence limitations are disclosed

### Target

```text
100% compliance on critical guardrails
```

---

### 4.7 Workflow Completion Rate

Measures successful end-to-end execution.

```text
Completion Rate =
Successfully Completed Workflows
÷
Total Valid Requests
```

### Target

```text
≥ 95%
```

Invalid requests are measured separately as validation outcomes.

---

### 4.8 Latency

Measures the duration of each execution stage.

Tracked spans:

- Planning
- Dependency-graph construction
- Tool execution
- Knowledge retrieval
- Prompt construction
- LLM reasoning
- Validation
- Total request duration

### Capstone Targets

| Metric | Target |
|---|---:|
| Deterministic tool execution | Under 500 ms |
| Knowledge retrieval | Under 2 seconds |
| End-to-end OpenAI response | Under 10 seconds |
| End-to-end local MLX response | Recorded as baseline |
| Trace creation | 100% of requests |

Latency targets are capstone goals, not production service-level guarantees.

---

## 5. Evaluation Methods

The framework uses a combination of deterministic and model-based evaluation.

### Deterministic Evaluation

Used for:

- Tool selection
- Numeric calculation accuracy
- Schema compliance
- Required-field presence
- Trace generation
- Guardrail phrases
- Error behavior
- API status codes

### Human Review

Used for:

- Recommendation usefulness
- Clarity
- Actionability
- Evidence relevance
- Explanation quality

### Model-Based Evaluation

May be used as a secondary signal for:

- Groundedness
- Relevance
- Completeness
- Contradiction detection

Model-based evaluation must not be the only source of truth.

---

## 6. Evaluation Scorecard

Each case produces one scorecard.

| Metric | Result | Pass Condition |
|---|---:|---|
| Tool selection | 4 of 4 | All expected tools selected |
| Calculation accuracy | 4 of 4 | All values within tolerance |
| Retrieval relevance | 4 of 5 | At least 90% aggregate target |
| Groundedness | 95% | At least 90% |
| Schema compliance | Pass | All required fields valid |
| Guardrail compliance | Pass | No critical violation |
| Workflow completion | Pass | Valid structured response |
| Total latency | 4.8 seconds | Under target |

---

## 7. Baseline and Improved System

The capstone must show evidence of iteration rather than only a final result.

### Baseline

The baseline system represents the earlier architecture:

- Direct LLM dependency
- Hardcoded provider selection
- Limited startup validation
- Minimal observability
- Less explicit response structure
- No request-level trace
- No dedicated evaluation dataset

### Improved System

The improved system includes:

- Provider-independent OpenAI and MLX integration
- Deterministic financial tools
- FAISS-backed knowledge retrieval
- Vector-store startup validation
- Typed request and response schemas
- Configuration-driven behavior
- Structured logging
- Metrics
- End-to-end tracing
- Guardrail checks
- Repeatable evaluation cases

---

## 8. Before-and-After Evidence

The following table should be populated with measured results after the
evaluation suite is executed.

| Metric | Baseline | Improved | Change |
|---|---:|---:|---:|
| Tool-selection accuracy | TBD | TBD | TBD |
| Calculation accuracy | TBD | TBD | TBD |
| Retrieval relevance | TBD | TBD | TBD |
| Groundedness | TBD | TBD | TBD |
| Schema compliance | TBD | TBD | TBD |
| Guardrail compliance | TBD | TBD | TBD |
| Workflow completion | TBD | TBD | TBD |
| Average latency | TBD | TBD | TBD |
| Trace coverage | 0% | TBD | TBD |

Do not replace `TBD` with assumed values.

Only measured results should be reported.

---

## 9. Evaluation-Driven Improvement Loop

```text
Build Evaluation Dataset
          ↓
Run Platform
          ↓
Collect Results
          ↓
Identify Failure Patterns
          ↓
Change Prompt, Tool, Retrieval, or Validation
          ↓
Run Regression Evaluation
          ↓
Compare Before and After
```

Examples:

### Tool-Selection Failure

```text
Signal:
Planner missed the monthly-payment capability.

Improvement:
Refine capability keywords or planning rules.

Validation:
Rerun all planning cases and confirm no regression.
```

### Retrieval Failure

```text
Signal:
Retrieved chunks are related to mortgage policy but not relevant
to the specific question.

Improvement:
Adjust chunking, metadata, query construction, or top_k.

Validation:
Measure retrieval precision before and after.
```

### Grounding Failure

```text
Signal:
Recommendation includes an unsupported program-eligibility claim.

Improvement:
Strengthen prompt constraints and validation checks.

Validation:
Run unsupported-claim cases and compare violation rate.
```

### Reliability Failure

```text
Signal:
Missing FAISS files cause a low-level runtime exception.

Improvement:
Add VectorStoreValidator with explicit rebuild instructions.

Evidence:
Low-level FAISS error is replaced by a clear, actionable failure.
```

This vector-store improvement is already implemented and represents one
documented iteration cycle.

---

## 10. Minimum Capstone Evaluation Set

The first executable evaluation suite should contain at least 12 cases.

| Case | Purpose |
|---|---|
| MORTGAGE-001 | Standard purchase |
| MORTGAGE-002 | High DTI |
| MORTGAGE-003 | High LTV |
| MORTGAGE-004 | Large down payment |
| MORTGAGE-005 | Missing monthly income |
| MORTGAGE-006 | Negative property value |
| MORTGAGE-007 | Missing interest rate |
| MORTGAGE-008 | Guideline-specific question |
| MORTGAGE-009 | Unsupported final-approval request |
| MORTGAGE-010 | Missing vector store |
| MORTGAGE-011 | OpenAI provider run |
| MORTGAGE-012 | MLX provider run |

---

## 11. Evaluation Artifacts

The capstone repository should contain:

```text
evaluation/
├── cases/
│   └── mortgage_cases.json
├── expected/
│   └── expected_results.json
├── results/
│   ├── baseline_results.json
│   └── improved_results.json
└── reports/
    └── evaluation_summary.md
```

Suggested executable components:

```text
src/app/evaluation/
├── evaluation_case.py
├── evaluation_result.py
├── financial_evaluator.py
└── run_evaluation.py
```

For capstone scope, the implementation should remain small and focused.

---

## 12. Decision Thresholds

A release candidate passes capstone evaluation when:

- Financial calculation accuracy is 100%.
- Tool-selection accuracy is at least 95%.
- Retrieval relevance is at least 90%.
- Groundedness is at least 90%.
- Critical guardrail compliance is 100%.
- Schema compliance is 100%.
- Valid-request workflow completion is at least 95%.
- Every completed request produces a trace ID.

Any critical financial-calculation or guardrail failure blocks release.

---

## 13. Reporting

The final evaluation report must include:

- Dataset size and scenario coverage
- Metric definitions
- Test environment
- Provider used
- Measured results
- Failure examples
- Changes made
- Before-and-after comparison
- Known limitations

This prevents selective reporting and makes the results reproducible.

---

## 14. Known Limitations

The capstone evaluation does not establish:

- Regulatory certification
- Production lending compliance
- Fair-lending compliance
- Credit-decision validity
- Performance at enterprise scale
- Accuracy across every mortgage product
- Production-grade service-level guarantees

The system provides preliminary educational decision support only.

---

## 15. Capstone Rubric Alignment

| Rubric Requirement | Evaluation Coverage |
|---|---|
| Clear evaluation strategy | Dataset, metrics, methods, and thresholds defined |
| Use of evaluation signals | Failures map to prompt, retrieval, tool, and validation changes |
| Evidence of improvement | Baseline and improved results table plus documented iteration |
| Output reliability | Schema, guardrail, calculation, and completion metrics |
| Grounding | Retrieval precision and grounded-claim measurement |
| Technical reliability | Failure cases, latency, traces, and provider tests |

---

## 16. Summary

The Agentic Financial Platform is evaluated as a complete decision-support
workflow, not merely as an LLM response.

The framework separates:

- Deterministic financial accuracy
- Agent-planning quality
- Retrieval quality
- Grounded reasoning
- Guardrail compliance
- Operational reliability
- Business usefulness

The most important capstone evidence will be a repeatable evaluation dataset
and measured before-and-after results demonstrating that evaluation signals
produced meaningful platform improvements.
