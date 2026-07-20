# Conflux package guidance

Follow the repository root `AGENTS.md`. Keep public APIs explicit, typed, and
documented. Preserve provenance and avoid imports from benchmark-specific code
into domain or ITES modules. Prefer immutable dataclasses and dependency
injection over global state.
