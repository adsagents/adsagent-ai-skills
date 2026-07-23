"""Reference state machine for Meta pre-send quota plan circuit breaking.

This module performs no network calls and logs no mutation inputs. It exists so
the skill-pack's plan semantics have an executable, deterministic contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence


@dataclass(frozen=True)
class MutationIntent:
    local_key: str
    value_fingerprint: str


@dataclass(frozen=True)
class PreparedMutation:
    intent: MutationIntent
    approval_generation: int
    confirm_token: str = field(repr=False, compare=False)


@dataclass(frozen=True)
class CompletedMutation:
    intent: MutationIntent
    receipt: Mapping[str, Any] = field(repr=False, compare=False)


@dataclass(frozen=True)
class MutationPlanResult:
    status: str
    completed_mutations: tuple[CompletedMutation, ...]
    not_sent_mutations: tuple[MutationIntent, ...]
    remaining_mutations: tuple[MutationIntent, ...]
    attempted_mutations: tuple[MutationIntent, ...]
    retry_after_seconds: int | None
    approval_generation: int

    @property
    def resume_intents(self) -> tuple[MutationIntent, ...]:
        return self.not_sent_mutations + self.remaining_mutations


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


def is_pre_send_quota_defer(payload: Mapping[str, Any]) -> bool:
    details = _details(payload)
    return (
        details.get("code") == "mcp_meta_quota_deferred"
        and details.get("request_sent") is False
        and details.get("safe_to_retry") is True
        and details.get("operator_review_required") is False
    )


def _retry_after_seconds(payload: Mapping[str, Any]) -> int:
    details = _details(payload)
    try:
        return max(1, int(details.get("retry_after_seconds") or 1))
    except (TypeError, ValueError, OverflowError):
        return 1


def _is_success(payload: Mapping[str, Any]) -> bool:
    if payload.get("ok") is True:
        return True
    status = str(payload.get("status") or "").strip().lower()
    return status in {"completed", "ok", "success", "succeeded"}


def run_confirm_plan(
    prepared_mutations: Sequence[PreparedMutation],
    confirm: Callable[[PreparedMutation], Mapping[str, Any]],
    *,
    completed_mutations: Sequence[CompletedMutation] = (),
) -> MutationPlanResult:
    """Confirm serially and stop before all later calls on the first defer."""

    completed = list(completed_mutations)
    completed_intents = {item.intent for item in completed}
    attempted: list[MutationIntent] = []
    if not prepared_mutations:
        generation = max(
            (item.approval_generation for item in prepared_mutations),
            default=0,
        )
        return MutationPlanResult(
            status="completed",
            completed_mutations=tuple(completed),
            not_sent_mutations=(),
            remaining_mutations=(),
            attempted_mutations=(),
            retry_after_seconds=None,
            approval_generation=generation,
        )

    generation = prepared_mutations[0].approval_generation
    if generation < 1 or any(
        item.approval_generation != generation for item in prepared_mutations
    ):
        raise ValueError("one consolidated approval generation is required")
    if len({item.intent for item in prepared_mutations}) != len(prepared_mutations):
        raise ValueError("duplicate mutation intent")
    if any(item.intent in completed_intents for item in prepared_mutations):
        raise ValueError("completed mutation cannot be prepared again")

    for index, prepared in enumerate(prepared_mutations):
        attempted.append(prepared.intent)
        response = confirm(prepared)
        if is_pre_send_quota_defer(response):
            return MutationPlanResult(
                status="quota_paused",
                completed_mutations=tuple(completed),
                not_sent_mutations=(prepared.intent,),
                remaining_mutations=tuple(
                    item.intent for item in prepared_mutations[index + 1 :]
                ),
                attempted_mutations=tuple(attempted),
                retry_after_seconds=_retry_after_seconds(response),
                approval_generation=generation,
            )
        if not _is_success(response):
            return MutationPlanResult(
                status="failed_closed",
                completed_mutations=tuple(completed),
                not_sent_mutations=(),
                remaining_mutations=tuple(
                    item.intent for item in prepared_mutations[index:]
                ),
                attempted_mutations=tuple(attempted),
                retry_after_seconds=None,
                approval_generation=generation,
            )
        completed.append(
            CompletedMutation(
                intent=prepared.intent,
                receipt=dict(response.get("receipt") or {}),
            )
        )

    return MutationPlanResult(
        status="completed",
        completed_mutations=tuple(completed),
        not_sent_mutations=(),
        remaining_mutations=(),
        attempted_mutations=tuple(attempted),
        retry_after_seconds=None,
        approval_generation=generation,
    )


def validate_resume_plan(
    paused: MutationPlanResult,
    reprepared_mutations: Sequence[PreparedMutation],
) -> None:
    if paused.status != "quota_paused":
        raise ValueError("only a quota-paused plan can resume")
    expected = paused.resume_intents
    actual = tuple(item.intent for item in reprepared_mutations)
    if actual != expected:
        raise ValueError("resume must contain the exact unchanged remainder")
    if not reprepared_mutations or any(
        item.approval_generation <= paused.approval_generation
        for item in reprepared_mutations
    ):
        raise ValueError("resume requires one fresh consolidated approval")
    generations = {item.approval_generation for item in reprepared_mutations}
    if len(generations) != 1:
        raise ValueError("resume requires one consolidated approval generation")


__all__ = [
    "CompletedMutation",
    "MutationIntent",
    "MutationPlanResult",
    "PreparedMutation",
    "is_pre_send_quota_defer",
    "run_confirm_plan",
    "validate_resume_plan",
]
