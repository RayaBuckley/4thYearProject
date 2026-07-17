# AGENTS.md

## Project Identity

Conflux is a research framework that implements and evaluates principal-aware
security for AI agents.

The central research hypothesis is:

> An AI agent should be modelled as being simultaneously influenced by multiple
> principals. The agent's permissions should therefore be determined by its
> current Principal Context rather than by static prompt trust labels.

All implementation decisions should preserve this principle.

---

## Research Goals

Priority order:

1. Correctness of the security model
2. Faithfulness to realistic organisational access control
3. Reproducibility
4. Extensibility
5. Performance

Never sacrifice correctness for convenience.

---

## Core Concepts

### Principal

...

### Principal Context

...

### Provenance

...

### Resources

...

### Delegation

...

---

## Repository Layout

Describe every major directory and its purpose.

---

## Design Principles

Examples:

- Prefer explicit state over implicit behaviour.
- Avoid hidden trust assumptions.
- Provenance is never discarded.
- Policies are composable.
- Evaluation code should remain benchmark-independent.

---

## Coding Principles

- Python version
- Type hints
- Dataclasses
- Pure functions where practical
- Immutable models preferred
- Avoid global state

---

## Documentation Requirements

When implementing a new feature:

- Update Architecture.md if required.
- Update Implementation Status.
- Add tests.
- Document new abstractions.

---

## Benchmark Philosophy

Benchmarks measure the defence—not the benchmark.

Avoid benchmark-specific logic in core modules.

---

## Paper Synchronisation

If an implementation changes the architecture:

- update paper notes
- update architecture docs
- ensure terminology remains consistent

---

## Terminology

Always use:

Principal Context

not:

Current influence set

Always use:

Principal

not:

User

unless specifically referring to human users.

---

## Things Never To Do

Examples:

- Never hard-code benchmark behaviour.
- Never bypass provenance tracking.
- Never remove security checks to satisfy tests.
- Never silently broaden permissions.

---

## Development Workflow

Expected sequence:

Understand architecture

↓

Produce technical specification

↓

Implement

↓

Run tests

↓

Update documentation

↓

Review diff

---

## Definition of Done

A feature is complete only if:

- implementation finished
- tests pass
- documentation updated
- terminology consistent
- benchmark compatibility maintained