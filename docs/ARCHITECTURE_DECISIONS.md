# Architecture Decision Records (ADR)

> *"Good architecture is a collection of intentional decisions. Great architecture remembers why those decisions were made."*

---

# Purpose

This document captures the significant architectural decisions made while building the **Agentic Financial Platform**.

It is intended to answer questions that future contributors, reviewers, or even the original author may ask months or years later.

Each decision records:

- The problem
- The available options
- The chosen solution
- The reasoning behind the decision
- The long-term consequences

---

# ADR-001

## Metadata-Driven Tool Discovery

### Status

✅ Accepted

### Problem

Business capabilities such as Debt-to-Income (DTI), Loan-to-Value (LTV), Loan Amount, and Monthly Payment should be discoverable without hardcoding execution logic.

A tightly coupled implementation would require changing planner logic every time a new financial tool is introduced.

### Decision

Represent every business tool using metadata.

Each tool declares:

- Name
- Version
- Description
- Required Inputs
- Produced Outputs
- Supported Capabilities

### Rationale

Metadata allows the planner to discover tools dynamically rather than relying on explicit conditional logic.

Adding a new business capability becomes a matter of registering another tool.

### Consequences

Benefits

- Extensible
- Loosely coupled
- Easier testing
- Simplified planner

Trade-offs

- Slightly more metadata maintenance

---

# ADR-002

## Automatic Dependency Graph Generation

### Status

✅ Accepted

### Problem

Financial calculations depend on one another.

Example

Loan Amount

↓

Loan-to-Value

↓

Monthly Payment

Hardcoding execution order would become increasingly difficult as additional tools are introduced.

### Decision

Generate a dependency graph automatically using declared tool inputs and outputs.

### Rationale

Execution order should emerge from metadata instead of being manually maintained.

### Consequences

Benefits

- Automatic execution ordering
- Parallel execution planning
- Cycle detection
- Scalable architecture

Trade-offs

- Slightly more complex graph generation

---

# ADR-003

## Shared Execution Context

### Status

✅ Accepted

### Problem

Each tool produces outputs that become inputs to subsequent tools.

Passing large parameter lists between tools creates tight coupling.

### Decision

Introduce a shared execution context responsible for storing verified financial facts.

### Rationale

The execution context becomes the single source of truth during request processing.

### Consequences

Benefits

- Simplified interfaces
- Reduced parameter passing
- Easier debugging
- Shared state visibility

Trade-offs

- Requires disciplined ownership of context updates

---

# ADR-004

## Separate Deterministic Execution from AI Reasoning

### Status

✅ Accepted

### Problem

Large Language Models should not perform financial calculations.

Financial values must always remain reproducible.

### Decision

Use software to calculate.

Use AI to explain.

### Architecture

```
Financial Tools

↓

Verified Facts

↓

Reasoning Engine

↓

LLM
```

### Consequences

Benefits

- Reproducible results
- Lower hallucination risk
- Explainable reasoning
- Regulatory friendliness

Trade-offs

- Slightly more architectural complexity

---

# ADR-005

## Retrieval-Augmented Generation (RAG)

### Status

✅ Accepted

### Problem

Mortgage guidance changes over time.

Embedding policies inside prompts would become difficult to maintain.

### Decision

Retrieve supporting mortgage guidelines from a vector database before reasoning.

### Rationale

Separate knowledge from reasoning.

### Consequences

Benefits

- Updated knowledge without changing prompts
- Better grounding
- Lower hallucination rate

Trade-offs

- Additional retrieval latency

---

# ADR-006

## Provider-Independent LLM Architecture

### Status

✅ Accepted

### Problem

Directly depending on OpenAI creates vendor lock-in.

### Decision

Introduce an LLM Provider abstraction.

```
Reasoning Engine

↓

LLM Provider

↓

OpenAI

MLX

Azure OpenAI

Claude

Gemini
```

### Rationale

Business logic should remain independent from infrastructure.

### Consequences

Benefits

- Provider independence
- Easier testing
- Future extensibility

Trade-offs

- Additional abstraction layer

---

# ADR-007

## Structured Prompt Builder

### Status

✅ Accepted

### Problem

Constructing prompts inside the reasoning engine mixes prompt engineering with orchestration.

### Decision

Introduce a dedicated Prompt Builder.

### Rationale

Prompt construction is a separate responsibility.

### Consequences

Benefits

- Cleaner reasoning engine
- Easier experimentation
- Prompt reuse

---

# ADR-008

## Configuration as a First-Class Concern

### Status

🚧 In Progress

### Problem

Hardcoded providers, models, temperatures, and retrieval settings reduce flexibility.

### Decision

Introduce:

- ApplicationConfig
- ConfigurationLoader
- ConfigurationManager

### Architecture

```
application.yaml

↓

ConfigurationLoader

↓

ApplicationConfig

↓

Platform Components
```

### Expected Benefits

- Environment-specific configuration
- Provider selection
- Easier deployments
- Cleaner startup

---

# ADR-009

## Provider Factory

### Status

🚧 Planned

### Problem

FinancialAgent currently creates providers directly.

### Decision

Centralize provider creation inside a Provider Factory.

```
Configuration

↓

Provider Factory

↓

Provider

↓

Financial Agent
```

### Expected Benefits

- Reduced coupling
- Cleaner startup
- Easier provider registration

---

# ADR-010

## Observability by Design

### Status

🚧 Planned

### Problem

Enterprise systems require complete visibility into request execution.

### Decision

Every request should expose:

- Request ID
- Correlation ID
- Timing
- Tool execution
- Retrieval metrics
- LLM latency
- Token usage
- Cost

### Expected Benefits

- Faster debugging
- Production readiness
- Performance tuning

---

# ADR-011

## Platform Before Features

### Status

✅ Accepted

### Problem

Adding mortgage-specific functionality too early would reduce reuse.

### Decision

Build reusable infrastructure before domain expansion.

```
Platform

↓

Mortgage

Insurance

Wealth

Compliance

Fraud
```

### Rationale

The platform should outlive individual applications.

---

# ADR-012

## Simplicity Over Cleverness

### Status

✅ Accepted

### Decision

Every abstraction must justify its existence.

Before introducing a new class, ask:

- Does this reduce coupling?

- Does this improve readability?

- Does this make testing easier?

- Does this simplify future change?

If the answer is "No", the abstraction should not be introduced.

---

# Future ADRs

The following architectural decisions will be documented as the platform evolves.

- Configuration Manager
- Logging Framework
- Metrics
- Request Tracing
- REST APIs
- Security Model
- MCP Integration
- A2A Communication
- Multi-Agent Orchestration
- Human Approval Workflow
- Cloud Deployment
- Kubernetes
- Event Streaming
- Distributed Execution

---

# Closing Thoughts

Architecture is a sequence of deliberate decisions.

Code changes frequently.

Frameworks evolve.

Models improve.

The reasoning behind architectural decisions should remain understandable.

This document exists to preserve that reasoning.

---

**Agentic Financial Platform**

*"Build systems that future engineers will thank you for."*
