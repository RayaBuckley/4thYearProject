"""
Core authorisation logic.
This module evaluates whether an artefact-derived action may proceed against a
given resource. The initial rule is intentionally simple: access is permitted
only when the provenance includes the relevant resource owner as a contributing
principal.
This keeps the first implementation easy to test while preserving the project’s
main architectural constraint: authorisation is derived from provenance, not
from ambient execution state.
"""
from __future__ import annotations
from fourth_year_project.core import Principal, Provenance, Resource
def effective_authority(provenance: Provenance) -> frozenset[Principal]:
    """
    Return the set of principals contributing authority to the provenance.
    """
    return provenance.principals
def can_access(provenance: Provenance, resource: Resource, permission: str) -> bool:
    """
    Determine whether the provenance is sufficient to access the resource.
    Current rule:
    - access is granted only if the resource owner appears in the provenance
    The permission argument is accepted now so the API can expand later to
    support richer policy rules without changing call sites.
    """
    _ = permission  # Reserved for future policy expansion.
    return resource.owner in effective_authority(provenance)
