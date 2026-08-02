"This project is an educational exploration of enterprise agentic AI architecture for financial services. The emphasis is on clean architectural boundaries, deterministic computation, provider independence, and explainable AI—not on a single LLM or framework."

# Agentic Financial Platform

> **A Provider-Independent Agentic AI Platform for Financial Services**

---

## Vision

Most AI applications tightly couple business logic with a single Large Language Model (LLM), making them difficult to maintain, extend, and deploy in regulated enterprise environments.

The **Agentic Financial Platform** takes a different approach.

It separates:

- Business Planning
- Deterministic Execution
- Financial Knowledge
- AI Reasoning
- LLM Providers

into independent architectural layers.

The result is an extensible platform where financial intelligence is built from verified calculations, enterprise knowledge, and AI reasoning rather than prompt engineering alone.

---

# Design Philosophy

The platform follows one simple architectural principle:

> **AI should reason. Software should calculate.**

Financial calculations must always remain deterministic.

Large Language Models should explain verified results—not invent them.

---

# Architecture

```
                          User Request
                               │
                               ▼
                     Financial Agent
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
 Capability Planner      Dependency Builder     Prompt Builder
        │                      │                      │
        ▼                      ▼                      ▼
  Tool Selection       Execution Graph        Structured Prompt
                               │
                               ▼
                     Execution Engine
                               │
                               ▼
                    Execution Context
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
Financial Tools         Knowledge Retriever      Future Agents
       │                       │
       ▼                       ▼
Verified Facts          Mortgage Guidelines (RAG)
       └───────────────────────┬────────────────────────┘
                               ▼
                      Reasoning Engine
                               │
                               ▼
                         LLM Provider
                  ┌────────────┴────────────┐
                  ▼                         ▼
           OpenAI Provider          Local MLX Provider
```

---

# Architectural Layers

## 1. Capability Planning

The planner analyzes the user's financial objective and determines which business capabilities are required.

Example:

```
User:
Can I qualify for this mortgage?
```

Planner:

```
Required Capabilities

✓ Debt-to-Income

✓ Loan Amount

✓ Loan-to-Value

✓ Monthly Payment
```

No calculations occur during planning.

---

## 2. Tool Discovery

Business tools are registered through metadata rather than hardcoded logic.

Example metadata:

- Tool Name
- Version
- Description
- Inputs
- Outputs
- Required Capabilities

The planner remains completely independent from tool implementations.

---

## 3. Dependency Builder

The platform automatically constructs a dependency graph from tool metadata.

Example:

```
Loan Amount
     │
     ├─────────────► Loan-to-Value
     │
     └─────────────► Monthly Payment

Debt-to-Income
```

This enables:

- Automatic execution ordering
- Parallel execution planning
- Future workflow optimization

---

## 4. Execution Engine

The execution engine performs deterministic financial calculations.

Responsibilities:

- Execute tools
- Share outputs
- Capture failures
- Preserve execution order
- Update execution context

The execution engine never calls an LLM.

---

## 5. Execution Context

A shared runtime state stores verified financial facts.

Example:

```
Monthly Income

Monthly Debt

Loan Amount

Loan-to-Value

Debt-to-Income

Monthly Payment
```

Every component receives the same verified information.

---

## 6. Knowledge Retrieval (RAG)

The platform retrieves relevant mortgage guidance from a vector database.

Current implementation:

- PDF Loader
- Text Splitter
- OpenAI Embeddings
- FAISS Vector Store
- Semantic Retrieval

The reasoning engine never answers questions without supporting knowledge.

---

## 7. Prompt Builder

Instead of manually writing prompts, the platform constructs structured prompts from:

- User Question
- Verified Financial Facts
- Retrieved Mortgage Guidelines
- Reasoning Instructions
- Output Instructions

Prompt construction is completely independent from the selected LLM.

---

## 8. Reasoning Engine

The reasoning engine combines:

- Verified Calculations
- Mortgage Guidance
- User Intent

to generate a grounded financial explanation.

The reasoning engine contains no provider-specific code.

---

## 9. Provider-Independent LLM Layer

The platform follows the Dependency Inversion Principle.

```
Reasoning Engine

↓

LLM Provider

↓

OpenAI

MLX

Future Providers
```

Current implementations:

- OpenAI
- Local MLX

Future providers:

- Azure OpenAI
- Anthropic Claude
- Google Gemini
- AWS Bedrock
- On-Prem Enterprise Models

Business logic remains unchanged.

---

# Project Structure

```
src/

    agents/
        capability_planner.py
        dependency_builder.py
        financial_agent.py
        prompt_builder.py

    execution/
        execution_engine.py
        execution_context.py

    rag/
        loader.py
        retriever.py
        vectorstore.py
        knowledge_retriever.py

    reasoning/
        reasoning_engine.py

    providers/
        llm/
            provider.py
            openai_provider.py
            mlx_provider.py

    tools/
        tool_registry.py
        tool_definition.py
```

---

# Current Features

✓ Capability Planning

✓ Metadata-Driven Tool Discovery

✓ Dependency Graph Generation

✓ Parallel Execution Planning

✓ Deterministic Financial Calculations

✓ Shared Execution Context

✓ Retrieval-Augmented Generation (RAG)

✓ Structured Prompt Construction

✓ Provider-Independent Reasoning Engine

✓ OpenAI Integration

✓ Local MLX Integration

---

# Why This Architecture?

Traditional AI Applications:

```
User

↓

Prompt

↓

LLM

↓

Answer
```

Agentic Financial Platform:

```
User

↓

Planning

↓

Execution

↓

Knowledge

↓

Reasoning

↓

Provider

↓

LLM
```

The platform separates deterministic software engineering from probabilistic AI reasoning.

---

# Future Roadmap

## Phase 2

- Configuration-driven Provider Selection
- Structured Logging
- Metrics
- Tracing
- Error Recovery

---

## Phase 3

- FastAPI REST APIs
- Streamlit UI
- Authentication
- Session Management

---

## Phase 4

- Multi-Agent Collaboration
- Agent-to-Agent Communication (A2A)
- Model Context Protocol (MCP)
- Human-in-the-Loop Approval
- Workflow Orchestration

---

# Engineering Principles

The platform is intentionally designed around enterprise software engineering principles.

- Separation of Concerns
- Dependency Inversion
- Single Responsibility
- Provider Independence
- Deterministic Financial Calculations
- Explainable AI
- Extensibility
- Testability

---

# Disclaimer

This platform provides **preliminary financial assessments**.

It does **not** replace:

- Licensed Mortgage Professionals
- Automated Underwriting Systems
- Credit Decisions
- Regulatory Compliance Reviews

Final lending decisions require complete underwriting and verification.

---

# Author

**Gopal Muriki**

Software Engineer | Agentic AI Engineer | AI Architecture Enthusiast

Building enterprise-grade Agentic AI Platforms for Financial Services.
