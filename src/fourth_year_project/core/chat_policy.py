"""
Conversation visibility and confidentiality policies.

A conversation is itself an information source. User messages become
artifacts whose provenance depends on the participants and whose
confidentiality is governed by the chat policy.

The chat policy determines who may observe information originating from the
conversation. It does not authorise actions; it only constrains the visibility
of information and user-visible actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import FrozenSet

from .actions import ActionVisibility
from .principals import Principal


class ChatConfidentiality(str, Enum):
    """
    Default confidentiality of messages sent within a conversation.
    """

    PRIVATE = "private"
    PARTICIPANTS = "participants"
    AUDITABLE = "auditable"
    PUBLIC = "public"


@dataclass(frozen=True, slots=True)
class ChatPolicy:
    """
    Defines the visibility policy for a conversation.

    Attributes
    ----------
    confidentiality:
        Default confidentiality of information introduced through this chat.
    participants:
        Principals participating in the conversation.
    auditors:
        Principals explicitly permitted to observe auditable conversations.
    allow_provider_logging:
        Whether provider-visible actions may reveal conversational content.
    allow_transcript_visibility:
        Whether transcript-visible actions are permitted.
    allow_user_visible:
        Whether user-visible actions are permitted.
    """

    confidentiality: ChatConfidentiality = ChatConfidentiality.PRIVATE
    participants: FrozenSet[Principal] = field(default_factory=frozenset)
    auditors: FrozenSet[Principal] = field(default_factory=frozenset)
    allow_provider_logging: bool = False
    allow_transcript_visibility: bool = True
    allow_user_visible: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "participants", frozenset(self.participants))
        object.__setattr__(self, "auditors", frozenset(self.auditors))

        if self.confidentiality == ChatConfidentiality.PUBLIC:
            return

        if self.confidentiality == ChatConfidentiality.PRIVATE:
            # Private chats may still have participants, but auditors should not
            # be used to broaden observability unless the policy is auditable.
            return

    def may_observe(self, principal: Principal) -> bool:
        """
        Return whether the principal may observe conversation contents.
        """
        if self.confidentiality == ChatConfidentiality.PUBLIC:
            return True

        if principal in self.participants:
            return True

        if (
            self.confidentiality == ChatConfidentiality.AUDITABLE
            and principal in self.auditors
        ):
            return True

        return False

    def permits_visibility(self, visibility: ActionVisibility) -> bool:
        """
        Return whether an action of the given visibility class may be emitted.
        """
        if visibility == ActionVisibility.INTERNAL:
            return True

        if visibility == ActionVisibility.USER_VISIBLE:
            return self.allow_user_visible

        if visibility == ActionVisibility.TRANSCRIPT_VISIBLE:
            return self.allow_transcript_visibility

        if visibility == ActionVisibility.AUDITED:
            return self.confidentiality == ChatConfidentiality.AUDITABLE

        if visibility == ActionVisibility.PROVIDER_VISIBLE:
            return self.allow_provider_logging

        return False

    def visible_principals(self) -> FrozenSet[Principal]:
        """
        Return every principal that may observe conversation contents.
        """
        visible = set(self.participants)

        if self.confidentiality == ChatConfidentiality.AUDITABLE:
            visible.update(self.auditors)

        if self.confidentiality == ChatConfidentiality.PUBLIC:
            visible.update(self.auditors)

        return frozenset(visible)

    def with_participant(self, principal: Principal) -> "ChatPolicy":
        """
        Return a copy with an additional participant.
        """
        return replace(self, participants=self.participants | {principal})

    def with_participants(self, participants: FrozenSet[Principal]) -> "ChatPolicy":
        """
        Return a copy with a replaced participant set.
        """
        return replace(self, participants=frozenset(participants))

    def with_auditor(self, principal: Principal) -> "ChatPolicy":
        """
        Return a copy with an additional auditor.
        """
        return replace(self, auditors=self.auditors | {principal})

    def with_auditors(self, auditors: FrozenSet[Principal]) -> "ChatPolicy":
        """
        Return a copy with a replaced auditor set.
        """
        return replace(self, auditors=frozenset(auditors))

    def with_confidentiality(self, confidentiality: ChatConfidentiality) -> "ChatPolicy":
        """
        Return a copy with a new confidentiality level.
        """
        return replace(self, confidentiality=confidentiality)

    def with_visibility_controls(
        self,
        *,
        allow_user_visible: bool | None = None,
        allow_transcript_visibility: bool | None = None,
        allow_provider_logging: bool | None = None,
    ) -> "ChatPolicy":
        """
        Return a copy with updated visibility controls.
        """
        return replace(
            self,
            allow_user_visible=self.allow_user_visible if allow_user_visible is None else allow_user_visible,
            allow_transcript_visibility=(
                self.allow_transcript_visibility
                if allow_transcript_visibility is None
                else allow_transcript_visibility
            ),
            allow_provider_logging=(
                self.allow_provider_logging if allow_provider_logging is None else allow_provider_logging
            ),
        )

    @property
    def is_private(self) -> bool:
        return self.confidentiality == ChatConfidentiality.PRIVATE

    @property
    def is_auditable(self) -> bool:
        return self.confidentiality == ChatConfidentiality.AUDITABLE


__all__ = [
    "ChatConfidentiality",
    "ChatPolicy",
]
