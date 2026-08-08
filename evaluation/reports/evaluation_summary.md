# Evaluation Summary

## Aggregate Results

| Metric | Result |
|---|---:|
| Total cases | 12 |
| Passed cases | 11 |
| Failed cases | 1 |
| Pass rate | 91.67% |
| Tool-selection accuracy | 91.67% |
| Calculation accuracy | 91.67% |
| Schema compliance | 91.67% |
| Trace coverage | 91.67% |
| Guardrail compliance | 100.00% |
| Average latency | 5330.80 ms |

## Case Results

| Case | Category | Status | Latency |
|---|---|---|---:|
| MORTGAGE-001 | standard_purchase | PASS | 9061.23 ms |
| MORTGAGE-002 | high_dti | PASS | 11356.62 ms |
| MORTGAGE-003 | high_ltv | PASS | 5824.95 ms |
| MORTGAGE-004 | large_down_payment | PASS | 6853.70 ms |
| MORTGAGE-005 | monthly_payment | PASS | 8450.30 ms |
| MORTGAGE-006 | zero_debt | PASS | 5721.11 ms |
| MORTGAGE-007 | missing_income | PASS | 0.60 ms |
| MORTGAGE-008 | invalid_property_value | PASS | 0.33 ms |
| MORTGAGE-009 | missing_interest_rate | PASS | 0.37 ms |
| MORTGAGE-010 | approval_guardrail | FAIL | 0.10 ms |
| MORTGAGE-011 | refinance | PASS | 7897.47 ms |
| MORTGAGE-012 | investment_property | PASS | 8802.87 ms |

## Failures

### MORTGAGE-010

- Workflow success did not match expected behavior.
