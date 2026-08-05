# 06 — Guardrails and Reliability

## Purpose

The Agentic Financial Platform provides preliminary mortgage
decision support. It does not approve, deny, underwrite, or guarantee
a mortgage.

Guardrails are applied across the full workflow rather than relying
only on the final LLM prompt.

## Guardrail Architecture

```text
API Validation
      ↓
Financial Input Validation
      ↓
Deterministic Tool Execution
      ↓
Knowledge Retrieval Validation
      ↓
Prompt Constraints
      ↓
Recommendation Validation
      ↓
Typed Response Contract
      ↓
Audit Logs, Metrics, and Trace
