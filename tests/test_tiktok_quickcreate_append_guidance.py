from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tiktok_skill_documents_readiness_and_native_append_contract() -> None:
    text = _read("skills/tiktok-insights/SKILL.md")

    for term in (
        "readiness.create_eligible=true",
        "readiness.reason_code",
        "readiness.retryable",
        "readiness.next_action",
        "creatives_reconcile",
        "1..20",
        "campaigns_quick_create",
        "append_mode=append-campaign",
        "target_campaign_id",
        "append_mode=append-adgroup",
        "target_adgroup_id",
        "operations_get",
        "operation_ref",
        "call_to_action_configured",
        "creative_info.image_info[].web_uri",
        "CAROUSEL_ADS",
        "failed_proven",
        "reconnect the MCP transport",
    ):
        assert term in text

    assert "Never supply both target IDs" in text
    assert "never client-side fan out" in text
    assert "upload_failed" in text
    assert "new explicit upload" in text
    assert "use Meta `append-adset`" in text
    assert "explicit approval" in text
    assert "Confirm once" in text
    assert "Never replay" in text
    assert "Use `task_ref` only for `tasks_get_status`" in text
    assert "Use canonical `operation_ref` only for `operations_get`" in text
    assert "Do not send a CDN image URL" in text
    assert "invent provider CTA, music, or identity IDs" in text


def test_public_surfaces_keep_tiktok_and_meta_append_names_distinct() -> None:
    router = _read("skills/adsagent-router/SKILL.md")
    faq = _read("docs/faq.md")
    output = _read("docs/output-contract.md")

    assert "append to an existing TikTok campaign or ad group" in router
    assert "target_adgroup_id" in router
    assert "TikTok uses a separate native append contract" in faq
    assert "Append-adgroup creates one Ad only" in output
    assert "creatives_reconcile" in faq
    assert "creatives_reconcile" in output
    assert "creatives_confirm_upload" not in faq
    assert "creatives_confirm_upload" not in output


def test_tiktok_smart_plus_append_and_receipt_contract_is_consistent() -> None:
    text = "\n".join(
        _read(path)
        for path in (
            "README.md",
            "skills/tiktok-insights/SKILL.md",
            "docs/faq.md",
            "docs/examples.md",
            "docs/output-contract.md",
        )
    )

    for term in (
        "operation_ref",
        "task_ref",
        "failed_proven",
        "fresh approval",
        "Smart+ image",
        "advertiser ownership",
        "image-family",
    ):
        assert term in text

    assert "operations_get(operation_ref=...)" in text
    assert "tasks_get_status(task_ref=..." in text
    assert "name-match" in text
