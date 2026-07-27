"""Executable fail-closed model for reverse-engineered Meta templates.

This module performs no network calls and never constructs a Hosted payload.
It gives the public skill-pack contract deterministic acceptance states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class TemplateGuideContract:
    snapshot_import_semantics: bool
    bounded_write_schema: bool
    normalization_and_rejected_paths: bool
    immutable_readback_identity: bool
    machine_verifiable_readiness: bool

    @property
    def allows_reverse_engineered_write(self) -> bool:
        return all(
            (
                self.snapshot_import_semantics,
                self.bounded_write_schema,
                self.normalization_and_rejected_paths,
                self.immutable_readback_identity,
                self.machine_verifiable_readiness,
            )
        )


@dataclass(frozen=True)
class TemplateSnapshotEvidence:
    exact_template_name: bool
    write_bound_revision_matches: bool
    campaign_config_accounted_for: bool
    adset_config_accounted_for: bool
    ad_config_accounted_for: bool
    rejected_paths_complete: bool
    launch_critical_coverage_complete: bool
    machine_verifiable_readiness: bool
    persisted: bool | None
    fresh_read_immediately_before_prepare: bool
    prepare_bound_to_revision: bool
    confirmation_token_bound_to_revision: bool
    legacy_projection: bool = False
    default_only_projection: bool = False
    unaccounted_empty_levels: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateSnapshotDecision:
    state: str
    quick_create_allowed: bool
    reason: str


@dataclass(frozen=True)
class TemplateWriteRejection:
    state: str
    automatic_retry_allowed: bool
    invalid_fields: tuple[str, ...]
    required_fields: tuple[str, ...]
    support_ref: str | None


def evaluate_snapshot(
    evidence: TemplateSnapshotEvidence,
) -> TemplateSnapshotDecision:
    """Return the launch state for an affected saved template."""

    if not evidence.exact_template_name:
        return TemplateSnapshotDecision(
            state="write_accepted_unverified",
            quick_create_allowed=False,
            reason="exact template read-back missing",
        )
    if not evidence.write_bound_revision_matches:
        return TemplateSnapshotDecision(
            state="write_accepted_unverified",
            quick_create_allowed=False,
            reason="read-back is not bound to the accepted write",
        )

    blockers: list[str] = []
    if evidence.persisted is not True:
        blockers.append("persistence not authoritative")
    if evidence.legacy_projection:
        blockers.append("legacy projection")
    if evidence.default_only_projection:
        blockers.append("default-only projection")
    if evidence.unaccounted_empty_levels:
        blockers.append("unaccounted empty config")
    if not all(
        (
            evidence.campaign_config_accounted_for,
            evidence.adset_config_accounted_for,
            evidence.ad_config_accounted_for,
        )
    ):
        blockers.append("configuration levels not fully accounted for")
    if not evidence.rejected_paths_complete:
        blockers.append("rejected-path report incomplete")
    if not evidence.launch_critical_coverage_complete:
        blockers.append("launch-critical coverage incomplete")
    if not evidence.machine_verifiable_readiness:
        blockers.append("readiness evidence missing")

    if blockers:
        return TemplateSnapshotDecision(
            state="saved_unverified",
            quick_create_allowed=False,
            reason="; ".join(blockers),
        )

    binding_blockers: list[str] = []
    if not evidence.fresh_read_immediately_before_prepare:
        binding_blockers.append("fresh pre-prepare read missing")
    if not evidence.prepare_bound_to_revision:
        binding_blockers.append("prepare is not bound to snapshot revision")
    if not evidence.confirmation_token_bound_to_revision:
        binding_blockers.append(
            "confirmation token is not bound to snapshot revision"
        )
    if binding_blockers:
        return TemplateSnapshotDecision(
            state="snapshot_verified",
            quick_create_allowed=False,
            reason="; ".join(binding_blockers),
        )

    return TemplateSnapshotDecision(
        state="snapshot_verified",
        quick_create_allowed=True,
        reason="authoritative snapshot and QuickCreate binding complete",
    )


def _details(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    structured = payload.get("structuredContent")
    if isinstance(structured, Mapping):
        details = structured.get("details")
        if isinstance(details, Mapping):
            return details
    details = payload.get("details")
    if isinstance(details, Mapping):
        return details
    return payload


def _public_fields(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(
        field
        for item in value
        if (field := str(item).strip())
    )


def classify_template_write_rejection(
    payload: Mapping[str, Any],
) -> TemplateWriteRejection:
    """Classify a rejected template write without authorizing a replay."""

    details = _details(payload)
    support_ref = details.get("support_ref")
    if support_ref is not None:
        support_ref = str(support_ref).strip() or None
    return TemplateWriteRejection(
        state="operator_handoff",
        automatic_retry_allowed=False,
        invalid_fields=_public_fields(details.get("invalid_fields")),
        required_fields=_public_fields(details.get("required_fields")),
        support_ref=support_ref,
    )


__all__ = [
    "TemplateGuideContract",
    "TemplateSnapshotDecision",
    "TemplateSnapshotEvidence",
    "TemplateWriteRejection",
    "classify_template_write_rejection",
    "evaluate_snapshot",
]
