from pathlib import Path
import re

import pytest

from scripts.skill_contract import read_skill_bundle


ROOT = Path(__file__).resolve().parents[1]


def _bundle(skill: str) -> str:
    text, _ = read_skill_bundle(ROOT, skill)
    return " ".join(text.split())


def test_skills_do_not_teach_platform_targeting_codes() -> None:
    forbidden = re.compile(
        r"\b(?:1000|1001|locales|language_ids|location_ids)\b"
        r"|(?:find|resolve|pass|require)\s+(?:chosen\s+)?(?:location|language) ids",
        re.IGNORECASE,
    )
    violations = [
        str(path.relative_to(ROOT))
        for path in (ROOT / "skills").rglob("*.md")
        if forbidden.search(path.read_text(encoding="utf-8"))
    ]
    assert violations == []


@pytest.mark.parametrize("skill", ["meta-copy", "tiktok-insights"])
def test_creation_guidance_preserves_groups_and_one_approval(skill: str) -> None:
    text = _bundle(skill)
    for term in (
        "`groups`", "video", "image", "country and language names",
        "paused by default", "explicitly asks", "revise",
        "same Campaign", "budget or targeting", "partial",
    ):
        assert term in text, (skill, term)


def test_meta_ranking_uses_reusable_creatives_before_prepare() -> None:
    text = _bundle("meta-copy")
    assert "`creatives_top`" in text
    assert "cached" in text
    assert "`campaigns_quick_create_revise`" in text
    assert "Do not deny and recreate" in text


def test_create_revision_is_distinct_from_batch_composition() -> None:
    text = _bundle("adsagent-approvals")
    assert "revise changes one unconfirmed creation draft" in text
    assert "batch combines changes to existing entities" in text
    assert "original expiry" in text
    assert "old digest" in text
    assert "budget or targeting" in text


def test_google_names_are_sent_without_an_id_lookup_step() -> None:
    text = _bundle("google-ads-create")
    assert "country and language names" in text
    assert "server resolves" in text
    assert "Never choose a location or language on the user's behalf" in text
    assert "match type" in text
    assert "ask" in text.lower()
