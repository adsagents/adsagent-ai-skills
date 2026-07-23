from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tiktok_skill_documents_readiness_and_native_append_contract() -> None:
    text = _read("skills/tiktok-insights/SKILL.md")

    for term in (
        "readiness.create_eligible=true",
        "readiness.status=verification_pending",
        "creatives_confirm_upload",
        "campaigns_quick_create",
        "append_mode=append-campaign",
        "target_campaign_id",
        "append_mode=append-adgroup",
        "target_adgroup_id",
        "operations_get",
        "reconnect the MCP transport",
    ):
        assert term in text

    assert "Never supply both target IDs" in text
    assert "use Meta `append-adset`" in text
    assert "explicit approval" in text
    assert "Confirm once" in text
    assert "Never replay" in text


def test_public_surfaces_keep_tiktok_and_meta_append_names_distinct() -> None:
    router = _read("skills/adsagent-router/SKILL.md")
    faq = _read("docs/faq.md")
    output = _read("docs/output-contract.md")

    assert "append to an existing TikTok campaign or ad group" in router
    assert "target_adgroup_id" in router
    assert "TikTok uses a separate native append contract" in faq
    assert "Append-adgroup creates one Ad only" in output
