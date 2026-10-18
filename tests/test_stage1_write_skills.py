from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts import validate_tri_channel_pack as pack
from tests.contract_reader import read_contract

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


@pytest.mark.parametrize("skill", ["google-ads-create", "google-ads-manage"])
def test_google_write_skills_require_test_account_for_real_test_writes(skill: str) -> None:
    text = " ".join(_read(f"skills/{skill}/SKILL.md").split())

    assert "test accounts" in text
    assert "adsagent-approvals" in text
    contract = " ".join(
        _read(
            f"skills/{skill}/"
            + ("create-contract.md" if skill.endswith("create") else "manage-contract.md")
        ).split()
    )
    assert "confirm a write only on a customer marked `test_account`" in contract
    assert "never choose a test account to avoid an approval step" in contract.lower() or (
        "never replaces approval" in contract
    )


def test_google_create_requires_location_and_language() -> None:
    text = " ".join(_read("skills/google-ads-create/SKILL.md").split())

    assert "Location and language are required" in text
    assert "google_ads_geo_targets_suggest" in text
    assert "never create a worldwide campaign" in text
    contract = _read("skills/google-ads-create/create-contract.md")
    assert "Never choose a location or language on the user's behalf" in contract
    assert "google_ads_creation_capabilities_get" in contract


def test_google_manage_keeps_location_and_language_when_targeting_changes() -> None:
    text = _read("skills/google-ads-manage/SKILL.md")

    assert "Location and language stay required" in text


def test_approvals_skill_covers_shared_protection_rules() -> None:
    text = " ".join(_read("skills/adsagent-approvals/approval-contract.md").split())

    for term in (
        "`needs_input`",
        "(`validate_only`)",
        "`money_change_exceeds_guard`",
        "`over_cap`",
        "Never split one change",
        "never state a threshold",
        "Never replay",
        "Legacy drafts are not reconfirmed",
        "Never resend the uncertain row",
        "proven-unsent tail",
    ):
        assert term.lower() in text.lower(), term


def test_confirmation_tools_come_from_returned_handle_fields() -> None:
    names = (
        "google-ads-create",
        "google-ads-manage",
        "adsagent-approvals",
        "meta-copy",
    )
    text = "\n".join(_read(f"skills/{name}/SKILL.md") for name in names)
    text += _read("skills/meta-copy/update-contract.md")

    assert "next_action" in text
    assert "confirm_tool" in text
    assert not re.search(r"`google_ads_[a-z_]+_confirm`", text)
    assert "copy_ad_quick_copy_confirm" not in text
    assert "overview_update_campaign_budget_confirm" not in text


def test_meta_update_contract_names_the_new_tools_and_rules() -> None:
    text = " ".join(_read("skills/meta-copy/update-contract.md").split())

    for term in (
        "`entities_prepare_update`",
        "`ads_get_copy`",
        "(`validate_only`)",
        "`money_change_exceeds_guard`",
        "`needs_input`",
        "creates no draft",
    ):
        assert term in text, term


def test_no_risk_control_numbers_in_skills_or_docs() -> None:
    for path in pack.iter_public_safety_files():
        text = path.read_text(encoding="utf-8")
        assert not pack.PUBLIC_SAFETY_PATTERNS["risk-control number"].search(text), path


def test_public_safety_scan_catches_private_names(tmp_path: Path, monkeypatch) -> None:
    leaked = tmp_path / "docs"
    leaked.mkdir()
    (leaked / "note.md").write_text(
        "See the private repo kimlucky7/example for details.\n", encoding="utf-8"
    )
    monkeypatch.setattr(pack, "ROOT", tmp_path)

    with pytest.raises(SystemExit):
        pack.assert_public_safe()


def test_current_tree_passes_public_safety_scan() -> None:
    pack.assert_public_safe()


def test_agents_file_has_no_internal_process() -> None:
    text = _read("AGENTS.md")

    for forbidden in ("standing authorization", "VPS", "Cloudflare", "Supabase"):
        assert forbidden not in text


def test_readme_names_all_supported_clients() -> None:
    readme = _read("README.md")

    for client in ("ChatGPT", "Claude", "Codex", "Cursor"):
        assert client in readme
    assert "Supported clients" in readme


def test_version_matches_changelog_release() -> None:
    assert _read("VERSION").strip() == "0.7.78"
    assert "Version 0.7.78" in _read("CHANGELOG.md")
