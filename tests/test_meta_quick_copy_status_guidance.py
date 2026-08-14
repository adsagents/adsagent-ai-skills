from __future__ import annotations

from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_quick_copy_existing_campaign_and_status_fields_are_tool_scoped():
    skill = _read("skills/meta-copy/SKILL.md")
    reference = _read("skills/meta-copy/creation-and-copy-contract.md")

    assert "Quick Copy uses `*_status`, never `status_option`/`append_mode`." in skill

    for term in (
        'mode="new_adsets"',
        "target_campaign_id",
        "campaign_status",
        "adset_status",
        "ad_status",
        "ACTIVE|PAUSED",
        "status_option",
        "copy_ad_clone_structure",
        "append_mode",
        "campaigns_quick_create",
    ):
        assert term in reference

    assert "`status_option` belongs only to `copy_ad_clone_structure`" in reference
    assert "`append_mode` belongs only to `campaigns_quick_create`" in reference
    assert _read("VERSION").strip() == "0.7.61"
