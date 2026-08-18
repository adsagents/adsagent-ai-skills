from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

import pytest

from scripts.meta_template_snapshot_guard import (
    MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH,
    MAX_PUBLIC_DIAGNOSTIC_ITEMS,
    MAX_PUBLIC_SUPPORT_REF_LENGTH,
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
        "setup_get_status.capabilities.template_mutations.allowed=true",
        "`required_capability` is exactly `mcp.templates.write`",
        "templates_get",
        "exact `template_name`",
        "write_accepted_unverified",
        "saved_unverified",
        "snapshot_persisted_unbound",
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
        "invalid_fields_complete",
        "required_fields_complete",
        "support_ref_complete",
        "diagnostics_complete",
        "templates_list",
        "templates_delete",
        "bounded screening",
        "exact-name `templates_get`",
    ):
        assert term in guidance

    assert "Non-empty maps" in guidance
    assert "still not sufficient" in guidance
    assert "reject QuickCreate from an unverified or stale template" in guidance


def test_manual_template_account_binding_is_not_source_provenance():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "all three complete configuration maps",
        "`source_account_id` without `source_adset_id`",
        "account binding",
        "not reverse-engineered source provenance",
        "`source_adset_id` with optional `source_account_id`",
    ):
        assert term in guidance


def test_server_owned_source_import_is_the_only_provenance_only_exception():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "exact server-owned source-import mode",
        "source references are import instructions",
        "not client-supplied snapshot evidence",
        "Outside that exact mode",
    ):
        assert term in guidance


def test_template_guide_resource_is_optional_when_inline_contract_is_present():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "guide_resource_required=false",
        "`inline_contract`",
        "must not block the write",
        "client does not expose MCP Resources",
    ):
        assert term in guidance


def test_precreate_exact_name_miss_is_not_operator_review():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "`complete=true`, `found=false`, and `status=not_found`",
        "normal pre-create read outcome",
        "does not authorize a write",
        "Post-write read-back",
        "persistence unverified",
    ):
        assert term in guidance


def test_creative_distribution_update_uses_existing_canonical_template_tool():
    guidance = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "`templates_update`",
        '"template_name": "<exact template name>"',
        '"creative_distribution": "one_per_adset"',
        "Do not invent a creative-distribution-specific template update tool",
        "update mask exactly matches its patch",
        "`template_snapshot_changed`",
        "Never replay the stale update",
    ):
        assert term in guidance


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
        "templates_list": "mcp.read",
        "templates_get": "mcp.read",
        "templates_update": "mcp.templates.write",
        "templates_delete": "mcp.templates.write",
    }
    for name, capability in expected.items():
        assert registered_tools[name]["required_capability"] == capability
        assert hosted_tools[name]["required_capability"] == capability
        assert (
            hosted_tools[name]["guide_resource"]
            == "adsagent://guide/catalog/templates"
        )


def test_meta_template_persistence_release_is_consistently_versioned():
    expected = "0.7.66"
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
    changelog = " ".join(_read("CHANGELOG.md").split())
    assert "client-side safety mitigation" in changelog
    assert "does not claim that Hosted persistence" in changelog


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


def test_reverse_engineered_write_requires_strict_guide_booleans():
    malformed = TemplateGuideContract(
        snapshot_import_semantics="false",
        bounded_write_schema="false",
        normalization_and_rejected_paths="false",
        immutable_readback_identity="false",
        machine_verifiable_readiness="false",
    )

    assert malformed.allows_reverse_engineered_write is False


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
        assert decision.state == "snapshot_persisted_unbound"
        assert decision.state != "snapshot_verified"
        assert decision.quick_create_allowed is False


def test_snapshot_evidence_requires_strict_booleans():
    decision = evaluate_snapshot(
        TemplateSnapshotEvidence(
            exact_template_name="false",
            write_bound_revision_matches="false",
            campaign_config_accounted_for="false",
            adset_config_accounted_for="false",
            ad_config_accounted_for="false",
            rejected_paths_complete="false",
            launch_critical_coverage_complete="false",
            machine_verifiable_readiness="false",
            persisted="false",
            fresh_read_immediately_before_prepare="false",
            prepare_bound_to_revision="false",
            confirmation_token_bound_to_revision="false",
            legacy_projection="false",
            default_only_projection="false",
            unaccounted_empty_levels=(),
        )
    )

    assert decision.state != "snapshot_verified"
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
    assert rejection.invalid_fields_complete is True
    assert rejection.required_fields_complete is True
    assert rejection.support_ref_complete is True
    assert rejection.diagnostics_complete is True


def test_public_template_diagnostics_are_bounded_deduplicated_and_sanitized():
    secret = "access_token=EAA" + ("s" * 40)
    opaque_secret = "AbCd0123" * 6
    oversized = "field." + (
        "x" * (MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH + 40)
    )
    invalid_fields = [
        "adset_params.bid_strategy",
        "adset_params.bid_strategy",
        {"raw": "mapping"},
        ["nested", "args"],
        True,
        secret,
        opaque_secret,
        "Bearer private-credential",
        '{"raw_args":{"token":"private"}}',
        oversized,
        *[
            f"campaign_params.field_{index}"
            for index in range(MAX_PUBLIC_DIAGNOSTIC_ITEMS + 5)
        ],
    ]

    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "details": {
                    "invalid_fields": invalid_fields,
                    "required_fields": "raw_args=private",
                    "support_ref": {"token": "private"},
                }
            }
        }
    )
    public = asdict(rejection)
    rendered = repr(public)

    assert len(rejection.invalid_fields) == MAX_PUBLIC_DIAGNOSTIC_ITEMS
    assert len(set(rejection.invalid_fields)) == len(
        rejection.invalid_fields
    )
    assert all(
        len(item) <= MAX_PUBLIC_DIAGNOSTIC_ITEM_LENGTH
        for item in rejection.invalid_fields
    )
    assert rejection.required_fields == ()
    assert rejection.support_ref is None
    assert rejection.invalid_fields_complete is False
    assert rejection.required_fields_complete is False
    assert rejection.support_ref_complete is False
    assert rejection.diagnostics_complete is False
    for forbidden in (
        secret,
        opaque_secret,
        "private-credential",
        "raw_args",
        "{'raw': 'mapping'}",
        "{'token': 'private'}",
        "'true'",
    ):
        assert forbidden not in rendered


def test_valid_public_template_diagnostics_remain_backward_compatible():
    rejection = classify_template_write_rejection(
        {
            "details": {
                "invalid_fields": [
                    "adset_params.bid_strategy",
                    "adset_params.bid_strategy",
                    {
                        "field": "request.source_adset_id",
                        "issue": "missing",
                    },
                ],
                "required_fields": ["campaign_params.objective"],
                "support_ref": "merr_template-123",
            }
        }
    )

    assert rejection.invalid_fields == (
        "adset_params.bid_strategy",
        "request.source_adset_id",
    )
    assert rejection.required_fields == ("campaign_params.objective",)
    assert rejection.support_ref == "merr_template-123"
    assert rejection.invalid_fields_complete is True
    assert rejection.required_fields_complete is True
    assert rejection.support_ref_complete is True
    assert rejection.diagnostics_complete is True


def test_hosted_top_level_support_ref_is_preserved():
    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "message": "Request incomplete",
                "details": {
                    "invalid_fields": [
                        {
                            "field": "request.source_adset_id",
                            "issue": "missing",
                        }
                    ],
                    "required_fields": ["request.source_adset_id"],
                },
                "support_ref": "merr_1234567890123456789012",
            }
        }
    )

    assert rejection.support_ref == "merr_1234567890123456789012"
    assert rejection.support_ref_complete is True
    assert rejection.diagnostics_complete is True


def test_hosted_top_level_diagnostics_are_preserved_and_honor_completeness():
    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "details": {
                    "code": "adsagent_request_incomplete",
                },
                "invalid_fields": [
                    {
                        "field": "request.source_adset_id",
                        "issue": "missing",
                    }
                ],
                "required_fields": ["request.source_adset_id"],
                "invalid_fields_complete": False,
                "required_fields_complete": True,
                "diagnostics_complete": False,
            }
        }
    )

    assert rejection.invalid_fields == ("request.source_adset_id",)
    assert rejection.required_fields == ("request.source_adset_id",)
    assert rejection.invalid_fields_complete is False
    assert rejection.required_fields_complete is True
    assert rejection.diagnostics_complete is False


def test_conflicting_completeness_declarations_fail_closed():
    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "details": {
                    "invalid_fields": ["request.source_adset_id"],
                    "invalid_fields_complete": True,
                    "diagnostics_complete": True,
                },
                "invalid_fields_complete": False,
                "diagnostics_complete": "true",
            }
        }
    )

    assert rejection.invalid_fields == ("request.source_adset_id",)
    assert rejection.invalid_fields_complete is False
    assert rejection.diagnostics_complete is False


def test_dual_details_containers_preserve_diagnostics_and_fail_closed():
    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "details": {
                    "code": "adsagent_request_incomplete",
                    "invalid_fields": ["campaign_params.objective"],
                }
            },
            "details": {
                "invalid_fields": ["request.source_adset_id"],
                "support_ref": "merr_template-123",
                "invalid_fields_complete": False,
                "diagnostics_complete": False,
            },
        }
    )

    assert rejection.invalid_fields == (
        "campaign_params.objective",
        "request.source_adset_id",
    )
    assert rejection.support_ref == "merr_template-123"
    assert rejection.invalid_fields_complete is False
    assert rejection.diagnostics_complete is False


def test_conflicting_support_refs_are_omitted_and_marked_incomplete():
    rejection = classify_template_write_rejection(
        {
            "structuredContent": {
                "support_ref": "merr_template-123",
            },
            "details": {
                "support_ref": "merr_template-456",
            },
        }
    )

    assert rejection.support_ref is None
    assert rejection.support_ref_complete is False
    assert rejection.diagnostics_complete is False


@pytest.mark.parametrize(
    ("field", "support_ref"),
    (
        (
            "request.field_EAA" + ("a" * 32),
            "merr_EAA" + ("a" * 32),
        ),
        (
            "request.field_github_pat_" + ("a" * 32),
            "support_github_pat_" + ("a" * 32),
        ),
        (
            "request.field_sk-proj-" + ("a" * 32),
            "ref_sk-proj-" + ("a" * 32),
        ),
    ),
)
def test_credential_shapes_are_never_public_diagnostics(field, support_ref):
    rejection = classify_template_write_rejection(
        {
            "details": {
                "invalid_fields": [field],
                "support_ref": support_ref,
            }
        }
    )

    assert rejection.invalid_fields == ()
    assert rejection.support_ref is None
    assert rejection.invalid_fields_complete is False
    assert rejection.support_ref_complete is False
    assert rejection.diagnostics_complete is False


def test_oversized_support_ref_is_omitted_and_marked_incomplete():
    rejection = classify_template_write_rejection(
        {
            "details": {
                "support_ref": "merr_" + (
                    "x" * MAX_PUBLIC_SUPPORT_REF_LENGTH
                ),
            }
        }
    )

    assert rejection.support_ref is None
    assert rejection.support_ref_complete is False
    assert rejection.diagnostics_complete is False


def test_untyped_scalar_cannot_masquerade_as_support_ref():
    rejection = classify_template_write_rejection(
        {"details": {"support_ref": "private-token-value"}}
    )

    assert rejection.support_ref is None
    assert rejection.support_ref_complete is False
    assert rejection.diagnostics_complete is False


def test_template_lifecycle_routing_boundaries_are_explicit():
    router = " ".join(
        _read("skills/adsagent-router/routing-contract.md").split()
    )
    meta_copy = " ".join(
        _read("skills/meta-copy/template-persistence-contract.md").split()
    )

    for term in (
        "templates_list",
        "templates_get",
        "templates_update",
        "templates_delete",
        "Do not assume Meta",
    ):
        assert term in router
    for term in (
        "list/view/delete/rename",
        "never call Meta template tools",
        "Never implement rename as delete-and-recreate",
    ):
        assert term in meta_copy
