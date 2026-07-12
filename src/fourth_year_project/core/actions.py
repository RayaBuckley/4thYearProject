"""Action taxonomy.

This module defines the common action model used across the core, policy,ITES, and exhaustive-search layers.

The design separates:

primitive provider operations,

nested execution,

delegation,

user-visible chat messages,

clarification / consent requests,

and termination / no-op control actions.

Every action can carry:

input artifacts it depends on,

decision provenance identifying who selected it,

a visibility label describing who may observe it.

This is intentionally generic so provider adapters and chat/session policiescan be layered on top without changing the core action model."""

from future import annotations

from dataclasses import dataclass, fieldfrom enum import Enumfrom typing import Any, FrozenSet, Generic, TypeVar

from .artifacts import Artifactfrom .permissions import Permission, normalise_permissionfrom .principals import Principalfrom .resources import Resource

T = TypeVar("T")

class ActionKind(str, Enum):"""High-level categories of actions."""

PRIMITIVE = "primitive"
NESTED_EXECUTION = "nested_execution"
DELEGATION = "delegation"
MESSAGE_USER = "message_user"
CLARIFICATION_REQUEST = "clarification_request"
REQUEST_CONSENT = "request_consent"
STOP = "stop"
NO_OP = "no_op"

class ActionVisibility(str, Enum):"""Visibility categories for action observability.

INTERNAL:
    Only the executor / core system should observe this action.
USER_VISIBLE:
    May be shown to the chat user.
TRANSCRIPT_VISIBLE:
    May appear in the conversation transcript.
AUDITED:
    May be shown to designated auditors / admins.
PROVIDER_VISIBLE:
    May be visible to an external provider or tool boundary.
"""

INTERNAL = "internal"
USER_VISIBLE = "user_visible"
TRANSCRIPT_VISIBLE = "transcript_visible"
AUDITED = "audited"
PROVIDER_VISIBLE = "provider_visible"

@dataclass(frozen=True, slots=True)class Action(Generic[T]):"""Base class for all actions.

Attributes
----------
kind:
    High-level action kind.
inputs:
    Input artifacts used to derive the action.
decision_principals:
    Principals who actually participated in choosing this action.
    Consent is only meaningful when sourced from one of these principals.
visibility:
    Who may observe the action.
"""

kind: ActionKind
inputs: FrozenSet[Artifact[Any]] = field(default_factory=frozenset)
decision_principals: FrozenSet[Principal] = field(default_factory=frozenset)
visibility: ActionVisibility = ActionVisibility.INTERNAL

def with_visibility(self, visibility: ActionVisibility) -> "Action[T]":
    """Return a copy of this action with a new visibility label."""
    return type(self)(**self._replace_kwargs(visibility=visibility))  # type: ignore[arg-type]

def with_decision_principals(self, principals: FrozenSet[Principal]) -> "Action[T]":
    """Return a copy of this action with a new decision-principal set."""
    return type(self)(**self._replace_kwargs(decision_principals=principals))  # type: ignore[arg-type]

def _replace_kwargs(self, **updates: Any) -> dict[str, Any]:
    data = {
        "kind": self.kind,
        "inputs": self.inputs,
        "decision_principals": self.decision_principals,
        "visibility": self.visibility,
    }
    data.update(updates)
    return data

@dataclass(frozen=True, slots=True)class PrimitiveAction(Action[None]):"""Primitive provider operation.

This is the externally observable action that provider policy adapters
authorise, e.g. read/write/delete/push/send/invoke.
"""

permission: Permission = field(default_factory=lambda: Permission(""))

resource: Resource | None = None
provider_operation: str = ""

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.PRIMITIVE)
    if isinstance(self.permission, str):  # type: ignore[unreachable]
        object.__setattr__(self, "permission", normalise_permission(self.permission))
    if not self.provider_operation:
        raise ValueError("PrimitiveAction.provider_operation must be non-empty")

def __repr__(self) -> str:
    return (
        "PrimitiveAction("
        f"permission={self.permission!r}, "
        f"resource={self.resource!r}, "
        f"provider_operation={self.provider_operation!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class NestedExecutionAction(Action[None]):"""Recursive LLM execution over a new input set.

This is the modern form of the old LLMExecutionAction.
"""

nested_inputs: FrozenSet[Artifact[Any]] = field(default_factory=frozenset)
max_depth_hint: int | None = None

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.NESTED_EXECUTION)

def __repr__(self) -> str:
    return (
        "NestedExecutionAction("
        f"nested_inputs={tuple(self.nested_inputs)!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r}, "
        f"max_depth_hint={self.max_depth_hint!r})"
    )

@dataclass(frozen=True, slots=True)class DelegationAction(Action[None]):"""Delegate authority, work, or execution to another actor.

Delegation is distinct from nested execution because it may change the
authority boundary rather than simply recursing within the same one.
"""

delegate_to: Principal | None = None
scope: str = ""
delegated_permissions: FrozenSet[Permission] = field(default_factory=frozenset)

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.DELEGATION)
    if not self.scope:
        raise ValueError("DelegationAction.scope must be non-empty")

def __repr__(self) -> str:
    return (
        "DelegationAction("
        f"delegate_to={self.delegate_to!r}, "
        f"scope={self.scope!r}, "
        f"delegated_permissions={tuple(self.delegated_permissions)!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class MessageUserAction(Action[str]):"""Emit a user-visible message into the standard chatbot interface.

Because this action can expose state, it is subject to both the visibility
policy and the "can the influencers read all inputs?" rule.
"""

message: str = ""

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.MESSAGE_USER)
    if not self.message:
        raise ValueError("MessageUserAction.message must be non-empty")

def __repr__(self) -> str:
    return (
        "MessageUserAction("
        f"message={self.message!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class ClarificationRequestAction(Action[str]):"""Request missing information from the user.

This is a controlled subtype of user-visible messaging.
"""

prompt: str = ""

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.CLARIFICATION_REQUEST)
    if not self.prompt:
        raise ValueError("ClarificationRequestAction.prompt must be non-empty")

def __repr__(self) -> str:
    return (
        "ClarificationRequestAction("
        f"prompt={self.prompt!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class RequestConsentAction(Action[None]):"""Request consent from the current decision principals.

This does not broaden the authority set. It only asks the already-current
influencers to confirm a proposal.
"""

requested_permission: Permission = field(default_factory=lambda: Permission(""))
target_resource: Resource | None = None
reason: str = ""

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.REQUEST_CONSENT)
    if isinstance(self.requested_permission, str):  # type: ignore[unreachable]
        object.__setattr__(self, "requested_permission", normalise_permission(self.requested_permission))
    if not self.reason:
        raise ValueError("RequestConsentAction.reason must be non-empty")

def __repr__(self) -> str:
    return (
        "RequestConsentAction("
        f"requested_permission={self.requested_permission!r}, "
        f"target_resource={self.target_resource!r}, "
        f"reason={self.reason!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class StopAction(Action[None]):"""Terminate the current branch safely."""

reason: str = ""

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.STOP)
    if not self.reason:
        raise ValueError("StopAction.reason must be non-empty")

def __repr__(self) -> str:
    return (
        "StopAction("
        f"reason={self.reason!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

@dataclass(frozen=True, slots=True)class NoOpAction(Action[None]):"""Do nothing.

Useful for exhaustive search branches where the defence declines to act.
"""

label: str = "noop"

def __post_init__(self) -> None:
    object.__setattr__(self, "kind", ActionKind.NO_OP)

def __repr__(self) -> str:
    return (
        "NoOpAction("
        f"label={self.label!r}, "
        f"inputs={tuple(self.inputs)!r}, "
        f"decision_principals={tuple(self.decision_principals)!r}, "
        f"visibility={self.visibility!r})"
    )

Proposal = (PrimitiveAction| NestedExecutionAction| DelegationAction| MessageUserAction| ClarificationRequestAction| RequestConsentAction| StopAction| NoOpAction)

def is_user_visible(action: Action[Any]) -> bool:"""Return True if the action may be shown to a user."""return action.visibility in {ActionVisibility.USER_VISIBLE, ActionVisibility.TRANSCRIPT_VISIBLE}

def is_transcript_visible(action: Action[Any]) -> bool:"""Return True if the action may appear in the transcript."""return action.visibility == ActionVisibility.TRANSCRIPT_VISIBLE

def is_internal(action: Action[Any]) -> bool:"""Return True if the action is internal-only."""return action.visibility == ActionVisibility.INTERNAL

def action_kind_name(action: Action[Any]) -> str:"""Return the stable string name for an action kind."""return action.kind.value

all = ["Action","ActionKind","ActionVisibility","ClarificationRequestAction","DelegationAction","MessageUserAction","NestedExecutionAction","NoOpAction","PrimitiveAction","Proposal","RequestConsentAction","StopAction","action_kind_name","is_internal","is_transcript_visible","is_user_visible",]
