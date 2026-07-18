from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_meta_pagination_guidance_keeps_one_cached_snapshot_contract():
    combined = "\n".join(
        [
            _read("skills/meta-insights/SKILL.md"),
            _read("docs/output-contract.md"),
        ]
    )

    assert "page 2 and later" in combined
    assert "consistency=cached" in combined
    assert "min_as_of" in combined
    assert "require_complete_range=true" in combined
    assert "pagination_anchor_unavailable" in combined
    assert "never rerun page 1" in combined


def test_meta_write_recovery_guidance_distinguishes_safe_terminal_states():
    combined = "\n".join(
        [
            _read("skills/meta-copy/SKILL.md"),
            _read("skills/adsagent-reliability/SKILL.md"),
            _read("docs/output-contract.md"),
        ]
    )

    for value in (
        "meta_write_rejected",
        "meta_write_verification_pending",
        "verified_created",
        "verified_not_created",
        "verification_ambiguous",
        "operations_get_context",
    ):
        assert value in combined

    assert "fresh task" in combined
    assert "fresh approval" in combined
    assert "never replay" in combined


def test_release_version_is_current():
    assert _read("VERSION").strip() == "0.7.21"
    assert '"version": "0.7.21"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.21"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.21`" in _read("README.md")
