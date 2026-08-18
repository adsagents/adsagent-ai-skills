from __future__ import annotations

from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_plan_reconciliation_contract_is_public() -> None:
    text = "\n".join(
        _read(path)
        for path in (
            "skills/adsagent-reliability/plan-reconciliation-contract.md",
            "skills/meta-copy/creation-and-copy-contract.md",
        )
    )
    for term in (
        "campaigns_reconcile_campaign_plan",
        "creation_intent=fresh|recover",
        "name_collision_policy",
        "match_status",
        "found_outside_scope",
        "review_semantics.state",
        "inventory_issue_labels",
        "plan_reconciliation",
    ):
        assert term in text


def test_plan_reconciliation_release_is_current() -> None:
    assert _read("VERSION").strip() == "0.7.66"
