"""
Execution operations.
This module defines the basic abstraction for transforming artefacts while
preserving provenance. It is intentionally small: the project does not use a
planner/executor split, so execution units should be lightweight and composable.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar
from fourth_year_project.core import Artifact
T = TypeVar("T")
U = TypeVar("U")
@dataclass(frozen=True, slots=True)
class Operation(ABC, Generic[T, U]):
    """
    Base class for an execution step.
    Subclasses should implement `run`, which accepts an input artefact and
    returns a new derived artefact.
    """
    name: str
    @abstractmethod
    def run(self, artifact: Artifact[T]) -> Artifact[U]:
        """
        Execute the operation on an input artefact.
        """
        raise NotImplementedError
