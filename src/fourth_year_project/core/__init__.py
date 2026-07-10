“””
Core domain model.

This package contains the fundamental immutable objects used throughout the
system. These objects are deliberately independent of execution, policy and
authorisation logic.

Modules:

* principals: Represents users, services and other security principals.
* resources: Represents protected resources.
* permissions: Defines permission types.
* provenance: Tracks the causal origins of information.
* artifacts: Represents information together with its provenance.
    “””

from .principals import Principal
from .resources import Resource
from .permissions import Permission
from .provenance import Provenance
from .artifacts import Artifact

all = [
“Principal”,
“Resource”,
“Permission”,
“Provenance”,
“Artifact”,
]
