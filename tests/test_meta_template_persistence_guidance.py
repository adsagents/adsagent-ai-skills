from __future__ import annotations

import json
from pathlib import Path

from scripts.meta_template_snapshot_guard import (
    TemplateGuideContract,
    TemplateSnapshotEvidence,
    classify_template_write_rejection,
    evaluate_snapshot,
)
from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_reverse_engineered_template_uses_fail_closed_snapshot_semantics():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "snapshot semantics",
        "templates_reverse_engineer",
        "unsaved preview",
        "source account/ad set IDs, names, and tags are provenance only",
        "templates_create",
        "templates_update",
        "mcp.templates.write",
        "templates_get",
        "exact `template_name`",
        "write_accepted_unverified",
        "saved_unverified",
        "overwrite=false",
        "campaign_params",
        "adset_params",
        "ad_params",
        "machine-verifiable",
        "Never copy opaque preview maps wholesale into a write",
        "Never send source references alone",
        "this pack defines no positive launch-safe inference",
        "stop before `templates_create` or `templates_update`",
        "source references, names, tags, and `overwrite`",
    ):
        assert term in guidance


def test_template_readback_blocks_unsafe_quickcreate():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "migration_state.persisted=false",
        "legacy_projection",
        "effective_creation_defaults",
        "migration_state.persisted=true",
        "updated_at",
        "saved but not launch-safe",
        "write accepted; persistence unverified",
        "Do not auto-update, delete, recreate, overwrite",
        "campaigns_quick_create",
        "Missing or changed evidence blocks both prepare and confirm",
        "A client re-read or client-added summary echo is not token binding",
        "write_outcome_unknown",
    ):
        assert term in guidance

    assert "Non-empty maps" in guidance
    assert "still not sufficient" in guidance
    assert "reject QuickCreate from an unverified or stale template" in guidance


def test_unactionable_template_validation_never_probes_or_replays():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "direct AdsAgent-state writes",
        "not prepare calls",
        "adsagent_request_incomplete",
        "template_request_incomplete",
        "invalid_fields",
        "required_fields",
        "support_ref",
        "when it is absent, report that none was returned",
        "Do not probe the hidden schema",
        "new explicit user request, not an automatic retry",
    ):
        assert term in guidance


def test_template_tools_are_registered_with_hosted_capabilities():
    contract = json.loads(_read("contracts/public-tool-references.json"))
    registered_tools = {
        entry["name"]: entry
        for entry in contract["channels"]["meta"]["tools"]
    }
    manifest = json.loads(_read("contracts/manifests/meta.json"))
    hosted_tools = {entry["name"]: entry for entry in manifest["tools"]}

    expected = {
        "templates_reverse_engineer": "mcp.read",
        "templates_create": "mcp.templates.write",
        "templates_get": "mcp.read",
        "templates_update": "mcp.templates.write",
    }
    for name, capability in expected.items():
        assert registered_tools[name]["required_capability"] == capability
        assert hosted_tools[name]["required_capability"] == capability
        assert (
            hosted_tools[name]["guide_resource"]
            == "adsagent://guide/catalog/templates"
        )


def test_meta_template_persistence_release_is_consistently_versioned():
    expected = "0.7.40"
    assert _read("VERSION").strip() == expected
    assert f'"version": "{expected}"' in _read(".claude-plugin/plugin.json")
    assert f'"version": "{expected}"' in _read(
        ".claude-plugin/marketplace.json"
    )
    assert f"Current contract version: `{expected}`" in _read("README.md")
    assert f'VERSION = "{expected}"' in _read(
        "scripts/validate_tri_channel_pack.py"
    )
    readme = " ".join(_read("README.md").split())
    assert "client-side safety mitigation" in readme
    assert "does not claim that Hosted persistence" in readme


def _complete_snapshot(**overrides):
    values = {
        "exact_template_name": True,
        "write_bound_revision_matches": True,
        "campaign_config_accounted_for": True,
        "adset_config_accounted_for": True,
        "ad_config_accounted_for": True,
        "rejected_paths_complete": True,
        "launch_critical_coverage_complete": True,
        "machine_verifiable_readiness": True,
        "persisted": True,
        "fresh_read_immediately_before_prepare": True,
        "prepare_bound_to_revision": True,
        "confirmation_token_bound_to_revision": True,
    }
    values.update(overrides)
    return TemplateSnapshotEvidence(**values)


def test_reverse_engineered_write_is_blocked_before_complete_guide_contract():
    incomplete = TemplateGuideContract(
        snapshot_import_semantics=True,
        bounded_write_schema=True,
        normalization_and_rejected_paths=True,
        immutable_readback_identity=False,
        machine_verifiable_readiness=False,
    )
    complete = TemplateGuideContract(
        snapshot_import_semantics=True,
        bounded_write_schema=True,
        normalization_and_rejected_paths=True,
        immutable_readback_identity=True,
        machine_verifiable_readiness=True,
    )

    assert incomplete.allows_reverse_engineered_write is False
    assert complete.allows_reverse_engineered_write is True


def test_empty_legacy_or_default_only_readback_never_allows_quickcreate():
    cases = (
        _complete_snapshot(
            unaccounted_empty_levels=("campaign_params", "adset_params"),
        ),
        _complete_snapshot(legacy_projection=True),
        _complete_snapshot(default_only_projection=True),
        _complete_snapshot(persisted=False),
    )

    for evidence in cases:
        decision = evaluate_snapshot(evidence)
        assert decision.state == "saved_unverified"
        assert decision.quick_create_allowed is False


def test_missing_or_wrong_revision_remains_persistence_unverified():
    missing = evaluate_snapshot(
        _complete_snapshot(exact_template_name=False)
    )
    wrong_revision = evaluate_snapshot(
        _complete_snapshot(write_bound_revision_matches=False)
    )

    assert missing.state == "write_accepted_unverified"
    assert wrong_revision.state == "write_accepted_unverified"
    assert missing.quick_create_allowed is False
    assert wrong_revision.quick_create_allowed is False


def test_only_complete_authoritative_snapshot_allows_quickcreate():
    incomplete = evaluate_snapshot(
        _complete_snapshot(rejected_paths_complete=False)
    )
    complete = evaluate_snapshot(_complete_snapshot())

    assert incomplete.state == "saved_unverified"
    assert incomplete.quick_create_allowed is False
    assert complete.state == "snapshot_verified"
    assert complete.quick_create_allowed is True


def test_snapshot_without_fresh_prepare_and_token_binding_stays_blocked():
    stale_read = evaluate_snapshot(
        _complete_snapshot(fresh_read_immediately_before_prepare=False)
    )
    unbound_prepare = evaluate_snapshot(
        _complete_snapshot(prepare_bound_to_revision=False)
    )
    unbound_token = evaluate_snapshot(
        _complete_snapshot(confirmation_token_bound_to_revision=False)
    )

    for decision in (stale_read, unbound_prepare, unbound_token):
        assert decision.state == "snapshot_verified"
        assert decision.quick_create_allowed is False


def test_generic_template_validation_error_is_operator_handoff_not_retry():
    rejection = classify_template_write_rejection(
        {
            "details": {
                "code": "adsagent_request_incomplete",
                "category": "template_request_incomplete",
            }
        }
    )

    assert rejection.state == "operator_handoff"
    assert rejection.automatic_retry_allowed is False
    assert rejection.invalid_fields == ()
    assert rejection.required_fields == ()
    assert rejection.support_ref is None
