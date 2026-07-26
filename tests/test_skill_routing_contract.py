from __future__ import annotations

import json
from pathlib import Path

from scripts.skill_contract import markdown_references, read_skill_bundle
from scripts.skill_routing_contract import expected_skill_activation


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    path.parent.name: path
    for path in (ROOT / "skills").glob("*/SKILL.md")
}


def _frontmatter_description(path: Path) -> str:
    frontmatter = path.read_text(encoding="utf-8").split("---\n", 2)[1]
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"{path} has no description")


def test_routing_fixtures_activate_at_most_one_initial_skill() -> None:
    cases = json.loads(
        (ROOT / "tests/fixtures/skill-routing-cases.json").read_text(
            encoding="utf-8"
        )
    )

    for case in cases:
        actual = expected_skill_activation(case["prompt"])
        assert list(actual) == case["expected"], case["id"]
        assert len(actual) <= 1, case["id"]


def test_router_frontmatter_is_ambiguity_only() -> None:
    description = _frontmatter_description(
        SKILLS["adsagent-router"]
    ).lower()

    assert "ambiguous" in description
    assert "spans channels" in description
    for forbidden in (
        "meta",
        "facebook",
        "google",
        "tiktok",
        "retry-after",
        "429",
        "503",
        "copy",
        "performance",
        "notification",
        "scheduled",
    ):
        assert forbidden not in description


def test_specialized_descriptions_have_distinct_primary_intents() -> None:
    descriptions = {
        name: _frontmatter_description(path).lower()
        for name, path in SKILLS.items()
    }

    assert "reading or analyzing meta ads" in descriptions["meta-insights"]
    assert "preparing a meta ads creation" in descriptions["meta-copy"]
    assert "reading or analyzing google ads" in descriptions["google-ads-insights"]
    assert "reading or changing tiktok ads" in descriptions["tiktok-insights"]
    assert "connecting, authorizing" in descriptions["adsagent-setup"]
    assert "mcp call fails" in descriptions["adsagent-reliability"]
    assert "adsagent notifications" in descriptions["adsagent-notifications"]
    assert "agent-owned scheduled task" in descriptions["agent-scheduled-tasks"]


def test_skill_entrypoints_are_small_and_reference_details() -> None:
    total_bytes = 0
    for name, path in SKILLS.items():
        size = path.stat().st_size
        total_bytes += size
        assert size <= 1_600, name
        assert markdown_references(path), name
        bundle, files = read_skill_bundle(ROOT, name)
        assert len(files) >= 2, name
        assert len(bundle) > size, name

    assert total_bytes <= 12_000


def test_reference_graphs_stay_inside_skills_and_are_bounded() -> None:
    for name in SKILLS:
        bundle, files = read_skill_bundle(ROOT, name)
        assert len(files) <= 16, name
        assert len(bundle.encode("utf-8")) <= 128_000, name
