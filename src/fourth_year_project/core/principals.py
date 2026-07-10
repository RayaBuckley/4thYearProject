"""
Security principals.

A principal represents an entity that can own resources, perform actions,
and be granted permissions within the system.

Examples include:

- Human users
- Service accounts
- Automated agents
- Organisations
- Groups (future extension)

Principals are immutable and uniquely identified by their identifier.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Principal:
    """
    Represents a security principal.

    Attributes
    ----------
    id:
        Globally unique identifier for the principal.

    name:
        Human-readable display name.

    principal_type:
        The category of principal (e.g. "user", "service", "agent").
    """

    id: str
    name: str
    principal_type: str = "user"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"Principal("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"principal_type={self.principal_type!r})"
        )
