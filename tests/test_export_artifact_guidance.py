from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_export_artifact_url_is_treated_as_opaque_capability():
    combined = "\n".join(
        [
            _read("skills/meta-insights/SKILL.md"),
            _read("skills/adsagent-reliability/SKILL.md"),
            _read("docs/output-contract.md"),
        ]
    )

    for term in (
        "result.artifact",
        "download_url",
        "byte-for-byte",
        "Never redact",
        "rebuild",
        "decode",
        "truncate",
        "artifact_status=expired",
        "new explicit export",
    ):
        assert term in combined


def test_release_version_is_current():
    assert _read("VERSION").strip() == "0.7.30"
    assert '"version": "0.7.30"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.30"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.30`" in _read("README.md")
