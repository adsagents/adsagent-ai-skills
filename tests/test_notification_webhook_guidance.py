from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


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


def test_current_notification_actions_and_push_preserve_authorization():
    guidance = _read("skills/adsagent-notifications/SKILL.md")

    for term in (
        "notifications_list",
        "notifications_summary",
        "Current Meta removed",
        "explicit user approval",
        "events/list",
        "events/subscribe",
        "An event is never",
        "tasks_get_status(task_ref)",
        "Never replay",
        "never claim background monitoring is active",
        "Never create, enable, disable, or modify customer FB User permissions",
    ):
        assert term in guidance


def test_notification_capability_and_source_boundaries_are_explicit():
    guidance = _read("skills/adsagent-notifications/SKILL.md")

    for term in (
        "monitoring_capabilities",
        "notification.created",
        "approval.pending",
        "approval.expiring",
        "task.finished",
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
        "MCP Events do not replace Insights pulls",
        "MCP Events do not continuously stream spend or balance metrics",
        "cached asset-health monitoring",
        "Missing capability evidence stays unknown",
    ):
        assert term in guidance


def test_notification_release_surfaces_are_consistently_versioned():
    assert _read("VERSION").strip() == "0.7.72"
    assert '"version": "0.7.72"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.72"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.72`" in _read("README.md")
    assert 'VERSION = "0.7.72"' in _read("scripts/validate_tri_channel_pack.py")
