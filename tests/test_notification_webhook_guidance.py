from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_notification_skill_is_routed_and_packaged():
    router = _read("skills/adsagent-router/SKILL.md")
    plugin = _read(".claude-plugin/plugin.json")

    assert "notification / webhook / email / Feishu / Telegram" in router
    assert "`adsagent-notifications`" in router
    assert '"./skills/adsagent-notifications"' in plugin
    guidance = _read("skills/adsagent-notifications/SKILL.md")
    assert "operator-scoped" in guidance
    assert "OAuth Safe Mode" in guidance
    assert "do not solicit credentials in chat" in guidance


def test_notification_changes_are_prepare_confirm_and_never_replayed():
    guidance = _read("skills/adsagent-notifications/SKILL.md")

    for term in (
        "notifications_integrations_list",
        "notifications_integration_prepare",
        "sanitized summary",
        "explicit user approval",
        "notifications_integration_confirm",
        "tasks_get_status(task_ref)",
        "one real external message",
        "Never replay",
        "fresh approval",
        "Never create, enable, disable, or modify customer FB User permissions",
    ):
        assert term in guidance


def test_notification_capability_and_source_boundaries_are_explicit():
    guidance = _read("skills/adsagent-notifications/SKILL.md")

    for term in (
        "monitoring_capabilities",
        "effective_status",
        "ad_recommendations",
        "with_issues_ad_objects",
        "creative_fatigue",
        "in_process_ad_objects",
        "subscriptions",
        "ad_account_status",
        "ad_account_recharge",
        "page_unpublished",
        "page_ads_restricted",
        "page_no_advertise_access",
        "fb_user_abnormal",
        "fb_user_disabled",
        "fb_user_token_expiring",
        "remaining spend cap <= 50",
        "<= 10 percent",
        "<= 7 days",
        "3600-second cooldown",
        "Webhooks do not replace Insights pulls",
        "Webhooks do not continuously stream spend or balance metrics",
        "cached asset-health monitoring",
        "live-read",
    ):
        assert term in guidance


def test_notification_release_surfaces_are_consistently_versioned():
    assert _read("VERSION").strip() == "0.7.33"
    assert '"version": "0.7.33"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.33"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.33`" in _read("README.md")
    assert 'VERSION = "0.7.33"' in _read("scripts/validate_tri_channel_pack.py")
