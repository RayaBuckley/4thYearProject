# Conflux: Principal Context Is All You Need for Secure AI Agents

This is the repo for my master's project. It extends my prior work on ITES and SLED under one system: Conflux.

# ITES

ITES is a provenance-aware defence architecture for agentic LLM systems. It enforces authorisation based on the principals that actually influenced an action, rather than relying solely on the identity of the requesting user or the permissions of the executing agent.

The project has two major components:

- **ITES**, the defence architecture that mediates LLM execution.
- **SLED** (Security, Logic and Evaluation Dataset), an exhaustive evaluation framework for reasoning about the security and utility of agentic systems.

The long-term goal is to evaluate realistic agentic systems against prompt injection and influence attacks while maintaining as much legitimate utility as possible.

---

# Motivation

Modern LLM agents execute actions on behalf of users.

Current systems generally authorise actions using one of:

- the permissions of the executing service,
- the permissions of the requesting user,
- heuristic prompt filtering.

These approaches fail to account for **who actually influenced the decision**.

Prompt injection is fundamentally an influence attack.

ITES models influence explicitly and derives authority from information provenance.

---

# Core idea

Every piece of information has provenance.

When information influences an action:

```
information
        │
        ▼
provenance
        │
        ▼
current influencers
        │
        ▼
intersection rule
        │
        ▼
authorised action
```

The defence maintains the set of current influencers throughout recursive LLM execution.

A primitive action is authorised only when **every current influencer is authorised** to perform that action.

This preserves the security properties of the original prototype while allowing recursive execution.

---

# Architecture

The project is divided into several layers.

```
core
│
├── principals
├── permissions
├── resources
├── provenance
├── artifacts
├── actions
├── consent
├── chat_policy
└── session

↓

execution

↓

auth

↓

ITES

↓

SLED

↓

provider adapters

↓

benchmarks
```

---

# Core model

The core package defines immutable domain objects.

## Principals

Represent users, services, agents and other security principals.

Principals carry their authorised permissions.

---

## Resources

Protected objects that primitive actions operate on.

Examples include

- files
- databases
- cloud resources
- APIs

---

## Artifacts

Artifacts are provenance-bearing pieces of information.

Examples include

- user prompts
- retrieved documents
- tool outputs
- generated summaries

Artifacts are the fundamental information-flow objects of ITES.

---

## Provenance

Information provenance records

- which principals contributed information,
- source labels,
- provenance tags.

Decision provenance is deliberately **not** stored here.

---

## Actions

The defence reasons about actions rather than raw strings.

Current action taxonomy:

- PrimitiveAction
- NestedExecutionAction
- DelegationAction
- MessageUserAction
- ClarificationRequestAction
- RequestConsentAction
- StopAction
- NoOpAction

---

# ITES

ITES mediates every proposed action.

The mediator:

- tracks provenance-derived influence,
- propagates influence through recursive execution,
- enforces the exact intersection rule,
- applies visibility policy,
- applies consent policy,
- records an immutable execution trace.

The defence intentionally contains no planner/executor split.

Nested execution is modelled directly.

---

# Authorisation

ITES separates three independent concepts.

## Authorisation

Can the current influencers perform the action?

Uses the exact intersection rule:

> every current influencer must authorise the action.

---

## Visibility

Can this action be observed?

Conversation visibility is controlled independently of authorisation.

Visibility policies include:

- internal
- user-visible
- transcript-visible
- audited
- provider-visible

---

## Consent

Consent is intentionally narrower than authorisation.

Users may voluntarily expose only a subset of their permissions for automatic execution.

Consent:

- is attached to decision principals,
- never broadens authority,
- cannot be manufactured by involving unrelated users.

---

# Sessions

A Session represents an execution context.

It binds together:

- participants,
- conversation visibility,
- consent profiles.

Execution state is intentionally separate.

---

# SLED

SLED is the evaluation framework.

It models:

- environment data,
- authors,
- readers,
- recursive execution,
- benchmark environments.

The goal is exhaustive evaluation of security and utility.

---

# Planned evaluation

The intended evaluator explores every reachable execution branch.

```
Environment

↓

Representative Environment

↓

Exhaustive Search

↓

Security / Utility Metrics
```

Planned optimisations include:

- representative-environment reduction
- branch memoisation
- action canonicalisation
- branch pruning
- symbolic state compression

---

# Provider adapters

The core defence is provider-independent.

Real systems will be integrated using adapters.

Planned adapters include:

- Docker
- Virtual Machines
- Filesystems
- Databases
- AWS IAM
- Google Cloud IAM
- Microsoft Entra PIM

These adapters will materialise realistic organisational environments without changing the defence.

---

# Benchmarks

Planned benchmark integrations include:

- native exhaustive SLED evaluation
- AgentDojo
- additional external agent benchmarks
- comparisons across multiple frontier LLMs

---

# Current implementation status

Implemented:

- immutable core model
- provenance tracking
- action taxonomy
- consent model
- conversation visibility
- session model
- intersection-rule authorisation
- ITES mediation framework
- execution trace
- environment model

Partially implemented:

- exhaustive evaluator
- representative environments

Planned:

- benchmark runners
- provider adapters
- Docker / VM simulation
- cloud policy adapters
- benchmark reporting
- organisational simulation

---

# Repository structure

```
src/
    fourth_year_project/
        core/
        execution/
        auth/
        ites/
        sled/

tests/

scripts/        (planned)

benchmarks/     (planned)

providers/      (planned)
```

---

# Research direction

The project aims to answer:

> Can provenance-based authorisation provide practical protection against prompt injection while preserving legitimate utility?

Unlike traditional prompt-injection defences, ITES reasons about **authority**, **influence**, **visibility**, and **consent** simultaneously.

The long-term objective is to demonstrate these guarantees on realistic organisational environments and existing agent security benchmarks.
