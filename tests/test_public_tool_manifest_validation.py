from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_public_tool_manifests import (
    CHANNELS,
    ManifestValidationError,
    documented_tool_names,
    load_deprecated_tools,
    validate_no_deprecated_references,
    validate_offline,
    validate_documented_tool_names,
    validate_manifest,
    validate_optional_manifests,
    validate_reference_contract,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return json.loads(
        (ROOT / "contracts/public-tool-references.json").read_text(
            encoding="utf-8"
        )
    )


def _manifest_for(channel: str) -> dict:
    references = _contract()["channels"][channel]["tools"]
    tools = []
    for reference in references:
        entry = {"name": reference["name"]}
        if "required_capability" in reference:
            entry["required_capability"] = reference[
                "required_capability"
            ]
        gates: list[str] = []
        gate = reference.get("capability_gate")
        if isinstance(gate, str):
            gates.append(gate)
        elif isinstance(gate, list):
            gates.extend(gate)
        extra_gates = reference.get("capability_gates")
        if isinstance(extra_gates, str):
            gates.append(extra_gates)
        elif isinstance(extra_gates, list):
            gates.extend(extra_gates)
        if gates:
            entry["capability_gates"] = gates
        tools.append(entry)
    return {
        "manifest_version": 1,
        "platform": channel,
        "guide_version": "test",
        "tool_count": len(tools),
        "tools": tools,
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _tool(payload: dict, name: str) -> dict:
    return next(item for item in payload["tools"] if item["name"] == name)


def test_reference_contract_names_are_present_in_skill_bundles() -> None:
    validate_reference_contract(ROOT)


def test_unregistered_ghost_tool_fails_before_manifest_lookup() -> None:
    text = "Call `overview_get_nonexistent_config`."

    assert documented_tool_names(text) == {
        "overview_get_nonexistent_config"
    }
    with pytest.raises(ManifestValidationError, match="unregistered tools"):
        validate_documented_tool_names(text, {"overview_get_live_configs"})


def test_release_validation_requires_all_three_channels() -> None:
    with pytest.raises(
        ManifestValidationError,
        match="manifest missing channel: meta",
    ):
        validate_optional_manifests({}, root=ROOT, require_all=True)


def test_developer_compatibility_mode_is_explicitly_optional() -> None:
    messages = validate_optional_manifests({}, root=ROOT)

    assert messages == (
        "SKIP: meta public tool manifest not provided",
        "SKIP: google public tool manifest not provided",
        "SKIP: tiktok public tool manifest not provided",
    )


@pytest.mark.parametrize("channel", CHANNELS)
def test_valid_public_manifest_passes(
    tmp_path: Path,
    channel: str,
) -> None:
    path = tmp_path / f"{channel}.json"
    _write_json(path, _manifest_for(channel))

    validate_manifest(channel, path, root=ROOT)


def test_gate_normalization_accepts_singular_and_list_formats(
    tmp_path: Path,
) -> None:
    payload = _manifest_for("tiktok")
    singular = _tool(payload, "optimization_evaluate")
    singular["capability_gate"] = singular.pop("capability_gates")[0]
    legacy = _tool(payload, "support_report_error")
    legacy.pop("capability_gates")
    payload["capability_gated_tools"] = [
        {
            "name": "support_report_error",
            "gate": "mcp_authenticated",
        }
    ]
    path = tmp_path / "tiktok.json"
    _write_json(path, payload)

    validate_manifest("tiktok", path, root=ROOT)


def test_wrong_channel_identity_fails(tmp_path: Path) -> None:
    payload = _manifest_for("google")
    payload["platform"] = "tiktok"
    path = tmp_path / "google.json"
    _write_json(path, payload)

    with pytest.raises(ManifestValidationError, match="declares channel"):
        validate_manifest("google", path, root=ROOT)


def test_conflicting_duplicate_tool_fails(tmp_path: Path) -> None:
    payload = _manifest_for("google")
    payload["tools"].append(
        {
            "name": payload["tools"][0]["name"],
            "required_capability": "mcp.conflicting",
        }
    )
    payload["tool_count"] = len(payload["tools"])
    path = tmp_path / "google.json"
    _write_json(path, payload)

    with pytest.raises(ManifestValidationError, match="conflicting duplicate"):
        validate_manifest("google", path, root=ROOT)


def test_excessive_manifest_nesting_fails(tmp_path: Path) -> None:
    nested: object = "setup_get_status"
    for _ in range(40):
        nested = [nested]
    path = tmp_path / "meta.json"
    _write_json(
        path,
        {
            "manifest_version": 1,
            "platform": "meta",
            "tools": nested,
        },
    )

    with pytest.raises(ManifestValidationError, match="tool list entries"):
        validate_manifest("meta", path, root=ROOT)


def test_removed_tools_in_nested_manifest_section_do_not_false_pass(
    tmp_path: Path,
) -> None:
    payload = _manifest_for("meta")
    payload["tools"] = {
        "active": payload["tools"],
        "removed": ["overview_get_nonexistent_config"],
    }
    path = tmp_path / "meta.json"
    _write_json(path, payload)

    with pytest.raises(ManifestValidationError, match="tool container"):
        validate_manifest("meta", path, root=ROOT)


def test_setup_prefix_tools_are_checked_in_documentation() -> None:
    text = "Call `setup_reset_connection` before continuing."

    assert documented_tool_names(text) == {"setup_reset_connection"}
    with pytest.raises(ManifestValidationError, match="unregistered tools"):
        validate_documented_tool_names(text, {"setup_get_status"})


def test_explicit_missing_manifest_path_fails(tmp_path: Path) -> None:
    with pytest.raises(ManifestValidationError, match="does not exist"):
        validate_manifest("google", tmp_path / "missing.json", root=ROOT)


def test_offline_validation_has_no_snapshot_dependency() -> None:
    assert validate_offline(ROOT) == (
        "PASS: tool reference contract and deprecated-tool list",
    )
    assert not (ROOT / "contracts" / "manifests").exists()


def test_deprecated_tools_are_named_but_not_referenced() -> None:
    deprecated = load_deprecated_tools(ROOT)

    assert "copy_ad_quick_copy_confirm" in deprecated
    assert "overview_update_campaign_budget_confirm" in deprecated
    validate_no_deprecated_references(ROOT)
    referenced = {
        tool["name"]
        for channel in _contract()["channels"].values()
        for tool in channel["tools"]
    }
    assert referenced.isdisjoint(deprecated)


def test_reference_to_deprecated_tool_fails(tmp_path: Path) -> None:
    root = tmp_path
    (root / "contracts").mkdir()
    (root / "skills" / "meta-copy").mkdir(parents=True)
    (root / "contracts" / "deprecated-tools.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tools": {"old_confirm_tool": {"channel": "meta"}},
            }
        ),
        encoding="utf-8",
    )

    import scripts.validate_public_tool_manifests as module

    original = module._collect_documentation_sources
    module._collect_documentation_sources = lambda _root: [
        ("meta-copy", "Confirm with old_confirm_tool now.")
    ]
    try:
        with pytest.raises(
            ManifestValidationError, match="deprecated tools"
        ):
            validate_no_deprecated_references(root)
    finally:
        module._collect_documentation_sources = original


def test_new_write_skills_are_in_the_reference_contract() -> None:
    channels = _contract()["channels"]

    assert "google-ads-create" in channels["google"]["skill_bundles"]
    assert "google-ads-manage" in channels["google"]["skill_bundles"]
    assert "adsagent-approvals" in channels["meta"]["skill_bundles"]
    names = {tool["name"] for tool in channels["meta"]["tools"]}
    assert {"entities_prepare_update", "ads_get_copy"} <= names
