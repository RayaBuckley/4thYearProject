"""
Permission model.

Permissions represent atomic actions that may be authorised over a resource.

This module keeps the core model intentionally small. Provider-specific
policy semantics can be layered later without changing the primitive permission
representation used by principals and the authorisation layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Permission:
    """
    Represents a single permission name.

    Examples:
    - "read"
    - "write"
    - "delete"
    - "share"
    - "delegate"
    """

    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Permission.name must be non-empty")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Permission(name={self.name!r})"


READ = Permission("read")
WRITE = Permission("write")
DELETE = Permission("delete")
SHARE = Permission("share")
DELEGATE = Permission("delegate")


def normalise_permission(permission: str | Permission) -> Permission:
    """
    Convert a string or Permission into a canonical Permission instance.
    """
    if isinstance(permission, Permission):
        return permission

    name = permission.strip()
    if not name:
        raise ValueError("Permission name must be non-empty")

    for built_in in (READ, WRITE, DELETE, SHARE, DELEGATE):
        if built_in.name == name:
            return built_in

    return Permission(name)


def permission_names() -> tuple[str, ...]:
    """
    Return the built-in permission names.
    """
    return (
        READ.name,
        WRITE.name,
        DELETE.name,
        SHARE.name,
        DELEGATE.name,
    )
