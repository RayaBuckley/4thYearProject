# Testing

Tests live in `tests/` and should validate security invariants before
implementation details. The current suite covers core artifacts and
provenance, authorisation, operations, policies, ITES mediation/state, and
selected SLED benchmark runners.

Run the suite with:

```text
python -m pytest
```

Static checks configured by the project are:

```text
ruff check src tests
mypy src
```

New security behaviour should include allowed, denied, mixed-Principal
Context, provenance-preservation, immutability, and recursive-execution cases.
Provider adapters, external benchmark adapters, trace classification,
reporting, and consent/visibility interactions require additional integration
coverage as they become execution-critical.
