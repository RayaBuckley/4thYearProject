"""
Security principals.

A principal represents an entity that can own resources, perform actions,
and be granted permissions within the system.

Principals carry the permissions they are authorised to perform. That keeps
the intersection-rule authorisation model possible without forcing policy
logic into the provenance layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import FrozenSet

from .permissions import Permission, normalise_permission


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
        Category of principal (e.g. "user", "service", "agent").
    permissions:
        The permissions this principal is authorised to perform.
    """

    id: str
    name: str
    principal_type: str = "user"
    permissions: FrozenSet[Permission] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Principal.id must be non-empty")
        if not self.name:
            raise ValueError("Principal.name must be non-empty")

        normalised = frozenset(normalise_permission(permission) for permission in self.permissions)
        object.__setattr__(self, "permissions", normalised)

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
        permission_name = normalise_permission(permission)
        return permission_name in self.permissions

    def with_permissions(self, permissions: FrozenSet[Permission]) -> "Principal":
        """Return a copy of this principal with a new permission set."""
        return replace(self, permissions=frozenset(permissions))

    def add_permission(self, permission: str | Permission) -> "Principal":
        """Return a copy with one additional permission."""
        return replace(self, permissions=self.permissions | {normalise_permission(permission)})

    def remove_permission(self, permission: str | Permission) -> "Principal":
        """Return a copy with one permission removed."""
        target = normalise_permission(permission)
        return replace(self, permissions=frozenset(p for p in self.permissions if p != target))

    @property
    def permission_names(self) -> tuple[str, ...]:
        """Return the principal's permissions as stable names."""
        return tuple(sorted(permission.name for permission in self.permissions))


def principal_has_permission(principal: Principal, permission: str | Permission) -> bool:
    """Compatibility helper for permission checks."""
    return principal.can_perform(permission)
