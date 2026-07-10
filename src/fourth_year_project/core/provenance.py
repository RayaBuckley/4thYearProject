"""
Provenance tracking for artefacts.
A provenance object records which principals, resources, and operations
contributed to a piece of information. This is the security-critical core of
the project: authorisation decisions will later derive from this data rather
than from a separate trust classification.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import FrozenSet, Self
from .principals import Principal
from .resources import Resource
@dataclass(frozen=True, slots=True)
class Provenance:
    """
    Immutable provenance metadata.
    Attributes
    ----------
    principals:
        Principals that contributed to this artefact.
    resources:
        Resources that influenced or were read to produce this artefact.
    operations:
        Names of operations that participated in producing this artefact.
        These are kept as strings for now to keep the model simple and easy to
        inspect during development.
    """
    principals: FrozenSet[Principal] = field(default_factory=frozenset)
    resources: FrozenSet[Resource] = field(default_factory=frozenset)
    operations: FrozenSet[str] = field(default_factory=frozenset)
    def merge(self, other: Self) -> Self:
        """
        Combine two provenance objects.
        Merging is lossless: no contributing principal, resource, or operation
        is discarded.
        """
        return Provenance(
            principals=self.principals | other.principals,
            resources=self.resources | other.resources,
            operations=self.operations | other.operations,
        )
    @classmethod
    def from_principal(cls, principal: Principal, operation: str | None = None) -> Self:
        """
        Build provenance from a single principal.
        """
        return cls(
            principals=frozenset({principal}),
            operations=frozenset({operation}) if operation is not None else frozenset(),
        )
    @classmethod
    def from_resource(cls, resource: Resource, operation: str | None = None) -> Self:
        """
        Build provenance from a single resource.
        """
        return cls(
            resources=frozenset({resource}),
            operations=frozenset({operation}) if operation is not None else frozenset(),
        )
    def with_operation(self, operation: str) -> Self:
        """
        Return a new provenance object with one additional operation label.
        """
        return Provenance(
            principals=self.principals,
            resources=self.resources,
            operations=self.operations | frozenset({operation}),
        )
