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


def test_tiktok_management_reuse_optimization_and_mmp_are_capability_driven() -> None:
    skill = _read("skills/tiktok-insights/SKILL.md")
    public_text = "\n".join(
        _read(path)
        for path in (
            "README.md",
            "docs/faq.md",
            "docs/examples.md",
            "docs/output-contract.md",
        )
    )

    for term in (
        "overview_get_live_configs",
        "copy_ad_quick_copy",
        "copy_ad_clone_structure",
        "campaigns_recreate_from_task",
        "optimization_evaluate",
        "optimization_prepare_action",
        "notifications_list",
        "mmp_insights_get_product_event_today",
        "mmp_insights_query_product_event_summary",
        "mmp_product_aggregate_reads.available=true",
        "channel_pid=tiktokglobal_int",
        "support_report_error",
        "support_get_report_status",
        "creatives_abandon_upload",
    ):
        assert term in skill

    assert "1..20 grouped items" in skill
    assert "same-advertiser" in skill
    assert "disabled initial delivery" in skill
    assert "decimal advertiser-currency major units" in skill
    assert "native `ad_group` scoped" in skill
    assert "never auto-confirm" in skill
    assert "in-app only" in skill
    assert "adapter source field" in skill
    assert "Never include prompts" in skill

    for term in (
        "receipt-backed delivery, budget, bid",
        "copy/clone/recreate",
        "complete-evidence optimization recommendations",
        "manual support reporting",
        "TikTok-channel product MMP aggregates",
    ):
        assert term in public_text


def test_tiktok_router_covers_new_capability_families() -> None:
    router = _read("skills/adsagent-router/SKILL.md")

    for term in (
        "copy",
        "clone",
        "recreate",
        "delivery",
        "budget",
        "bid",
        "optimization",
        "support",
        "TikTok MMP",
        "`tiktok-insights`",
    ):
        assert term in router
