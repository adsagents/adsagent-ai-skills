import json
from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_meta_pagination_preserves_inventory_generation_anchor():
    guidance = _read("skills/meta-insights/query-contract.md")
    normalized = " ".join(guidance.split())

    for term in (
        "inventory_anchor",
        "inventory_anchors",
        "`data`",
        "`data.items[].result`",
        "continuation_valid=false",
        "discard all partially collected rows",
        "restart from page 1 serially",
    ):
        assert term in normalized


def test_meta_inventory_coverage_keeps_absence_and_zero_metrics_distinct():
    guidance = _read("skills/meta-insights/query-contract.md")
    normalized = " ".join(guidance.split())

    for term in (
        "inventory_coverage=complete",
        "zero_insights_entities_included=true",
        "inventory_freshness",
        "metrics_availability=unverified",
        "null",
        "configured_status",
        "effective_status",
        "delivery_status",
        "delivery_issue_codes",
    ):
        assert term in normalized

    assert "Never rewrite child status from an inherited blocker" in normalized
    assert "never convert unavailable metrics to zero" in normalized


def test_meta_product_health_uses_bounded_current_entity_inventory():
    guidance = _read("skills/meta-insights/SKILL.md")

    for term in (
        "current entity inventory",
        "zero-Insights",
        "inventory coverage",
        "inventory freshness",
        "cached-only",
    ):
        assert term in guidance


def test_meta_entity_inventory_release_is_consistently_versioned():
    expected = "0.7.48"
    assert _read("VERSION").strip() == expected
    assert f'"version": "{expected}"' in _read(".claude-plugin/plugin.json")
    assert f'"version": "{expected}"' in _read(
        ".claude-plugin/marketplace.json"
    )
    assert f"Current contract version: `{expected}`" in _read("README.md")
    assert f'VERSION = "{expected}"' in _read(
        "scripts/validate_tri_channel_pack.py"
    )
    release = json.loads(_read("release-manifest.json"))
    assert release["version"] == expected
    assert release["tag"] == f"v{expected}"
