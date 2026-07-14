# Fourth Year Project Architecture

> Canonical architectural description of the project.
>
> This document is the single source of truth for the system architecture,
> terminology, design principles and long-term roadmap.
>
> All implementation decisions should be consistent with this document unless
> an explicit architectural change is agreed.

---

# 1. Vision

The project aims to develop a **general defence architecture** for secure
agentic AI systems rather than a defence tied to a particular model,
framework, vendor or deployment platform.

The central research question is:

> How can an agent execute useful tasks while remaining robust against prompt
> injection and other influence attacks originating from untrusted data?

The project therefore focuses on modelling **information flow**, **authority**,
and **execution semantics**, rather than relying solely on prompt engineering
or model behaviour.

---

# 2. Core Contributions

The project consists of two primary research contributions.

## ITES

ITES is the defence architecture.

It mediates every execution step performed by an agent and determines whether
actions may execute based upon information provenance and authorisation.

ITES is intended to be:

- model independent
- framework independent
- deployment independent
- extensible

---

## SLED

SLED is the evaluation framework.

It provides a simulated execution environment for measuring whether a defence
behaves correctly.

SLED should support:

- synthetic benchmarks
- external benchmarks
- real deployment targets
- comparative evaluation

---

# 3. Design Principles

The architecture is designed around several principles.

## Explicit execution

Every action is explicitly represented.

Implicit model behaviour should be minimised wherever practical.

---

## Information provenance

Every piece of information has an associated provenance.

Provenance is treated as first-class data throughout execution.

---

## Dynamic authorisation

Authorisation decisions are evaluated at execution time.

Permissions are derived from the information actually influencing an action,
rather than solely from the identity of the executing agent.

---

## Defence in depth

Security should not rely on any single mechanism.

Multiple independent layers should contribute to overall security.

---

## Extensibility

New policy engines, runtimes, benchmarks and deployment targets should be
added without requiring widespread architectural changes.

---

# 4. High-Level Architecture

```text
                   User
                     │
                     ▼
            Agent Runtime
                     │
                     ▼
           Execution Planner
                     │
                     ▼
────────────────────────────────────
              ITES Core
────────────────────────────────────
    Provenance
    Authorisation
    Policy Evaluation
    Execution Control
────────────────────────────────────
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
     Tools      External APIs   LLMs
         │
         ▼
    Environment
```

The defence sits between planning and execution.

Every execution request passes through ITES.

---

# 5. Layered Architecture

The repository is organised into logical layers.

## Domain Layer

Defines:

- execution model
- resources
- principals
- actions
- provenance
- policies

Contains no deployment-specific logic.

---

## Core Layer

Implements:

- execution engine
- authorisation
- provenance tracking
- policy evaluation

Contains the primary research contribution.

---

## Adapter Layer

Integrates:

- policy engines
- benchmark suites
- runtimes
- deployment targets

Everything in this layer should be replaceable.

---

## Infrastructure Layer

Provides:

- logging
- telemetry
- configuration
- persistence
- sandbox execution

---

## Presentation Layer

Provides:

- reports
- visualisations
- command-line tools
- demonstrations

---

# 6. Repository Structure

Expected long-term package structure:

```text
src/fourth_year_project/

core/
environment/
policy/
runtime/
benchmarks/
extensions/
privacy/
observability/
gateway/
targets/
control/
reporting/
evaluation/
scripts/
```

Packages should remain loosely coupled.

---

# 7. Core Domain Model

The execution model revolves around several core concepts.

## Principal

An entity capable of owning resources or performing actions.

Examples:

- users
- assistants
- services
- delegated identities

---

## Resource

A piece of information or capability.

Examples:

- documents
- emails
- APIs
- databases
- files
- tool outputs

Resources carry provenance and authorisation metadata.

---

## Action

A request to perform work.

Examples:

- send email
- search
- read document
- invoke tool
- call LLM

Every action is evaluated before execution.

---

## Provenance

Represents how information was produced and propagated.

Provenance should be preserved across execution wherever practical.

---

## Policy

Defines whether an action should be permitted.

Policies consume:

- principals
- resources
- provenance
- contextual information

Policies return structured decisions rather than simple booleans.

---

# 8. Extension Interfaces

Subsystems should communicate through stable interfaces.

Expected interfaces include:

- PolicyEngine
- AttackGenerator
- EvaluationRunner
- SandboxRuntime
- TargetRuntime
- ScenarioAdapter
- PrivacyFilter
- TelemetrySink

Concrete implementations must not depend directly on one another.

---

# 9. Planned Backends

## Policy

- Cedar
- Open Policy Agent

---

## Runtime

- Local execution
- gVisor
- Firecracker

---

## Telemetry

- OpenTelemetry
- Structured logging

---

## Privacy

- Presidio

---

## Deployment

- Open WebUI
- MCP
- OpenAPI

Future deployments should require only adapters.

---

# 10. Evaluation Architecture

Evaluation should occur at several levels.

## Unit tests

Validate individual components.

---

## Integration tests

Validate subsystem interactions.

---

## Synthetic evaluation

Performed using SLED.

---

## External benchmarks

Examples:

- AgentDojo
- Promptfoo
- HarmBench
- garak
- Future benchmark suites

---

## Real deployment

Evaluate the defence in realistic agent platforms.

Examples include:

- Open WebUI
- MCP-based systems

---

# 11. Observability

Execution should be observable.

Record:

- execution traces
- policy decisions
- provenance evolution
- runtime events
- benchmark metrics

Observability should remain independent from the core execution engine.

---

# 12. Security Model

The project assumes:

- arbitrary prompt injection
- indirect prompt injection
- malicious retrieved documents
- malicious tool outputs
- compromised external services
- partially trusted users
- delegated execution

Security decisions should depend upon information flow rather than assumptions
about trusted prompts.

---

# 13. Future Research

Potential extensions include:

- richer provenance models
- quantitative influence analysis
- additional policy languages
- enterprise IAM modelling
- cloud authorisation systems
- distributed agents
- multi-agent coordination
- human approval workflows
- formal verification
- adaptive policies

The architecture should accommodate these without major redesign.

---

# 14. Development Strategy

Implementation proceeds in the following order:

1. Architecture
2. Technical specifications
3. Interfaces
4. Domain models
5. Implementations
6. Tests
7. Integration
8. Evaluation
9. Optimisation

Integration should generally occur after major subsystems have been created.

---

# 15. Non-Goals

The project is **not** intended to:

- optimise a specific LLM
- depend upon proprietary APIs
- rely on prompt engineering alone
- implement vendor-specific security mechanisms
- tightly couple to one orchestration framework

---

# 16. Architectural Decision Records

Significant architectural changes should be documented.

Each decision should record:

- motivation
- alternatives considered
- trade-offs
- expected impact

Maintaining a history of decisions reduces architectural drift over time.

---

# 17. Success Criteria

The project is successful if it demonstrates:

- a novel execution model
- strong modular architecture
- realistic evaluation
- reproducible experiments
- extensibility to new platforms
- applicability beyond a single benchmark
- research-quality implementation

Every major change should move the project closer to one or more of these goals.
