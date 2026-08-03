# 04 — Agent Architecture

## Project

**Agentic Financial Platform — Mortgage Qualification and Decision Support**

---

## 1. Purpose

The Agentic Financial Platform decomposes preliminary mortgage analysis into specialized responsibilities instead of relying on one monolithic prompt.

Each logical agent has:

- One clearly defined job
- Explicit inputs and outputs
- Limited tool access
- Independent validation
- Observable execution
- A defined failure strategy

The platform uses centralized orchestration to coordinate these agents and deterministic financial tools.

> **AI reasons. Software calculates. Agents coordinate work.**

---

## 2. Current Implementation and Capstone Architecture

The current platform already implements the orchestration foundation through:

- `FinancialAgent`
- `CapabilityPlanner`
- `DependencyBuilder`
- `ExecutionEngine`
- `KnowledgeRetriever`
- `PromptBuilder`
- `ReasoningEngine`
- `ProviderFactory`

For the capstone, these capabilities are organized into logical agent boundaries.

The agents initially run within one Python service. They can later become independently deployed agents without changing their responsibilities or data contracts.

---

## 3. High-Level Multi-Agent Architecture

```text
                            User / API Client
                                   │
                                   ▼
                      Financial Coordinator Agent
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
   Financial Analysis       Knowledge Agent      Validation Agent
         Agent                    │                      │
            │                     │                      │
            ▼                     ▼                      │
 Deterministic Financial   Mortgage Guidelines          │
          Tools             and Evidence                 │
            │                     │                      │
            └─────────────────────┼──────────────────────┘
                                  ▼
                       Recommendation Agent
                                  │
                                  ▼
                    Structured Financial Assessment
```

---

## 4. Agent Decomposition

### 4.1 Financial Coordinator Agent

#### Responsibility

Own the end-to-end workflow for one mortgage-analysis request.

#### Inputs

- User goal
- Borrower financial inputs
- Property information
- Platform configuration

#### Outputs

- Structured final response
- Agent execution status
- Trace ID
- Supporting evidence
- Recommended next steps

#### Responsibilities

- Validate the incoming request
- Determine the required workflow
- Delegate work to specialized agents
- Preserve request context
- Combine agent outputs
- Return a consistent API response

#### Does Not

- Perform financial calculations
- Search mortgage documents directly
- Generate unsupported recommendations
- Make final loan-approval decisions

#### Current Implementation

```text
FinancialAgent
```

---

### 4.2 Financial Analysis Agent

#### Responsibility

Produce verified mortgage calculations using deterministic tools.

#### Inputs

```json
{
  "property_value": 600000,
  "down_payment": 60000,
  "monthly_income": 12000,
  "monthly_debt": 2500,
  "annual_interest_rate": 6.5,
  "loan_term_years": 30
}
```

#### Tools

- Debt-to-Income calculator
- Loan-to-Value calculator
- Loan-amount calculator
- Monthly-payment calculator

#### Outputs

```json
{
  "loan_amount": 540000,
  "dti": 20.83,
  "ltv": 90.0,
  "monthly_payment": 3413.0
}
```

#### Internal Workflow

```text
Capability Planner
        │
        ▼
Tool Selection
        │
        ▼
Dependency Builder
        │
        ▼
Execution Engine
        │
        ▼
Verified Financial Facts
```

#### Guardrails

- Uses deterministic code rather than LLM arithmetic
- Rejects missing or invalid required inputs
- Executes tools according to declared dependencies
- Records success or failure for every tool
- Does not create a recommendation

#### Current Implementation

```text
CapabilityPlanner
DependencyBuilder
ExecutionEngine
ToolRegistry
ExecutionContext
```

---

### 4.3 Knowledge Agent

#### Responsibility

Retrieve relevant mortgage guidance that can support the analysis.

#### Inputs

- User question
- Financial-analysis context
- Requested retrieval count

#### Data Sources

- Mortgage-guideline documents
- FAISS vector index
- Source metadata

#### Outputs

```json
{
  "items": [
    {
      "content": "Relevant mortgage-guideline excerpt",
      "source": "Mortgage Guidelines",
      "page": 1078
    }
  ]
}
```

#### Guardrails

- Validates that the vector store exists before retrieval
- Returns source metadata with retrieved evidence
- Does not invent missing guidance
- Does not perform financial calculations
- Returns an explicit empty or failed state when evidence is unavailable

#### Current Implementation

```text
KnowledgeRetriever
VectorStoreValidator
FAISS Retriever
RetrievedKnowledge
```

---

### 4.4 Recommendation Agent

#### Responsibility

Produce a clear and useful preliminary mortgage assessment from verified calculations and retrieved evidence.

#### Inputs

- Original user question
- Verified financial facts
- Retrieved mortgage guidance
- Reasoning instructions
- Output requirements

#### Outputs

- Preliminary assessment
- Key qualification observations
- Identified concerns
- Missing information
- Recommended next steps
- Required disclaimer

#### Workflow

```text
Verified Financial Facts
          +
Retrieved Mortgage Evidence
          +
User Objective
          │
          ▼
     Prompt Builder
          │
          ▼
    Reasoning Engine
          │
          ▼
Structured Recommendation
```

#### Guardrails

- May explain verified calculations but may not replace them
- Must distinguish facts from preliminary interpretations
- Must not approve or deny a mortgage
- Must not claim unsupported program eligibility
- Must acknowledge missing information
- Must include an educational and underwriting disclaimer

#### Current Implementation

```text
PromptBuilder
ReasoningEngine
LLMProvider
OpenAIProvider
MLXProvider
```

---

### 4.5 Validation Agent

#### Responsibility

Verify that the workflow output is complete, internally consistent, and safe to return.

#### Inputs

- Tool-execution results
- Retrieved evidence
- Preliminary recommendation
- Response schema

#### Checks

- Required calculations are present
- Tool failures are surfaced
- Recommendation does not contradict verified values
- Evidence is available for guideline-based claims
- Required response fields are populated
- Disclaimer is included
- Trace ID exists
- Unsupported final-approval language is absent

#### Outputs

```json
{
  "valid": true,
  "issues": [],
  "guardrail_status": "passed"
}
```

#### Capstone Status

The platform currently performs validation across request models, tool inputs, vector-store startup checks, typed response models, and structured execution results.

A dedicated validation-agent class is a capstone enhancement that consolidates these checks into one explicit stage.

---

## 5. Orchestration Pattern

The platform uses **centralized orchestration**.

```text
Financial Coordinator Agent
             │
             ├── Financial Analysis Agent
             │
             ├── Knowledge Agent
             │
             ├── Recommendation Agent
             │
             └── Validation Agent
```

### Why Centralized Orchestration?

Centralized orchestration was selected because mortgage decision support requires:

- Predictable execution order
- Strong auditability
- Clear ownership of request state
- Deterministic tool execution
- Easier failure recovery
- End-to-end traceability
- Reduced agent-to-agent ambiguity

A decentralized collaboration model would introduce unnecessary complexity for the current capstone scope.

---

## 6. End-to-End Workflow

```text
1. Client submits mortgage question and structured inputs
                           │
                           ▼
2. Financial Coordinator validates the request
                           │
                           ▼
3. Financial Analysis Agent selects and executes tools
                           │
                           ▼
4. Knowledge Agent retrieves supporting guidance
                           │
                           ▼
5. Recommendation Agent creates a preliminary assessment
                           │
                           ▼
6. Validation Agent checks completeness and consistency
                           │
                           ▼
7. Coordinator returns the typed API response
```

---

## 7. Shared Data Contracts

Agents communicate through structured objects rather than unrestricted conversational messages.

### Request Contract

```json
{
  "user_goal": "Can this borrower qualify for the proposed mortgage?",
  "inputs": {
    "property_value": 600000,
    "down_payment": 60000,
    "monthly_income": 12000,
    "monthly_debt": 2500,
    "annual_interest_rate": 6.5,
    "loan_term_years": 30
  }
}
```

### Financial Facts Contract

```json
{
  "loan_amount": 540000,
  "dti": 20.83,
  "ltv": 90.0,
  "monthly_payment": 3413.0
}
```

### Evidence Contract

```json
{
  "content": "Retrieved guideline excerpt",
  "source": "Mortgage Guidelines",
  "page": 1078
}
```

### Response Contract

```json
{
  "selected_tools": [],
  "execution_results": [],
  "verified_financial_information": {},
  "retrieved_item_count": 5,
  "preliminary_assessment": "",
  "trace_id": "",
  "trace_spans": [],
  "disclaimer": ""
}
```

Structured contracts reduce ambiguity and make agent behavior testable.

---

## 8. Tool Ownership

| Agent | Permitted Tools |
|---|---|
| Financial Coordinator Agent | Orchestration only |
| Financial Analysis Agent | DTI, LTV, loan amount, monthly payment |
| Knowledge Agent | FAISS retrieval and vector-store validation |
| Recommendation Agent | Prompt builder and configured LLM provider |
| Validation Agent | Schema, consistency, evidence, and policy checks |

No agent receives unrestricted access to every tool.

This follows the principle of least privilege.

---

## 9. Failure Handling

### Invalid User Input

```text
Request rejected
→ Structured validation error
→ No downstream agent execution
```

### Financial Tool Failure

```text
Execution stops or degrades safely
→ Failed tool identified
→ No unsupported recommendation generated
```

### Missing Vector Store

```text
Startup validation fails
→ Clear rebuild instructions returned
→ Low-level FAISS failure avoided
```

### Knowledge Retrieval Failure

```text
Evidence marked unavailable
→ Recommendation constrained
→ No guideline-backed claim without evidence
```

### LLM Provider Failure

```text
Verified calculations remain available
→ Reasoning failure is reported
→ No fabricated recommendation returned
```

### Validation Failure

```text
Response withheld or marked incomplete
→ Issues included in structured result
→ Trace retained for diagnosis
```

---

## 10. Observability

Every request receives a unique trace ID.

Major workflow stages produce trace spans:

- Planning
- Dependency-graph construction
- Tool execution
- Knowledge retrieval
- Prompt construction
- LLM reasoning
- Validation

The platform also records:

- Structured logs
- Execution duration
- Tool success and failure
- Retrieval count
- Provider information
- End-to-end request status

```text
Logs + Metrics + Traces = Operational Visibility
```

---

## 11. Modularity and Extensibility

The architecture supports extension without rewriting the coordinator.

### Add a New Financial Tool

1. Implement the deterministic tool.
2. Declare its required inputs.
3. Declare its produced outputs.
4. Register the tool and capability.
5. Allow the dependency graph to determine execution order.

### Add a New LLM Provider

1. Implement the `LLMProvider` contract.
2. Register it with the provider factory.
3. Select it through configuration.

### Add a New Financial Domain

Future logical agents may include:

- FHA Eligibility Agent
- VA Eligibility Agent
- Conventional Loan Agent
- Compliance Agent
- Fraud-Risk Agent
- Commercial Lending Agent
- Insurance Agent
- Wealth Advisory Agent

The current platform services remain reusable.

---

## 12. Architectural Trade-Offs

### Centralized Orchestration vs. Decentralized Agents

**Decision:** Centralized orchestration

**Benefit:** Predictable, testable, and traceable execution

**Trade-off:** The coordinator owns more workflow responsibility

---

### Deterministic Tools vs. LLM Calculations

**Decision:** Deterministic tools

**Benefit:** Reproducibility and financial accuracy

**Trade-off:** New calculations require explicit tool implementation

---

### In-Process Agents vs. Distributed Services

**Decision:** In-process logical agents for the capstone

**Benefit:** Simpler deployment and debugging

**Trade-off:** Independent scaling is deferred

---

### Provider Abstraction vs. Direct LLM Integration

**Decision:** Provider abstraction

**Benefit:** OpenAI and MLX can be exchanged without changing business logic

**Trade-off:** Introduces an additional interface and factory

---

## 13. Current State vs. Roadmap

### Implemented

- Financial coordinator
- Capability planning
- Dependency-graph construction
- Deterministic execution
- Knowledge retrieval
- Prompt construction
- Provider-independent reasoning
- Configuration
- Logging
- Metrics
- Request tracing
- FastAPI interface

### Capstone Enhancement

- Explicit Validation Agent
- Agent-level evaluation
- Grounding checks
- Before-and-after quality evidence

### Future Roadmap

- MCP-based tool and resource access
- Agent-to-Agent communication
- Human approval workflow
- Persistent memory
- Distributed agent deployment
- Advanced compliance and policy agents

---

## 14. Capstone Rubric Alignment

| Rubric Requirement | Architecture Coverage |
|---|---|
| Clear multi-agent decomposition | Five logical agents with distinct responsibilities |
| One job per agent | Explicit responsibility and non-responsibility boundaries |
| Workflow orchestration | Centralized coordinator with staged execution |
| End-to-end completeness | API input through calculations, evidence, reasoning, validation, and response |
| Modularity | Agent responsibilities mapped to independent platform modules |
| Extensibility | New tools, providers, agents, and financial domains can be added |
| Reliability | Structured errors, validation, deterministic tools, and safe degradation |
| Explainability | Verified facts, retrieved evidence, logs, metrics, and trace IDs |

---

## 15. Summary

The Agentic Financial Platform uses a centrally orchestrated multi-agent architecture to separate financial analysis, knowledge retrieval, recommendation generation, and validation.

The design avoids a monolithic AI prompt and instead combines:

- Specialized agent responsibilities
- Deterministic financial tools
- Structured data contracts
- Knowledge-backed reasoning
- Provider independence
- Explicit guardrails
- End-to-end observability

This creates a mortgage decision-support workflow that is modular, explainable, testable, and ready to evolve into a broader financial-services platform.
