"""Intersection-rule authorisation.

This module restores the exact rule from the earlier prototype:

- for a primitive action to be authorised, every contributing principal
  in the provenance must be authorised for that action;
- provenance is the only authority-bearing input to the decision;
- resource arguments are accepted for future provider-specific policy layers,
  but they do not weaken the core provenance-derived rule.

The empty-provenance case is intentionally permissive, matching the original
prototype's vacuous truth semantics.
"""

from __future__ import annotations

from fourth_year_project.core.principals import Principal
from fourth_year_project.core.provenance import Provenance
from fourth_year_project.core.resources import Resource


def principals_for(provenance: Provenance) -> frozenset[Principal]:
    """Return the principals that contributed to the provenance."""
    return provenance.principals


def all_principals_authorised(
    provenance: Provenance,
    permission: str,
) -> bool:
    """Return True iff every contributing principal has the permission.

    This is the exact intersection rule from the earlier prototype.
    """
    return all(principal.can_perform(permission) for principal in principals_for(provenance))


def can_access(
    provenance: Provenance,
    resource: Resource,
    permission: str,
) -> bool:
    """Determine whether the provenance is sufficient to access a resource.

    The resource argument is retained so later policy adapters can add
    provider-specific checks, but the core decision remains provenance-driven.
    """
    _ = resource
    return all_principals_authorised(provenance, permission)


def can_read(provenance: Provenance, resource: Resource) -> bool:
    """Convenience wrapper for read access."""
    return can_access(provenance, resource, "read")


def can_write(provenance: Provenance, resource: Resource) -> bool:
    """Convenience wrapper for write access."""
    return can_access(provenance, resource, "write")


def can_delete(provenance: Provenance, resource: Resource) -> bool:
    """Convenience wrapper for delete access."""
    return can_access(provenance, resource, "delete")


def can_share(provenance: Provenance, resource: Resource) -> bool:
    """Convenience wrapper for share access."""
    return can_access(provenance, resource, "share")


def can_delegate(provenance: Provenance, resource: Resource) -> bool:
    """Convenience wrapper for delegation access."""
    return can_access(provenance, resource, "delegate")
