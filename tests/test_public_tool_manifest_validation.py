from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validate_public_tool_manifests import (
    CHANNELS,
    ManifestValidationError,
    documented_tool_names,
    validate_committed_manifests,
    validate_documented_tool_names,
    validate_manifest,
    validate_optional_manifests,
    validate_reference_contract,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "contracts" / "manifests"


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
        if "capability_gate" in reference:
            entry["capability_gates"] = [reference["capability_gate"]]
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


def _copy_real_manifest_set(tmp_path: Path) -> tuple[dict[str, Path], Path]:
    paths: dict[str, Path] = {}
    for channel in CHANNELS:
        destination = tmp_path / "contracts" / "manifests" / f"{channel}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((MANIFEST_DIR / f"{channel}.json").read_bytes())
        paths[channel] = destination
    provenance_path = tmp_path / "contracts" / "manifests" / "provenance.json"
    provenance_path.write_bytes(
        (MANIFEST_DIR / "provenance.json").read_bytes()
    )
    return paths, provenance_path


def _refresh_provenance(
    provenance_path: Path,
    channel: str,
    manifest_path: Path,
) -> None:
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = provenance["channels"][channel]
    entry["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    entry["manifest_version"] = manifest["manifest_version"]
    entry["guide_version"] = manifest["guide_version"]
    entry["tool_count"] = manifest["tool_count"]
    _write_json(provenance_path, provenance)


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


def test_committed_real_manifests_pass_fail_closed_validation() -> None:
    assert validate_committed_manifests(root=ROOT) == (
        "PASS: meta public tool manifest",
        "PASS: google public tool manifest",
        "PASS: tiktok public tool manifest",
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


def test_real_manifest_tool_removal_breaks_release_validation(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    payload = json.loads(paths["meta"].read_text(encoding="utf-8"))
    payload["tools"] = [
        item
        for item in payload["tools"]
        if item["name"] != "overview_get_live_configs"
    ]
    payload["tool_count"] = len(payload["tools"])
    _write_json(paths["meta"], payload)
    _refresh_provenance(provenance_path, "meta", paths["meta"])

    with pytest.raises(
        ManifestValidationError,
        match="overview_get_live_configs",
    ):
        validate_committed_manifests(
            root=ROOT,
            paths=paths,
            provenance_path=provenance_path,
        )


def test_real_tool_without_expected_gate_breaks_release_validation(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    payload = json.loads(paths["meta"].read_text(encoding="utf-8"))
    entry = _tool(payload, "overview_update_adset_budget")
    entry.pop("capability_gate", None)
    entry.pop("gate", None)
    entry["capability_gates"] = [
        gate
        for gate in entry.get("capability_gates", [])
        if gate != "delivery_mutations"
    ]
    _write_json(paths["meta"], payload)
    _refresh_provenance(provenance_path, "meta", paths["meta"])

    with pytest.raises(ManifestValidationError, match="gate mismatch"):
        validate_committed_manifests(
            root=ROOT,
            paths=paths,
            provenance_path=provenance_path,
        )


def test_ci_command_rejects_real_manifest_with_removed_gate(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    payload = json.loads(paths["meta"].read_text(encoding="utf-8"))
    entry = _tool(payload, "overview_update_adset_budget")
    entry.pop("capability_gate", None)
    entry.pop("gate", None)
    entry["capability_gates"] = [
        gate
        for gate in entry.get("capability_gates", [])
        if gate != "delivery_mutations"
    ]
    _write_json(paths["meta"], payload)
    _refresh_provenance(provenance_path, "meta", paths["meta"])

    command = [
        sys.executable,
        "scripts/validate_public_tool_manifests.py",
        "--provenance",
        str(provenance_path),
    ]
    for channel in CHANNELS:
        command.extend(
            ["--manifest", f"{channel}={paths[channel]}"]
        )
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "capability gate mismatch" in result.stderr
    assert "overview_update_adset_budget" in result.stderr


def test_real_manifest_required_capability_drift_breaks_release_validation(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    payload = json.loads(paths["meta"].read_text(encoding="utf-8"))
    entry = _tool(payload, "campaigns_quick_create")
    entry["required_capability"] = "mcp.read"
    _write_json(paths["meta"], payload)
    _refresh_provenance(provenance_path, "meta", paths["meta"])

    with pytest.raises(
        ManifestValidationError,
        match="required capability mismatch",
    ):
        validate_committed_manifests(
            root=ROOT,
            paths=paths,
            provenance_path=provenance_path,
        )


def test_changed_snapshot_without_lock_update_is_stale(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    paths["google"].write_bytes(paths["google"].read_bytes() + b"\n")

    with pytest.raises(
        ManifestValidationError,
        match="stale snapshot digest",
    ):
        validate_committed_manifests(
            root=ROOT,
            paths=paths,
            provenance_path=provenance_path,
        )


def test_missing_real_snapshot_breaks_release_validation(
    tmp_path: Path,
) -> None:
    paths, provenance_path = _copy_real_manifest_set(tmp_path)
    del paths["tiktok"]

    with pytest.raises(
        ManifestValidationError,
        match="manifest missing channel: tiktok",
    ):
        validate_committed_manifests(
            root=ROOT,
            paths=paths,
            provenance_path=provenance_path,
        )


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


def test_ci_invokes_three_pinned_manifests_without_skip_mode() -> None:
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(
        encoding="utf-8"
    )

    for channel in CHANNELS:
        assert (
            f"--manifest {channel}=contracts/manifests/{channel}.json"
            in workflow
        )
    assert "--provenance contracts/manifests/provenance.json" in workflow
    assert "--allow-missing" not in workflow
