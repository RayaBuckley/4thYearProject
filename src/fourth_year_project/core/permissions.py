"""
Permission model.
Permissions represent atomic actions that may be authorised over a resource.
This module intentionally keeps the model simple at first. More expressive policy
semantics can be built later in the policy layer without changing the core
permission types.
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
    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return f"Permission(name={self.name!r})"
READ = Permission("read")
WRITE = Permission("write")
DELETE = Permission("delete")
SHARE = Permission("share")
DELEGATE = Permission("delegate")
