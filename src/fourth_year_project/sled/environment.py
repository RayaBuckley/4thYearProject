"""
SLED environment model.
SLED is the evaluation layer used to construct scenarios and measure whether a
defence such as ITES behaves safely.
This module defines the data structures that describe the environment seen by
the defence:
- Data items with authors and readers
- Primitive actions proposed by the model
- Nested LLM execution requests
- The overall environment container
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, FrozenSet, Iterable
from fourth_year_project.core import Principal
@dataclass(frozen=True, slots=True)
class Data:
    """
    A piece of environment data.
    Attributes
    ----------
    authors:
        Principals who contributed to or authored the data.
    readers:
        Principals who are permitted to read the data.
    tag:
        Optional human-readable label used by evaluation scenarios.
    """
    authors: FrozenSet[Principal] = field(default_factory=frozenset)
    readers: FrozenSet[Principal] = field(default_factory=frozenset)
    tag: str | None = None
@dataclass(frozen=True, slots=True)
class PrimitiveAction:
    """
    An action that has an external effect.
    The action is represented as a simple string for now so that the evaluation
    layer can remain lightweight and easy to inspect.
    """
    action: str
@dataclass(frozen=True, slots=True)
class LLMExecutionAction:
    """
    A request to execute the LLM again on a new set of inputs.
    """
    inputs: FrozenSet[Data] = field(default_factory=frozenset)
Proposal = PrimitiveAction | LLMExecutionAction
@dataclass(frozen=True, slots=True)
class Environment:
    """
    The complete evaluation environment.
    SLED uses the environment to expose the data available to the defence and
    to derive convenience sets used during evaluation.
    """
    data: FrozenSet[Data] = field(default_factory=frozenset)
    @property
    def total_principals(self) -> FrozenSet[Principal]:
        """
        Return all principals that appear anywhere in the environment.
        """
        principals: set[Principal] = set()
        for item in self.data:
            principals.update(item.authors)
            principals.update(item.readers)
        return frozenset(principals)
    @property
    def tags(self) -> FrozenSet[str]:
        """
        Return all non-empty data tags in the environment.
        """
        return frozenset(item.tag for item in self.data if item.tag is not None)
    def authors_for(self, inputs: Iterable[Data]) -> FrozenSet[Principal]:
        """
        Return the union of authors for a collection of data items.
        """
        authors: set[Principal] = set()
        for item in inputs:
            authors.update(item.authors)
        return frozenset(authors)
    def readable_by(self, principal: Principal, inputs: Iterable[Data]) -> bool:
        """
        Check whether a principal may read all supplied inputs.
        """
        return all(principal in item.readers for item in inputs)
    def contains_all(self, inputs: Iterable[Data]) -> bool:
        """
        Check whether every input is present in the environment.
        """
        env_items = set(self.data)
        return all(item in env_items for item in inputs)
def authors_for(inputs: Iterable[Data]) -> FrozenSet[Principal]:
    """
    Convenience helper for extracting the union of authors from inputs.
    """
    authors: set[Principal] = set()
    for item in inputs:
        authors.update(item.authors)
    return frozenset(authors)
