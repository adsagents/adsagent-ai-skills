from __future__ import annotations

from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_meta_quickcreate_reconciliation_contract_is_public() -> None:
    text = "\n".join(
        _read(path)
        for path in (
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
            "skills/adsagent-router/SKILL.md",
            "docs/output-contract.md",
            "docs/examples.md",
            "docs/faq.md",
        )
    )

    for term in (
        "destination.type=web|app",
        "created_from=<inclusive>",
        "created_to=<exclusive>",
        "result.create_reconciliation",
        "reconciled=true",
        "creative_results",
        "selection_key",
        "selection_keys",
        "ad_id",
        "approved_task_payload",
        "live_verified=false",
        "operations_get_context(response_mode=compact)",
        "recovered_by_url_fallback",
        "never permits retry or a new task",
    ):
        assert term in text


def test_meta_quickcreate_reconciliation_release_is_current() -> None:
    assert _read("VERSION").strip() == "0.7.60"
    assert '"version": "0.7.60"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.60"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.60`" in _read("README.md")
    assert 'VERSION = "0.7.60"' in _read(
        "scripts/validate_tri_channel_pack.py"
    )


def test_reconciliation_guidance_stays_semi_black_box() -> None:
    text = "\n".join(
        _read(path)
        for path in (
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
            "docs/output-contract.md",
        )
    )

    for private_term in (
        "meta_write_operation_repo",
        "platform_user_id",
        "response_summary",
        "supabase",
        "select * from",
        "access_token",
    ):
        assert private_term not in text.lower()


def test_reconciled_create_separates_live_delivery_and_metric_zero_evidence() -> None:
    paths = (
        "skills/adsagent-reliability/recovery-contract.md",
        "skills/meta-copy/creation-and-copy-contract.md",
        "skills/meta-insights/query-contract.md",
        "docs/output-contract.md",
        "docs/examples.md",
    )
    text = "\n".join(_read(path) for path in paths)

    for term in (
        "create_reconciliation.next_action",
        "retry_write=false",
        "metrics_evidence.zero_proven=true",
        "mutation_coverage",
        "after_mutation_ref",
        "never proves live delivery",
    ):
        assert term in text

    for path in (
        "skills/adsagent-reliability/recovery-contract.md",
        "skills/meta-copy/creation-and-copy-contract.md",
    ):
        contract = _read(path)
        assert "does not prove spend" in contract
        assert "never authorizes replaying the write" in contract
