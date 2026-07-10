"""
Information artefacts.
An artefact represents any piece of information manipulated by the system.
Unlike ordinary values, artefacts always carry provenance describing how they
were produced.
All computation within the system should consume and produce artefacts rather
than raw values.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar
from .provenance import Provenance
T = TypeVar("T")
@dataclass(frozen=True, slots=True)
class Artifact(Generic[T]):
    """
    A value together with its provenance.
    Attributes
    ----------
    value:
        The information represented by this artefact.
    provenance:
        The provenance associated with the value.
    """
    value: T
    provenance: Provenance
    def map(self, value: T, operation: str) -> "Artifact[T]":
        """
        Create a new artefact derived from this one.
        The value is replaced while the provenance is preserved and extended
        with the supplied operation.
        """
        return Artifact(
            value=value,
            provenance=self.provenance.with_operation(operation),
        )
    @staticmethod
    def combine(
        left: "Artifact[T]",
        right: "Artifact[T]",
        value: T,
        operation: str,
    ) -> "Artifact[T]":
        """
        Combine two artefacts into a new derived artefact.
        Provenance is merged without loss before recording the new operation.
        """
        return Artifact(
            value=value,
            provenance=(
                left.provenance
                .merge(right.provenance)
                .with_operation(operation)
            ),
        )
    def __repr__(self) -> str:
        return (
            f"Artifact("
            f"value={self.value!r}, "
            f"provenance={self.provenance!r})"
        )
