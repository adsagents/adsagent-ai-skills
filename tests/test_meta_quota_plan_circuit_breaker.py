from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.meta_quota_plan_guard import (
    MutationIntent,
    PreparedMutation,
    run_confirm_plan,
    validate_resume_plan,
)


def _prepared(
    intents: list[MutationIntent],
    *,
    approval_generation: int,
) -> list[PreparedMutation]:
    return [
        PreparedMutation(
            intent=intent,
            approval_generation=approval_generation,
            confirm_token=f"confirm-generation-{approval_generation}-{index}",
        )
        for index, intent in enumerate(intents, start=1)
    ]


def test_first_pre_send_defer_stops_later_confirms_and_resumes_exact_remainder():
    intents = [
        MutationIntent(
            local_key=f"mutation-{index:02d}",
            value_fingerprint=f"value-{index:02d}",
        )
        for index in range(1, 17)
    ]
    first_generation = _prepared(intents, approval_generation=1)
    confirm_calls: list[str] = []
    provider_sends: Counter[str] = Counter()
    deferred_payloads: list[dict] = []

    def first_confirm(item: PreparedMutation):
        confirm_calls.append(item.intent.local_key)
        if item.intent.local_key == "mutation-12":
            payload = {
                "details": {
                    "code": "mcp_meta_quota_deferred",
                    "request_sent": False,
                    "safe_to_retry": True,
                    "operator_review_required": False,
                    "retry_after_seconds": 60,
                    "plan_recovery": {
                        "action": "stop_remaining_mutations",
                    },
                }
            }
            deferred_payloads.append(payload)
            return payload
        provider_sends[item.intent.local_key] += 1
        return {
            "ok": True,
            "receipt": {"receipt_ref": f"receipt-{item.intent.local_key}"},
        }

    paused = run_confirm_plan(first_generation, first_confirm)

    assert paused.status == "quota_paused"
    assert confirm_calls == [f"mutation-{index:02d}" for index in range(1, 13)]
    assert "mutation-13" not in confirm_calls
    assert "mutation-14" not in confirm_calls
    assert "mutation-15" not in confirm_calls
    assert "mutation-16" not in confirm_calls
    assert len(paused.completed_mutations) == 11
    assert paused.not_sent_mutations == (intents[11],)
    assert paused.remaining_mutations == tuple(intents[12:])
    assert paused.retry_after_seconds == 60
    assert all(
        payload["details"]["request_sent"] is False
        for payload in deferred_payloads
    )

    resumed_generation = _prepared(
        list(paused.resume_intents),
        approval_generation=2,
    )
    validate_resume_plan(paused, resumed_generation)

    def resumed_confirm(item: PreparedMutation):
        confirm_calls.append(item.intent.local_key)
        provider_sends[item.intent.local_key] += 1
        return {
            "ok": True,
            "receipt": {"receipt_ref": f"receipt-{item.intent.local_key}"},
        }

    completed = run_confirm_plan(
        resumed_generation,
        resumed_confirm,
        completed_mutations=paused.completed_mutations,
    )

    assert completed.status == "completed"
    assert len(completed.completed_mutations) == 16
    assert completed.not_sent_mutations == ()
    assert completed.remaining_mutations == ()
    assert set(provider_sends) == {
        f"mutation-{index:02d}" for index in range(1, 17)
    }
    assert all(count == 1 for count in provider_sends.values())


def test_resume_rejects_changed_intent_or_stale_approval_generation():
    intents = [
        MutationIntent(local_key="mutation-01", value_fingerprint="value-01"),
        MutationIntent(local_key="mutation-02", value_fingerprint="value-02"),
    ]

    def defer_first(_item: PreparedMutation):
        return {
            "details": {
                "code": "mcp_meta_quota_deferred",
                "request_sent": False,
                "safe_to_retry": True,
                "operator_review_required": False,
                "retry_after_seconds": 60,
            }
        }

    paused = run_confirm_plan(
        _prepared(intents, approval_generation=1),
        defer_first,
    )

    with pytest.raises(ValueError, match="fresh consolidated approval"):
        validate_resume_plan(
            paused,
            _prepared(list(paused.resume_intents), approval_generation=1),
        )

    changed = [
        MutationIntent(
            local_key="mutation-01",
            value_fingerprint="changed-value",
        ),
        intents[1],
    ]
    with pytest.raises(ValueError, match="exact unchanged remainder"):
        validate_resume_plan(
            paused,
            _prepared(changed, approval_generation=2),
        )


def test_confirm_tokens_are_not_exposed_by_reference_state_repr():
    prepared = PreparedMutation(
        intent=MutationIntent(
            local_key="mutation-01",
            value_fingerprint="value-01",
        ),
        approval_generation=1,
        confirm_token="confirm-secret-must-not-appear",
    )

    assert "confirm-secret-must-not-appear" not in repr(prepared)
