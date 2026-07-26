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
