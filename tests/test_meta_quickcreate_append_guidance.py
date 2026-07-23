from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_quickcreate_append_contract_is_consistent_on_public_surfaces():
    surfaces = (
        "skills/meta-copy/SKILL.md",
        "docs/examples.md",
        "docs/faq.md",
        "docs/output-contract.md",
    )
    required = (
        "append_mode=append-campaign",
        "target_campaign_id",
        "append_mode=append-adset",
        "target_adset_id",
        "append_mode=existing",
        "existing_campaign_id",
        "existing_adset_id",
        "product_ref",
        "inherits the existing parent budget",
        "fresh explicit approval",
    )

    for path in surfaces:
        text = _read(path)
        for term in required:
            assert term in text, f"{path} missing {term}"


def test_append_adset_guidance_is_ads_only_and_never_auto_confirms():
    text = _read("skills/meta-copy/SKILL.md")

    assert "campaign_count=1" in text
    assert "adset_count=1" in text
    assert "creates zero Campaigns and zero AdSets" in text
    assert "creates the requested Ads only" in text
    assert "rerun prepare once" in text
    assert "Never auto-confirm" in text
    assert "change permissions" in text
    assert "replay a confirm token" in text


def test_release_version_is_0726():
    assert _read("VERSION").strip() == "0.7.29"
    assert '"version": "0.7.29"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.29"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.29`" in _read("README.md")
