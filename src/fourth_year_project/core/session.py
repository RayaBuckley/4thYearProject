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
        profile_principals = {
            profile.principal
            for profile in self.consent_profiles
        }

        unknown = profile_principals - self.participants

        if unknown:
            raise ValueError(
                "Consent profiles exist for non-participants: "
                + ", ".join(sorted(p.name for p in unknown))
            )

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    def contains(self, principal: Principal) -> bool:
        """
        Return whether the principal participates in this session.
        """
        return principal in self.participants

    def consent_profile(
        self,
        principal: Principal,
    ) -> ConsentProfile | None:
        """
        Return the consent profile for a participant.
        """
        for profile in self.consent_profiles:
            if profile.principal == principal:
                return profile

        return None

    def with_participant(
        self,
        principal: Principal,
    ) -> "Session":
        """
        Return a copy with an additional participant.
        """
        return replace(
            self,
            participants=self.participants | {principal},
            chat_policy=self.chat_policy.with_participant(principal),
        )

    def with_consent_profile(
        self,
        profile: ConsentProfile,
    ) -> "Session":
        """
        Return a copy with a new consent profile.
        """

        profiles = {
            p
            for p in self.consent_profiles
            if p.principal != profile.principal
        }

        profiles.add(profile)

        return replace(
            self,
            consent_profiles=frozenset(profiles),
        )

    def visible_principals(self) -> FrozenSet[Principal]:
        """
        Return every principal permitted to observe conversation contents.
        """
        return self.chat_policy.visible_principals()

    def may_observe(
        self,
        principal: Principal,
    ) -> bool:
        """
        Return whether a principal may observe conversation contents.
        """
        return self.chat_policy.may_observe(principal)


__all__ = [
    "Session",
]
