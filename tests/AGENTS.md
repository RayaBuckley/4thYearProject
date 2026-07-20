# Test guidance

Tests must cover security invariants, not only happy paths. For security
changes include allowed, denied, mixed-Principal Context, provenance, nested
execution, immutability, and regression cases where applicable. Keep tests
independent of external services unless explicitly marked integration tests.
