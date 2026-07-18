from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_terminal_create_failures_are_reported_without_replaying_writes():
    combined = "\n".join(
        _read(path)
        for path in (
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
            "docs/output-contract.md",
        )
    )

    for term in (
        "result.failures.items",
        "ad_name",
        "code",
        "message",
        "next_action",
        "failures.unclassified_count",
        "operator_review_required",
        "fresh approval",
    ):
        assert term in combined

    assert "never retry the unchanged write" in combined.lower()
    assert "raw Meta error" in combined
