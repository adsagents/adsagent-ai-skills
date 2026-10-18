from pathlib import Path

from scripts.skill_contract import read_skill_bundle


ROOT = Path(__file__).resolve().parents[1]


def test_shared_approval_bundle_explains_partial_batch_consent_and_recovery():
    text, _ = read_skill_bundle(ROOT, "adsagent-approvals")
    for required in (
        "same-kind", "accepted", "excluded", "expected_changes", "confirm_tool",
        "same digest", "original expiry", "not_attempted", "request_sent=false",
        "Suggestions are display-only", "host safety denial",
    ):
        assert required in text
    assert "Prepare exactly one change." not in text


def test_google_management_bundle_prefers_advertised_items_without_splitting_atomic_changes():
    text, _ = read_skill_bundle(ROOT, "google-ads-manage")
    assert "`items`" in text
    assert "same-kind" in text
    assert "shared-budget and portfolio" in text
    assert "confirm_tool" in text


def test_meta_update_keeps_exclusions_visible_and_preserves_unknown_write_fence():
    text = (ROOT / "skills/meta-copy/update-contract.md").read_text()
    assert "accepted" in text and "excluded" in text
    assert "confirm_tool" in text
    assert "not_attempted" in text
    assert 'never prepare the same change again to "try again"' in text


def test_tiktok_and_router_route_multi_entity_changes_to_shared_batch_contract():
    for skill in ("tiktok-insights", "adsagent-router"):
        text, _ = read_skill_bundle(ROOT, skill)
        assert "same-kind" in text.lower()
        assert "accepted" in text and "excluded" in text
        assert "adsagent-approvals" in text
