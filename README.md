4thYearProject

A reference implementation for a provenance-aware defence architecture for LLM-based systems and a framework for evaluating such defences.

This repository accompanies a fourth-year Computer Science dissertation investigating how provenance-aware execution can provide security guarantees against prompt injection and related influence attacks in agentic AI systems.

⸻

Overview

Large Language Model (LLM) systems increasingly perform actions on behalf of users by interacting with tools, APIs and external services. Existing systems typically execute actions using the authority of the application itself, making them vulnerable to prompt injection, indirect prompt injection and other influence attacks.

This project investigates an alternative execution model in which authority is derived from the provenance of information rather than the runtime context in which an action is executed.

The project consists of two major components:

* ITES — a provenance-aware defence architecture for LLM systems.
* SLED — an evaluation framework for measuring the effectiveness of AI defences.

Together they provide both a novel defence and a reproducible method for evaluating that defence.

⸻

Research Contributions

The project is centred around four research contributions.

1. ITES

Information-Tracked Execution System (ITES) is the primary contribution of this work.

ITES mediates every interaction between an LLM and the outside world by:

* tracking provenance throughout execution,
* propagating influence through derived information,
* authorising actions using provenance-derived authority,
* preventing unauthorised actions caused by prompt injection or other influence attacks.

Rather than attempting to classify inputs as “trusted” or “untrusted”, ITES treats every source of information uniformly and derives authority from provenance.

⸻

2. SLED

Security evaluation for LLM Execution Defences (SLED) is an evaluation framework for AI security defences.

SLED provides:

* benchmark environments,
* attack models,
* evaluation scenarios,
* metrics,
* reporting.

Unlike existing benchmark suites, SLED is designed around system-level abstract attacks rather than attacks targeting specific model behaviours.

This allows defences to be evaluated independently of any particular LLM implementation.

⸻

3. Enterprise Policy Models

The project models realistic organisational access control rather than relying on simplified permission systems.

Planned policy models include:

* AWS IAM
* Google Cloud IAM
* Microsoft Entra / Privileged Identity Management (PIM)

These integrations are intended to demonstrate that ITES can operate within realistic enterprise security environments.

⸻

4. Benchmark Integrations

SLED includes its own benchmark methodology while also supporting external benchmark suites.

External benchmarks are used for comparison only.

Planned integrations include:

* AgentDojo
* Future public AI security benchmarks

The AgentDojo integration executes ITES against the AgentDojo benchmark and reports the resulting performance and security metrics.

SLED’s native benchmark suite is independent of AgentDojo and is specifically designed around system-level evaluation.

⸻

Architecture

The repository is organised into several independent subsystems.

core/
    Fundamental domain model
policy/
    Enterprise authorisation models
auth/
    Provenance-derived authorisation
ites/
    Provenance-aware defence
sled/
    Evaluation framework
execution/
    Shared execution abstractions

Each subsystem has a single responsibility and can evolve independently.

⸻

Core Design Principles

The implementation is based on the following principles.

Provenance-first execution

Every artefact carries provenance.

No information exists without provenance.

⸻

Influence propagation

Derived information inherits the influence of every contributing input.

Influence is never discarded during execution.

⸻

Authorisation from provenance

Authority is derived from provenance rather than runtime identity.

Protected actions are authorised immediately before execution.

⸻

Separation of concerns

The repository separates:

* execution,
* provenance,
* policy,
* authorisation,
* evaluation.

This keeps the architecture modular and allows individual components to evolve independently.

⸻

Evaluation Philosophy

The primary goal of SLED is to evaluate systems, not individual language models.

Accordingly, SLED focuses on:

* system-level abstract attacks,
* information-flow attacks,
* privilege escalation,
* cross-user influence,
* delegated authority,
* indirect prompt injection.

Model-level attacks are included only as reference benchmarks to facilitate comparison with prior work and existing benchmark suites.

They are not the primary methodology for evaluating AI security.

⸻

Repository Status

The project is currently under active development.

Implemented:

* Core provenance model
* Authorisation framework
* Policy abstractions
* ITES defence framework
* SLED evaluation framework
* Initial unit tests

Planned:

* Complete ITES mediation algorithm
* Native SLED benchmark suite
* AWS IAM policy adapter
* Google Cloud IAM adapter
* Microsoft Entra adapter
* AgentDojo benchmark adapter
* Additional benchmark integrations
* Comprehensive evaluation metrics
* Benchmark reporting
* Performance evaluation

⸻

Development Goals

The long-term objective is to provide:

* a practical provenance-aware defence for agentic AI systems,
* realistic enterprise policy integrations,
* reproducible security evaluation,
* compatibility with existing benchmark suites,
* a platform for future research into secure LLM execution.
