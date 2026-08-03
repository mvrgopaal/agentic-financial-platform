# Capstone Problem Definition

## Project

**Agentic Financial Platform — Mortgage Qualification and Decision Support**

## Problem Statement

Mortgage loan officers must combine borrower financial information,
multiple deterministic calculations, product guidelines, and policy
documents before providing an initial qualification assessment.

Today, this work is often distributed across calculators, document
repositories, lender portals, and manual guideline searches. This
creates several problems:

- Slow preliminary qualification decisions
- Repetitive manual calculations
- Inconsistent interpretation of guidelines
- Limited traceability into how a recommendation was produced
- Risk of relying on unsupported or hallucinated AI responses
- Difficulty comparing calculation results with supporting policies

The Agentic Financial Platform addresses this problem by coordinating
specialized agents and deterministic tools to calculate borrower
metrics, retrieve supporting mortgage guidance, validate results, and
produce a structured, explainable preliminary recommendation.

## Primary User

### Mortgage Loan Officer

The primary user is a licensed mortgage loan officer who needs to
quickly evaluate a borrower scenario before recommending appropriate
next steps.

### User Needs

The loan officer needs to:

- Enter borrower and property information once
- Receive verified DTI, LTV, loan amount, and payment calculations
- Retrieve relevant mortgage guidelines
- Understand why the platform produced its recommendation
- Identify missing information and potential qualification concerns
- Receive a consistent, structured response
- Reduce the time required for preliminary analysis

## Secondary Stakeholders

- Mortgage underwriters
- Loan processors
- Branch managers
- Compliance and risk teams
- Platform administrators
- Financial-services engineering teams

## Proposed Solution

The platform accepts a borrower question and structured financial data,
then coordinates the following workflow:

1. Interpret the user’s objective.
2. Select the required financial capabilities.
3. Build the tool dependency graph.
4. Execute deterministic calculations.
5. Retrieve relevant mortgage guidance.
6. Validate and organize the evidence.
7. Produce an explainable preliminary assessment.
8. Return calculations, supporting evidence, execution trace, and
   recommended next steps through a REST API.

The system supports OpenAI and a locally hosted MLX model through a
provider-independent reasoning interface.

## Value Proposition

The platform does not replace underwriting or make final credit
decisions. It improves the quality and speed of preliminary mortgage
analysis by combining deterministic computation, grounded knowledge,
agent orchestration, and traceable AI reasoning.

## Success Criteria

| Outcome | Baseline | Capstone Target |
|---|---:|---:|
| Preliminary analysis time | 15–30 minutes | Under 3 minutes |
| Financial-calculation accuracy | Manual and variable | 100% on test cases |
| Correct tool selection | Not automated | At least 95% |
| Grounded responses | Inconsistent | At least 90% groundedness |
| Required response fields | Informal output | 100% schema compliance |
| Unsupported factual claims | Possible | Under 5% |
| API workflow completion | Manual process | At least 95% successful runs |
| Traceability | Limited | Trace ID and stage results for every request |
| Provider portability | Single-provider risk | OpenAI and MLX supported |

## Non-Goals

The capstone will not:

- Approve or deny mortgage applications
- Replace a licensed mortgage professional
- Replace an Automated Underwriting System
- Access consumer credit reports
- Process production PII
- Execute financial transactions
- Implement Kubernetes, Kafka, or multi-tenant SaaS deployment
- Claim production regulatory certification

## Capstone Scope

### Included

- Multi-agent mortgage-analysis workflow
- Deterministic financial tools
- Knowledge-backed guideline retrieval
- Provider-independent LLM reasoning
- Structured request and response schemas
- Logging, metrics, and request tracing
- FastAPI interface
- Guardrails and validation
- Evaluation dataset and measurable results
- End-to-end demonstration

### Roadmap Only

- MCP integration
- Agent-to-Agent protocol
- Human approval workflow
- Persistent agent memory
- Kubernetes deployment
- Kafka event streaming
- Redis caching
- Multi-tenant financial applications
