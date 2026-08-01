import json
from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_meta_product_health_contract_is_progressively_disclosed():
    entrypoint = (ROOT / "skills/meta-insights/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "[product-health-contract.md](product-health-contract.md)" in entrypoint

    guidance = _read("skills/meta-insights/SKILL.md")
    for term in (
        "products_get_health",
        "products_list",
        "product_ref",
        "does not require a date range",
        "an Insights query",
        "assets_list_pages",
        "connection_health",
        "account_health",
        "page_health",
        "delivery_health",
        "reporting_health",
        "data_coverage",
        "collection_meta",
        "channel_availability",
    ):
        assert term in guidance


def test_meta_product_health_contract_preserves_unknown_and_source_boundaries():
    guidance = _read("skills/meta-insights/SKILL.md")
    for term in (
        "cached-only",
        "never starts an asset refresh",
        "may queue the shared singleflight asset refresh on a cache miss",
        "delivery is unknown",
        "never healthy",
        "must not be converted to zero",
        "requires_top_up=null",
        "balance_semantics",
        "campaign",
        "adset",
        "ad",
        "not_checked",
        "overview_get_live_configs",
        "Use the channel-specific AdsAgent MCP",
        "Never change customer permissions",
    ):
        assert term in guidance


def test_meta_product_health_tools_are_locked_to_the_meta_manifest():
    references = _read("contracts/public-tool-references.json")
    for name in ("products_get_health", "assets_list_pages"):
        assert f'"name": "{name}"' in references


def test_meta_product_health_release_is_consistently_versioned():
    expected = "0.7.50"
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
    assert release["release_url"].endswith(f"/releases/tag/v{expected}")
