# Conflux Module Guide

This is the high-level public map of the repository. Individual modules may
contain additional internal helpers that are not extension points.

## Domain and execution

- `core/principals.py`, `resources.py`, and `permissions.py` define security
  identities, protected objects, and permission values.
- `core/provenance.py` and `artifacts.py` define immutable information flow.
- `core/actions.py` defines the action taxonomy and proposals.
- `core/consent.py`, `chat_policy.py`, and `session.py` define consent,
  visibility, and execution-session context.
- `execution/operations.py` provides provenance-preserving transformations.

## Security and mediation

- `auth/authorisation.py` evaluates Principal Context authority.
- `policy/base.py` defines policy requests, decisions, and policy interfaces.
- `policy/adapters.py` and `policy/aws.py` adapt provider policy semantics.
- `ites/__init__.py` defines the ITES contract and result types.
- `ites/mediator.py`, `state.py`, and `properties.py` implement mediation,
  immutable execution state, and security properties.

## Evaluation and integration

- `sled/environment.py` and `scenario.py` model evaluation worlds.
- `sled/attack.py` defines attack extension points.
- `sled/defences/` contains comparison defences and the ITES adapter.
- `sled/evaluator.py`, `evaluation.py`, and `benchmark_runner.py` execute
  suites and branches.
- `sled/trace.py`, `task_classification.py`, `statistics.py`, and
  `reporting.py` produce observable outcomes.
- `providers/` materialises filesystem and Docker environments.
- `benchmarks/` integrates native and external benchmark systems.

The main extension interfaces are `ITES`, `Policy`, `PolicyAdapter`,
`ProviderAdapter`, `Attack`, `TaskSuite`, and the benchmark/external protocols.
Detailed contracts should be specified before adding new implementations.
