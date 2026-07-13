"""
Execution session.

A Session represents a single conversation or execution context.

It binds together:
- the conversation participants,
- the confidentiality policy,
- the consent policies,
- and provides convenience methods for determining the current execution
  context.

Sessions intentionally do not contain execution state such as provenance or
LLM recursion. Those belong to artifacts and actions respectively.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import FrozenSet

from .chat_policy import ChatPolicy
from .consent import ConsentProfile
from .principals import Principal


@dataclass(frozen=True, slots=True)
class Session:
    """
    A conversation / execution session.
    """

    id: str
    participants: FrozenSet[Principal] = field(default_factory=frozenset)
    chat_policy: ChatPolicy = field(default_factory=ChatPolicy)
    consent_profiles: FrozenSet[ConsentProfile] = field(default_factory=frozenset)
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Session.id must be non-empty")

        participant_set = frozenset(self.participants)
        object.__setattr__(self, "participants", participant_set)

        profile_principals = {profile.principal for profile in self.consent_profiles}
        unknown = profile_principals - participant_set
        if unknown:
            raise ValueError(
                "Consent profiles exist for non-participants: "
                + ", ".join(sorted(principal.name for principal in unknown))
            )

        # Keep the chat policy aligned with the declared participants where possible.
        if self.chat_policy.participants and not self.chat_policy.participants <= participant_set:
            raise ValueError(
                "Chat policy participants must be a subset of the session participants"
            )

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    def contains(self, principal: Principal) -> bool:
        """
        Return whether the principal participates in this session.
        """
        return principal in self.participants

    def consent_profile(self, principal: Principal) -> ConsentProfile | None:
        """
        Return the consent profile for a participant.
        """
        for profile in self.consent_profiles:
            if profile.principal == principal:
                return profile
        return None

    def with_participant(self, principal: Principal) -> "Session":
        """
        Return a copy with an additional participant.
        """
        return replace(
            self,
            participants=self.participants | {principal},
            chat_policy=self.chat_policy.with_participant(principal),
        )

    def with_participants(self, participants: FrozenSet[Principal]) -> "Session":
        """
        Return a copy with a replaced participant set.
        """
        updated_chat_policy = self.chat_policy
        for principal in participants:
            if principal not in updated_chat_policy.participants:
                updated_chat_policy = updated_chat_policy.with_participant(principal)

        return replace(
            self,
            participants=frozenset(participants),
            chat_policy=updated_chat_policy,
        )

    def with_chat_policy(self, chat_policy: ChatPolicy) -> "Session":
        """
        Return a copy with a new chat policy.
        """
        if chat_policy.participants and not chat_policy.participants <= self.participants:
            raise ValueError(
                "Chat policy participants must be a subset of the session participants"
            )
        return replace(self, chat_policy=chat_policy)

    def with_consent_profile(self, profile: ConsentProfile) -> "Session":
        """
        Return a copy with a new consent profile.
        """
        if profile.principal not in self.participants:
            raise ValueError("Consent profile principal must be a session participant")

        profiles = {p for p in self.consent_profiles if p.principal != profile.principal}
        profiles.add(profile)

        return replace(self, consent_profiles=frozenset(profiles))

    def with_consent_profiles(self, profiles: FrozenSet[ConsentProfile]) -> "Session":
        """
        Return a copy with a new consent profile set.
        """
        profile_principals = {profile.principal for profile in profiles}
        unknown = profile_principals - self.participants
        if unknown:
            raise ValueError(
                "Consent profiles exist for non-participants: "
                + ", ".join(sorted(principal.name for principal in unknown))
            )
        return replace(self, consent_profiles=frozenset(profiles))

    def with_metadata(self, **updates: object) -> "Session":
        """
        Return a copy with updated session metadata.
        """
        merged = dict(self.metadata)
        merged.update(updates)
        return replace(self, metadata=merged)

    def visible_principals(self) -> FrozenSet[Principal]:
        """
        Return every principal permitted to observe conversation contents.
        """
        return self.chat_policy.visible_principals()

    def may_observe(self, principal: Principal) -> bool:
        """
        Return whether a principal may observe conversation contents.
        """
        return self.chat_policy.may_observe(principal)

    def consent_profile_for(self, principal: Principal) -> ConsentProfile | None:
        """
        Compatibility alias for consent_profile.
        """
        return self.consent_profile(principal)


__all__ = [
    "Session",
]
