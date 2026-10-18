from pathlib import Path

import pytest

from scripts.skill_contract import read_skill_bundle


ROOT = Path(__file__).resolve().parents[1]


def test_shared_approval_bundle_explains_partial_batch_consent_and_recovery():
    text, _ = read_skill_bundle(ROOT, "adsagent-approvals")
    for required in (
        "same-kind", "accepted", "excluded", "complete reviewed change list",
        "confirmation tool named in the prepare result", "live schema",
        "same digest", "original expiry", "proven-unsent",
        "original agreement", "no new agreement",
        "Suggestions are display-only", "host safety denial",
    ):
        assert required in text
    assert "Prepare exactly one change." not in text


def test_google_management_bundle_prefers_advertised_batch_without_splitting_atomic_changes():
    text, _ = read_skill_bundle(ROOT, "google-ads-manage")
    assert "advertised batch" in text
    assert "same-kind" in text
    assert "shared-budget and portfolio" in text
    assert "confirmation tool named in the prepare result" in text
    assert "live schema" in text


def test_meta_update_keeps_exclusions_visible_and_preserves_unknown_write_fence():
    text = (ROOT / "skills/meta-copy/update-contract.md").read_text()
    assert "accepted" in text and "excluded" in text
    assert "confirmation tool named in the prepare result" in text
    assert "proven-unsent" in text
    assert 'never prepare the same change again to "try again"' in text


def test_tiktok_and_router_route_multi_entity_changes_to_shared_batch_contract():
    for skill in ("tiktok-insights", "adsagent-router"):
        text, _ = read_skill_bundle(ROOT, skill)
        assert "same-kind" in text.lower()
        assert "accepted" in text and "excluded" in text
        assert "adsagent-approvals" in text


@pytest.mark.parametrize("path", [
    "adsagent-approvals/approval-contract.md",
    "google-ads-manage/SKILL.md",
    "google-ads-manage/manage-contract.md",
    "meta-copy/update-contract.md",
    "tiktok-insights/channel-contract.md",
])
def test_batch_guidance_does_not_publish_new_payload_fields(path):
    text = (ROOT / "skills" / path).read_text()
    for internal_detail in (
        "`accepted`", "`excluded`", "`expected_changes`", "`confirm_tool`",
        "`not_attempted`", "`request_sent=false`", "`items`",
    ):
        assert internal_detail not in text, (path, internal_detail)


def test_meta_quota_guidance_separates_batch_continuation_from_legacy_reprepare():
    text = (ROOT / "skills/adsagent-reliability/meta-quota-plan.md").read_text()
    batch = text.split("## Advertised Batch Continuation\n", 1)[1].split("\n## ", 1)[0]
    legacy = text.split("## Legacy Quota Plans\n", 1)[1]

    for required in (
        "live contract explicitly advertises", "proven-unsent", "same digest",
        "complete reviewed change list", "original expiry", "original agreement",
        "no new agreement", "Do not re-prepare", "retry time", "uncertain",
        "host safety denial",
    ):
        assert required in batch, required
    for required in (
        "re-prepare only the exact unchanged", "fresh consolidated approval",
        "new confirm token", "Never reuse an old confirm token",
        "normative pure state machine for legacy quota plans only",
    ):
        assert required in legacy, required


def test_routed_recovery_does_not_apply_legacy_consent_to_advertised_batch():
    recovery = (ROOT / "skills/adsagent-reliability/recovery-contract.md").read_text()
    quota_row = next(line for line in recovery.splitlines() if line.startswith("| `mcp_meta_quota_deferred`"))
    approval_row = next(line for line in recovery.splitlines() if line.startswith("| `approval_ref` present"))
    assert "advertised batch continuation" in quota_row
    assert "legacy quota plans" in quota_row
    assert "original agreement" in approval_row
    assert "fresh explicit approval" in approval_row
    assert "never parallel-retry or replay confirm" not in recovery

    entrypoint = (ROOT / "skills/adsagent-reliability/SKILL.md").read_text()
    assert "replay a confirm" not in entrypoint
    router = (ROOT / "skills/adsagent-router/routing-contract.md").read_text()
    assert "advertised batch continuation" in router
    assert "legacy quota plans" in router
