"""
Protected resources.
A resource is any object over which the system may need to reason about access
control. Resources have an owner by default, and ownership is the basis for the
initial permission model.
Examples include:
- Files
- Emails
- Database records
- API endpoints
- Retrieved documents
- External tool handles
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .principals import Principal
@dataclass(frozen=True, slots=True)
class Resource:
    """
    Represents a protected resource.
    Attributes
    ----------
    id:
        Globally unique identifier for the resource.
    owner:
        The principal that owns the resource by default.
    resource_type:
        A simple category label for the resource.
    parent_id:
        Optional identifier of a containing or inherited resource.
        This supports hierarchical resource models later on.
    """
    id: str
    owner: Principal
    resource_type: str = "generic"
    parent_id: Optional[str] = None
    def __str__(self) -> str:
        return self.id
    def __repr__(self) -> str:
        return (
            f"Resource("
            f"id={self.id!r}, "
            f"owner={self.owner!r}, "
            f"resource_type={self.resource_type!r}, "
            f"parent_id={self.parent_id!r})"
        )
