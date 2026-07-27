"""Executable fail-closed model for reverse-engineered Meta templates.

This module performs no network calls and never constructs a Hosted payload.
It gives the public skill-pack contract deterministic acceptance states.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Sequence


MAX_PUBLIC_DIAGNOSTIC_ITEMS = 20
MAX_PUBLIC_DIAGNOSTIC_SCAN_ITEMS = 40
MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH = 160
MAX_PUBLIC_SUPPORT_REF_LENGTH = 128

_JSON_CONTAINER_RE = re.compile(r"^\s*[\[{].*[\]}]\s*$", re.DOTALL)
_SENSITIVE_VALUE_RE = re.compile(
    r"(?:\bauthorization\b|\bbearer\s+\S+|"
    r"\b(?:access|refresh|id)[_-]?token\b\s*[:=]|"
    r"\b(?:client|app)[_-]?secret\b\s*[:=]|"
    r"\bpassword\b\s*[:=]|\bcookie\b\s*[:=]|"
    r"\b(?:raw[_-]?)?(?:args?|body|payload)\b\s*[:=])",
    re.IGNORECASE,
)
_TOKEN_SHAPE_RE = re.compile(
    r"(?:EAA[A-Za-z0-9]{24,}|"
    r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\."
    r"[A-Za-z0-9_-]{8,}|"
    r"AKIA[0-9A-Z]{16}|ya29\.[A-Za-z0-9_-]{16,}|"
    r"github_pat_[A-Za-z0-9_]{16,}|"
    r"(?:sk-(?:proj-)?|gh[pousr]_|xox[baprs]-)"
    r"[A-Za-z0-9_-]{16,})",
    re.IGNORECASE,
)
_PUBLIC_FIELD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.\[\]-]*$")
_OPAQUE_SCALAR_RE = re.compile(r"^[A-Za-z0-9_+/=-]{32,}$")
_SUPPORT_REF_RE = re.compile(
    r"^(?:merr_[A-Za-z0-9][A-Za-z0-9_-]{3,63}|"
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})$"
)


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
            value is True
            for value in (
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
    invalid_fields_complete: bool = True
    required_fields_complete: bool = True
    support_ref_complete: bool = True
    diagnostics_complete: bool = True


@dataclass(frozen=True)
class _BoundedPublicStrings:
    values: tuple[str, ...]
    complete: bool


def evaluate_snapshot(
    evidence: TemplateSnapshotEvidence,
) -> TemplateSnapshotDecision:
    """Return the launch state for an affected saved template."""

    if evidence.exact_template_name is not True:
        return TemplateSnapshotDecision(
            state="write_accepted_unverified",
            quick_create_allowed=False,
            reason="exact template read-back missing",
        )
    if evidence.write_bound_revision_matches is not True:
        return TemplateSnapshotDecision(
            state="write_accepted_unverified",
            quick_create_allowed=False,
            reason="read-back is not bound to the accepted write",
        )

    blockers: list[str] = []
    if evidence.persisted is not True:
        blockers.append("persistence not authoritative")
    if evidence.legacy_projection is not False:
        blockers.append("legacy projection")
    if evidence.default_only_projection is not False:
        blockers.append("default-only projection")
    if (
        not isinstance(evidence.unaccounted_empty_levels, tuple)
        or evidence.unaccounted_empty_levels
    ):
        blockers.append("unaccounted empty config")
    if not all(
        value is True
        for value in (
            evidence.campaign_config_accounted_for,
            evidence.adset_config_accounted_for,
            evidence.ad_config_accounted_for,
        )
    ):
        blockers.append("configuration levels not fully accounted for")
    if evidence.rejected_paths_complete is not True:
        blockers.append("rejected-path report incomplete")
    if evidence.launch_critical_coverage_complete is not True:
        blockers.append("launch-critical coverage incomplete")
    if evidence.machine_verifiable_readiness is not True:
        blockers.append("readiness evidence missing")

    if blockers:
        return TemplateSnapshotDecision(
            state="saved_unverified",
            quick_create_allowed=False,
            reason="; ".join(blockers),
        )

    binding_blockers: list[str] = []
    if evidence.fresh_read_immediately_before_prepare is not True:
        binding_blockers.append("fresh pre-prepare read missing")
    if evidence.prepare_bound_to_revision is not True:
        binding_blockers.append("prepare is not bound to snapshot revision")
    if evidence.confirmation_token_bound_to_revision is not True:
        binding_blockers.append(
            "confirmation token is not bound to snapshot revision"
        )
    if binding_blockers:
        return TemplateSnapshotDecision(
            state="snapshot_persisted_unbound",
            quick_create_allowed=False,
            reason="; ".join(binding_blockers),
        )

    return TemplateSnapshotDecision(
        state="snapshot_verified",
        quick_create_allowed=True,
        reason="authoritative snapshot and QuickCreate binding complete",
    )


def _diagnostic_containers(
    payload: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    containers: list[Mapping[str, Any]] = []
    seen: set[int] = set()
    structured = payload.get("structuredContent")
    if isinstance(structured, Mapping):
        details = structured.get("details")
        if isinstance(details, Mapping):
            containers.append(details)
            seen.add(id(details))
        containers.append(structured)
        seen.add(id(structured))
    details = payload.get("details")
    if isinstance(details, Mapping) and id(details) not in seen:
        containers.append(details)
        seen.add(id(details))
    if id(payload) not in seen:
        containers.append(payload)
    return tuple(containers)


def _declared_complete(
    payload: Mapping[str, Any],
    key: str,
) -> bool:
    for container in _diagnostic_containers(payload):
        if key in container and container.get(key) is not True:
            return False
    return True


def _scalar_summary(value: Any, *, max_length: int) -> tuple[str | None, bool]:
    if isinstance(value, str):
        text = value
    elif isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, int):
        text = str(value)
    elif isinstance(value, float) and isfinite(value):
        text = str(value)
    else:
        return None, False

    if len(text) > max_length:
        return None, False
    text = " ".join(text.split())
    if not text:
        return None, False
    if (
        _JSON_CONTAINER_RE.fullmatch(text)
        or _SENSITIVE_VALUE_RE.search(text)
        or _TOKEN_SHAPE_RE.search(text)
    ):
        return None, False
    return text, True


def _public_fields(value: Any) -> _BoundedPublicStrings:
    if value is None:
        return _BoundedPublicStrings((), True)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return _BoundedPublicStrings((), False)

    values: list[str] = []
    seen: set[str] = set()
    complete = len(value) <= MAX_PUBLIC_DIAGNOSTIC_SCAN_ITEMS
    scan_count = min(len(value), MAX_PUBLIC_DIAGNOSTIC_SCAN_ITEMS)
    for index in range(scan_count):
        item = value[index]
        item_shape_complete = True
        if isinstance(item, Mapping):
            if len(item) > 2:
                item_shape_complete = False
                keys: set[Any] = set()
            else:
                keys = set(item)
            issue = item.get("issue")
            item_shape_complete = (
                item_shape_complete
                and "field" in keys
                and keys.issubset({"field", "issue"})
                and (
                    issue is None
                    or (
                        isinstance(issue, str)
                        and issue in {"invalid", "missing"}
                    )
                )
            )
            item = item.get("field")
        if not isinstance(item, str):
            complete = False
            continue
        summary, item_complete = _scalar_summary(
            item,
            max_length=MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH,
        )
        if summary is None:
            complete = False
            continue
        if _PUBLIC_FIELD_RE.fullmatch(summary) is None:
            complete = False
            continue
        if _OPAQUE_SCALAR_RE.fullmatch(summary):
            complete = False
            continue
        if not item_complete or not item_shape_complete:
            complete = False
        if summary in seen:
            continue
        seen.add(summary)
        if len(values) >= MAX_PUBLIC_DIAGNOSTIC_ITEMS:
            complete = False
            continue
        values.append(summary)
    return _BoundedPublicStrings(tuple(values), complete)


def _public_fields_from_payload(
    payload: Mapping[str, Any],
    key: str,
) -> _BoundedPublicStrings:
    values: list[str] = []
    seen: set[str] = set()
    complete = True
    for container in _diagnostic_containers(payload):
        if key not in container:
            continue
        bounded = _public_fields(container.get(key))
        if not bounded.complete:
            complete = False
        for value in bounded.values:
            if value in seen:
                continue
            seen.add(value)
            if len(values) >= MAX_PUBLIC_DIAGNOSTIC_ITEMS:
                complete = False
                continue
            values.append(value)
    return _BoundedPublicStrings(tuple(values), complete)


def _public_support_ref(value: Any) -> tuple[str | None, bool]:
    if value is None:
        return None, True
    summary, complete = _scalar_summary(
        value,
        max_length=MAX_PUBLIC_SUPPORT_REF_LENGTH,
    )
    if (
        summary is None
        or not complete
        or _SUPPORT_REF_RE.fullmatch(summary) is None
    ):
        return None, False
    return summary, True


def _public_support_ref_from_payload(
    payload: Mapping[str, Any],
) -> tuple[str | None, bool]:
    values: list[str] = []
    complete = True
    for container in _diagnostic_containers(payload):
        if "support_ref" not in container:
            continue
        value, value_complete = _public_support_ref(
            container.get("support_ref")
        )
        if not value_complete:
            complete = False
        if value is not None and value not in values:
            values.append(value)
    if len(values) > 1:
        return None, False
    return (values[0] if values else None), complete


def classify_template_write_rejection(
    payload: Mapping[str, Any],
) -> TemplateWriteRejection:
    """Classify a rejected template write without authorizing a replay."""

    invalid_fields = _public_fields_from_payload(
        payload,
        "invalid_fields",
    )
    required_fields = _public_fields_from_payload(
        payload,
        "required_fields",
    )
    support_ref, support_ref_complete = _public_support_ref_from_payload(
        payload
    )
    invalid_fields_complete = (
        invalid_fields.complete
        and _declared_complete(
            payload,
            "invalid_fields_complete",
        )
    )
    required_fields_complete = (
        required_fields.complete
        and _declared_complete(
            payload,
            "required_fields_complete",
        )
    )
    support_ref_complete = (
        support_ref_complete
        and _declared_complete(
            payload,
            "support_ref_complete",
        )
    )
    diagnostics_complete = all(
        (
            invalid_fields_complete,
            required_fields_complete,
            support_ref_complete,
            _declared_complete(payload, "diagnostics_complete"),
        )
    )
    return TemplateWriteRejection(
        state="operator_handoff",
        automatic_retry_allowed=False,
        invalid_fields=invalid_fields.values,
        required_fields=required_fields.values,
        support_ref=support_ref,
        invalid_fields_complete=invalid_fields_complete,
        required_fields_complete=required_fields_complete,
        support_ref_complete=support_ref_complete,
        diagnostics_complete=diagnostics_complete,
    )


__all__ = [
    "TemplateGuideContract",
    "TemplateSnapshotDecision",
    "TemplateSnapshotEvidence",
    "TemplateWriteRejection",
    "MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH",
    "MAX_PUBLIC_DIAGNOSTIC_ITEMS",
    "MAX_PUBLIC_SUPPORT_REF_LENGTH",
    "classify_template_write_rejection",
    "evaluate_snapshot",
]
