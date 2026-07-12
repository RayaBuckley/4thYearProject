"""Security principals.

A principal represents an entity that can own resources, perform actions,
and be granted permissions within the system.

This version restores the old project’s semantics more closely by letting
principals carry the permissions they are authorised to perform. That keeps
the intersection-rule authorisation model possible without forcing policy
logic into the provenance layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet

from .permissions import Permission


@dataclass(frozen=True, slots=True)
class Principal:
    """Represents a security principal.

    Attributes
    ----------
    id:
        Globally unique identifier for the principal.
    name:
        Human-readable display name.
    principal_type:
        Category of principal (e.g. "user", "service", "agent").
    permissions:
        The permissions this principal is authorised to perform.
    """

    id: str
    name: str
    principal_type: str = "user"
    permissions: FrozenSet[Permission] = field(default_factory=frozenset)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            "Principal("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"principal_type={self.principal_type!r}, "
            f"permissions={tuple(sorted(str(p) for p in self.permissions))!r})"
        )

    def can_perform(self, permission: str | Permission) -> bool:
        """Return True when this principal has the requested permission."""
        permission_name = permission.name if isinstance(permission, Permission) else permission
        return any(p.name == permission_name for p in self.permissions)

    def with_permissions(self, permissions: FrozenSet[Permission]) -> "Principal":
        """Return a copy of this principal with a new permission set."""
        return Principal(
            id=self.id,
            name=self.name,
            principal_type=self.principal_type,
            permissions=frozenset(permissions),
        )
