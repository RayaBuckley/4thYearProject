"""
Protected resources.

A Resource represents an object that may be acted upon by the agent.
Unlike Artifacts, Resources are not pieces of information flowing through
the LLM—they are the targets of primitive actions.

Provider adapters (AWS, Google Cloud, Microsoft Entra, local filesystem,
etc.) materialise concrete Resources from real systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Resource:
    """
    Provider-backed protected object.
    """

    id: str

    provider: str
    """
    Stable provider identifier.

    Examples:
        aws
        gcp
        entra
        filesystem
        postgres
        github
    """

    resource_type: str
    """
    Provider-specific resource kind.

    Examples:
        s3_bucket
        iam_role
        document
        file
        table
    """

    name: str

    attributes: Mapping[str, Any] = field(default_factory=dict)

    def with_attributes(self, **updates: Any) -> "Resource":
        merged = dict(self.attributes)
        merged.update(updates)

        return Resource(
            id=self.id,
            provider=self.provider,
            resource_type=self.resource_type,
            name=self.name,
            attributes=merged,
        )

    @property
    def key(self) -> tuple[str, str]:
        """
        Stable equivalence key used by representative-environment reduction.

        Individual providers may refine this further.
        """
        return (
            self.provider,
            self.resource_type,
        )
