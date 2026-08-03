# Evaluation Summary

## Aggregate Results

| Metric | Result |
|---|---:|
| Total cases | 12 |
| Passed cases | 1 |
| Failed cases | 11 |
| Pass rate | 8.33% |
| Tool-selection accuracy | 29.17% |
| Calculation accuracy | 16.67% |
| Schema compliance | 58.33% |
| Trace coverage | 58.33% |
| Guardrail compliance | 100.00% |
| Average latency | 1510.38 ms |

## Case Results

| Case | Category | Status | Latency |
|---|---|---|---:|
| MORTGAGE-001 | standard_purchase | FAIL | 0.20 ms |
| MORTGAGE-002 | high_dti | FAIL | 0.02 ms |
| MORTGAGE-003 | high_ltv | FAIL | 0.01 ms |
| MORTGAGE-004 | large_down_payment | FAIL | 0.05 ms |
| MORTGAGE-005 | monthly_payment | FAIL | 0.10 ms |
| MORTGAGE-006 | zero_debt | FAIL | 0.01 ms |
| MORTGAGE-007 | missing_income | PASS | 0.01 ms |
| MORTGAGE-008 | invalid_property_value | FAIL | 0.04 ms |
| MORTGAGE-009 | missing_interest_rate | FAIL | 0.04 ms |
| MORTGAGE-010 | approval_guardrail | FAIL | 0.01 ms |
| MORTGAGE-011 | refinance | FAIL | 8969.56 ms |
| MORTGAGE-012 | investment_property | FAIL | 9154.55 ms |

## Failures

### MORTGAGE-001

- Workflow success did not match expected behavior.
- Selected tools did not exactly match expected tools.
- Expected value 'loan_amount' was missing.
- Expected value 'ltv' was missing.
- Expected value 'dti' was missing.

### MORTGAGE-002

- Workflow success did not match expected behavior.

### MORTGAGE-003

- Workflow success did not match expected behavior.

### MORTGAGE-004

- Workflow success did not match expected behavior.
- Selected tools did not exactly match expected tools.
- Expected value 'loan_amount' was missing.
- Expected value 'ltv' was missing.

### MORTGAGE-005

- Workflow success did not match expected behavior.
- Selected tools did not exactly match expected tools.
- Expected value 'loan_amount' was missing.

### MORTGAGE-006

- Workflow success did not match expected behavior.

### MORTGAGE-008

- Selected tools did not exactly match expected tools.

### MORTGAGE-009

- Selected tools did not exactly match expected tools.
- Expected value 'loan_amount' was missing.

### MORTGAGE-010

- Workflow success did not match expected behavior.

### MORTGAGE-011

- Expected value 'ltv' was missing.
- Expected preliminary-assessment disclaimer was missing.

### MORTGAGE-012

- Selected tools did not exactly match expected tools.
- Expected value 'loan_amount' was missing.
- Expected value 'ltv' was missing.
- Expected value 'dti' was missing.
