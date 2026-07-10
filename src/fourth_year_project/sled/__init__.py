"""
SLED: the evaluation environment.
SLED provides the environment and harness used to evaluate defences such as
ITES. It is responsible for constructing scenarios, exposing inputs, and
measuring outcomes so that defence guarantees can be assessed against a known
testbed.
ITES is the defence under test.
SLED is the evaluation engine.
"""
from __future__ import annotations
from .environment import Data, Environment, PrimitiveAction, LLMExecutionAction, Proposal
from .evaluator import Evaluator
__all__ = [
    "Data",
    "Environment",
    "Evaluator",
    "LLMExecutionAction",
    "PrimitiveAction",
    "Proposal",
]
