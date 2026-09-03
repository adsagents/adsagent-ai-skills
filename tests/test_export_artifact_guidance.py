from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


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


def test_product_export_requires_authoritative_coverage_before_zero_row_delivery():
    combined = "\n".join(
        [
            _read("skills/meta-insights/SKILL.md"),
            _read("skills/meta-insights/query-contract.md"),
            _read("skills/agent-scheduled-tasks/scheduled-task-contract.md"),
            _read("docs/output-contract.md"),
        ]
    )

    for term in (
        "Product Export And Delivery Gate",
        "insights_query_consistent",
        "metrics_evidence.authoritative=true",
        "metrics_evidence.zero_proven=true",
        "status=incomplete_coverage",
        "row_count=0",
        "artifact_status=ready",
        "insights_export_csv",
        "incomplete—not a proven zero day",
        "Do not email",
    ):
        assert term in combined


def test_release_version_is_current():
    assert _read("VERSION").strip() == "0.7.67"
    assert '"version": "0.7.67"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.67"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.67`" in _read("README.md")
