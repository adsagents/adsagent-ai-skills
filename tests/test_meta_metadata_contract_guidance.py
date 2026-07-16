from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_meta_insights_keeps_metadata_roles_and_units_explicit():
    text = _read("skills/meta-insights/SKILL.md")

    for required in (
        "adsagent://guide/metadata-contract",
        "configured_status",
        "effective_status",
        "money_unit=major",
        "budget_level",
        "bid_strategy",
        "optimization_goal",
        "task",
    ):
        assert required in text


def test_meta_copy_uses_canonical_configured_status_write_fields():
    text = _read("skills/meta-copy/SKILL.md")

    assert "target_configured_status=ACTIVE|PAUSED" in text
    assert "current_configured_status" in text
    assert "Never pass `effective_status`" in text


def test_public_output_contract_matches_hosted_metadata_resource():
    text = _read("docs/output-contract.md")

    assert "adsagent://guide/metadata-contract" in text
    assert "account `currency` in major units" in text
    assert "task, batch, notification, and connection `status`" in text
