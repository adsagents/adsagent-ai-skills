from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_meta_copy_uses_explicit_delivery_permission_and_budget_paths():
    text = _read("skills/meta-copy/SKILL.md")

    for required in (
        "setup_get_status.capabilities.delivery_mutations",
        "permission_action",
        "/dashboard/settings#mcp-access",
        "mcp.optimize.write",
        "reconnect",
        "re-list tools",
        "overview_update_adset_budget",
        "overview_update_confirm",
        "overview_update_campaign_budget",
        "overview_update_campaign_budget_confirm",
        "Never substitute",
        "support_ref",
    ):
        assert required in text


def test_pack_never_grants_delivery_permission_on_the_users_behalf():
    text = "\n".join(
        _read(path)
        for path in (
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-router/SKILL.md",
            "skills/adsagent-setup/SKILL.md",
            "docs/safety.md",
        )
    )

    assert "Never change permissions automatically" in text
    assert "Never enable or modify customer permissions automatically" in text


def test_known_entity_preflight_never_scans_historical_insights():
    copy_text = "\n".join(
        _read(path)
        for path in (
            "skills/meta-copy/SKILL.md",
            "skills/meta-copy/creation-and-copy-contract.md",
        )
    )
    insights_text = _read("skills/meta-insights/query-contract.md")
    router_text = "\n".join(
        _read(path)
        for path in (
            "skills/adsagent-router/SKILL.md",
            "skills/adsagent-router/routing-contract.md",
        )
    )
    recovery_text = "\n".join(
        _read(path)
        for path in (
            "skills/adsagent-reliability/recovery-contract.md",
            "docs/output-contract.md",
        )
    )

    normalized_copy = " ".join(copy_text.split())
    assert "skip Insights preflight" in normalized_copy
    assert (
        "prepare reads the live current value and does not mutate Meta"
        in normalized_copy
    )
    assert "exactly one typed entity and no" in normalized_copy
    assert "product/date Insights is not live" in normalized_copy

    assert "not a live-configuration preflight" in insights_text
    assert "read_query_too_large" in insights_text
    assert "operator_review_required=false" in insights_text
    assert "automatic_retry_allowed=false" in insights_text
    assert "query_change_required=true" in insights_text
    assert "do not repeat the unchanged request" in insights_text

    assert "known-entity status" in router_text
    assert "matching prepare tool directly" in router_text
    assert "one typed `overview_get_live_configs`" in router_text

    assert "`read_query_too_large`" in recovery_text
    assert "is not an" in recovery_text
    assert "operator incident" in recovery_text


def test_meta_delivery_write_matrix_stops_on_unsupported_object_fields():
    text = " ".join(
        _read("skills/meta-copy/creation-and-copy-contract.md").split()
    )

    for required in (
        "Campaign status: `overview_update_campaign_status`",
        "Campaign budget: `overview_update_campaign_budget`",
        "Ad Set status: `overview_update_adset_status`",
        "Ad Set budget: `overview_update_adset_budget`",
        "Ad Set bid: `overview_update_adset_bid`",
        "Ad status: `overview_update_ad_status`",
        "Campaign bid is unsupported",
        "Ad budget and Ad bid are unsupported",
        "`overview_update_confirm`",
        "`overview_update_campaign_budget_confirm`",
    ):
        assert required in text
