#!/usr/bin/env python3
"""Validate public skill references against pinned service tool manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from skill_contract import SkillContractError, read_skill_bundle
except ModuleNotFoundError:  # Imported as scripts.validate_public_tool_manifests.
    from scripts.skill_contract import SkillContractError, read_skill_bundle


ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ("meta", "google", "tiktok")
DEFAULT_MANIFEST_PATHS = {
    channel: ROOT / "contracts" / "manifests" / f"{channel}.json"
    for channel in CHANNELS
}
DEFAULT_PROVENANCE_PATH = (
    ROOT / "contracts" / "manifests" / "provenance.json"
)
ENV_KEYS = {
    "meta": "ADSAGENT_META_TOOL_MANIFEST",
    "google": "ADSAGENT_GOOGLE_TOOL_MANIFEST",
    "tiktok": "ADSAGENT_TIKTOK_TOOL_MANIFEST",
}
MAX_MANIFEST_BYTES = 2_000_000
MAX_MANIFEST_DEPTH = 32
INLINE_CODE_IDENTIFIER_RE = re.compile(
    r"`([a-z][a-z0-9_]+)(?:\([^`]*)?`"
)
TOOL_PREFIXES = (
    "accounts_",
    "assets_",
    "campaigns_",
    "connections_",
    "copy_ad_",
    "creatives_",
    "google_ads_",
    "insights_",
    "mmp_insights_",
    "notifications_",
    "operations_",
    "optimization_",
    "overview_",
    "products_",
    "support_",
    "tasks_",
    "templates_",
)
NON_TOOL_IDENTIFIERS = {
    "insights_export",
    "insights_query_contract",
    "optimization_goal",
    "support_ref",
    "support_refs",
    "support_reporting",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ManifestValidationError(ValueError):
    """Raised for an invalid or drifting public tool manifest."""


def _normalize_tool_name(value: str) -> str:
    return value.rsplit("__", 1)[-1].strip()


def _string_set(value: Any, *, label: str) -> frozenset[str]:
    if value is None:
        return frozenset()
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, list) or not all(
        isinstance(item, str) and item.strip() for item in values
    ):
        raise ManifestValidationError(
            f"{label} must be a string or a list of non-empty strings"
        )
    return frozenset(item.strip() for item in values)


def _entries(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    pending: list[tuple[Any, int]] = [(value, 0)]
    while pending:
        current, depth = pending.pop()
        if depth > MAX_MANIFEST_DEPTH:
            raise ManifestValidationError(
                f"manifest nesting exceeds {MAX_MANIFEST_DEPTH}"
            )
        if isinstance(current, str):
            result.append(
                {
                    "name": _normalize_tool_name(current),
                    "capability_gates": frozenset(),
                    "required_capabilities": frozenset(),
                }
            )
            continue
        if isinstance(current, list):
            pending.extend(
                (item, depth + 1) for item in reversed(current)
            )
            continue
        if not isinstance(current, dict):
            continue
        if isinstance(current.get("name"), str):
            gates = frozenset()
            for key in ("capability_gate", "capability_gates", "gate"):
                gates |= _string_set(
                    current.get(key),
                    label=f"{current['name']}.{key}",
                )
            required_capabilities = frozenset()
            for key in ("required_capability", "required_capabilities"):
                required_capabilities |= _string_set(
                    current.get(key),
                    label=f"{current['name']}.{key}",
                )
            result.append(
                {
                    "name": _normalize_tool_name(current["name"]),
                    "capability_gates": gates,
                    "required_capabilities": required_capabilities,
                }
            )
            continue
        pending.extend(
            (item, depth + 1)
            for item in reversed(tuple(current.values()))
        )
    return result


def _index_entries(
    entries: list[dict[str, Any]],
    *,
    label: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        name = entry["name"]
        if not name:
            continue
        previous = indexed.get(name)
        if previous is not None and previous != entry:
            raise ManifestValidationError(
                f"{label} contains conflicting duplicate tool: {name}"
            )
        indexed[name] = entry
    return indexed


def _merge_entry_indexes(
    tools: dict[str, dict[str, Any]],
    gated: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged = {name: dict(entry) for name, entry in tools.items()}
    for name, entry in gated.items():
        previous = merged.get(name)
        if previous is None:
            merged[name] = dict(entry)
            continue
        previous_capabilities = previous["required_capabilities"]
        next_capabilities = entry["required_capabilities"]
        if (
            previous_capabilities
            and next_capabilities
            and previous_capabilities != next_capabilities
        ):
            raise ManifestValidationError(
                "tools and capability-gated lists conflict for tool: "
                f"{name}"
            )
        previous["required_capabilities"] = (
            previous_capabilities | next_capabilities
        )
        previous["capability_gates"] = (
            previous["capability_gates"] | entry["capability_gates"]
        )
    return merged


def _manifest_entries(
    payload: Any,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    if isinstance(payload, list):
        return _index_entries(_entries(payload), label="tools"), {}
    if not isinstance(payload, dict):
        raise ManifestValidationError("manifest root must be an object or list")

    tool_payload = None
    for key in ("tools", "public_tools", "tool_manifest"):
        if key in payload:
            tool_payload = payload[key]
            break
    if tool_payload is None:
        raise ManifestValidationError(
            "manifest must contain tools, public_tools, or tool_manifest"
        )

    tools = _index_entries(_entries(tool_payload), label="tools")
    gated: dict[str, dict[str, Any]] = {}
    for key in ("capability_gated_tools", "gated_tools"):
        if key not in payload:
            continue
        indexed = _index_entries(_entries(payload[key]), label=key)
        for name, entry in indexed.items():
            previous = gated.get(name)
            if previous is not None and previous != entry:
                raise ManifestValidationError(
                    "capability-gated lists contain conflicting duplicate "
                    f"tool: {name}"
                )
            gated[name] = entry
    return tools, gated


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise ManifestValidationError(f"manifest does not exist: {path}")
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ManifestValidationError(f"manifest exceeds size limit: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestValidationError(f"invalid manifest {path}: {exc}") from exc


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ManifestValidationError(
            f"unable to hash manifest {path}: {exc}"
        ) from exc


def _load_reference_contract(root: Path) -> dict[str, Any]:
    payload = _load_json(root / "contracts/public-tool-references.json")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ManifestValidationError("unsupported tool reference contract")
    channels = payload.get("channels")
    if not isinstance(channels, dict):
        raise ManifestValidationError("tool reference contract has no channels")
    if set(channels) != set(CHANNELS):
        raise ManifestValidationError(
            "tool reference contract must define exactly meta, google, tiktok"
        )
    return channels


def documented_tool_names(text: str) -> set[str]:
    """Extract callable-looking public tool names from inline code."""
    return {
        name
        for name in INLINE_CODE_IDENTIFIER_RE.findall(text)
        if name.startswith(TOOL_PREFIXES)
        and name not in NON_TOOL_IDENTIFIERS
        and not name.endswith("_tool")
    }


def validate_documented_tool_names(
    text: str,
    registered_names: set[str],
) -> None:
    unregistered = sorted(documented_tool_names(text) - registered_names)
    if unregistered:
        raise ManifestValidationError(
            "skill references unregistered tools: "
            + ", ".join(unregistered)
        )


def validate_reference_contract(root: Path = ROOT) -> None:
    channels = _load_reference_contract(root)
    registered_names: set[str] = set()
    all_bundle_text = ""
    for channel, contract in channels.items():
        if channel not in CHANNELS or not isinstance(contract, dict):
            raise ManifestValidationError(f"invalid channel contract: {channel}")
        bundles = contract.get("skill_bundles")
        references = contract.get("tools")
        if not isinstance(bundles, list) or not isinstance(references, list):
            raise ManifestValidationError(
                f"{channel} contract must define skill_bundles and tools"
            )
        bundle_text = ""
        for skill_name in bundles:
            try:
                text, _ = read_skill_bundle(root, str(skill_name))
            except SkillContractError as exc:
                raise ManifestValidationError(str(exc)) from exc
            bundle_text += "\n" + text
        all_bundle_text += "\n" + bundle_text
        channel_names: set[str] = set()
        for reference in references:
            if not isinstance(reference, dict) or not isinstance(
                reference.get("name"), str
            ):
                raise ManifestValidationError(
                    f"{channel} has malformed tool reference"
                )
            name = reference["name"]
            if name in channel_names:
                raise ManifestValidationError(
                    f"{channel} has duplicate tool reference: {name}"
                )
            channel_names.add(name)
            registered_names.add(name)
            if re.search(
                rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])",
                bundle_text,
            ) is None:
                raise ManifestValidationError(
                    f"{channel} tool reference is not documented: {name}"
                )
    validate_documented_tool_names(all_bundle_text, registered_names)


def validate_manifest(
    channel: str,
    manifest_path: Path,
    *,
    root: Path = ROOT,
) -> None:
    channels = _load_reference_contract(root)
    contract = channels[channel]
    payload = _load_json(manifest_path)
    if isinstance(payload, dict):
        if payload.get("manifest_version") != 1:
            raise ManifestValidationError(
                f"{channel}: unsupported manifest version"
            )
        declared_channel = payload.get("platform") or payload.get("channel")
        aliases = {
            "meta": "meta",
            "google": "google",
            "google_ads": "google",
            "google-ads": "google",
            "tiktok": "tiktok",
        }
        normalized_channel = aliases.get(str(declared_channel).lower())
        if declared_channel is not None and normalized_channel != channel:
            raise ManifestValidationError(
                f"{channel}: manifest declares channel {declared_channel}"
            )
    tools, gated_tools = _manifest_entries(payload)
    available_tools = _merge_entry_indexes(tools, gated_tools)
    if (
        isinstance(payload, dict)
        and isinstance(payload.get("tool_count"), int)
        and payload["tool_count"] != len(tools)
    ):
        raise ManifestValidationError(
            f"{channel}: tool_count does not match tools"
        )

    missing: list[str] = []
    gate_mismatches: list[str] = []
    capability_mismatches: list[str] = []
    for reference in contract["tools"]:
        name = reference["name"]
        expected_gates = _string_set(
            reference.get("capability_gate"),
            label=f"{name}.expected_capability_gate",
        ) | _string_set(
            reference.get("capability_gates"),
            label=f"{name}.expected_capability_gates",
        )
        expected_capabilities = _string_set(
            reference.get("required_capability"),
            label=f"{name}.expected_required_capability",
        ) | _string_set(
            reference.get("required_capabilities"),
            label=f"{name}.expected_required_capabilities",
        )
        actual = available_tools.get(name)
        if actual is None:
            missing.append(name)
            continue
        actual_gates = actual["capability_gates"]
        unproven_gates = expected_gates - actual_gates
        if unproven_gates:
            rendered = ",".join(sorted(actual_gates)) or "<absent>"
            gate_mismatches.append(
                f"{name} ({rendered} does not prove "
                f"{','.join(sorted(unproven_gates))})"
            )
        actual_capabilities = actual["required_capabilities"]
        unproven_capabilities = (
            expected_capabilities - actual_capabilities
        )
        if unproven_capabilities:
            rendered = (
                ",".join(sorted(actual_capabilities)) or "<absent>"
            )
            capability_mismatches.append(
                f"{name} ({rendered} does not prove "
                f"{','.join(sorted(unproven_capabilities))})"
            )

    if missing or gate_mismatches or capability_mismatches:
        details = []
        if missing:
            details.append("missing tools: " + ", ".join(sorted(missing)))
        if gate_mismatches:
            details.append(
                "capability gate mismatch: "
                + ", ".join(sorted(gate_mismatches))
            )
        if capability_mismatches:
            details.append(
                "required capability mismatch: "
                + ", ".join(sorted(capability_mismatches))
            )
        raise ManifestValidationError(f"{channel}: {'; '.join(details)}")


def manifest_paths_from_environment() -> dict[str, Path]:
    return {
        channel: Path(value).expanduser()
        for channel, key in ENV_KEYS.items()
        if (value := os.environ.get(key))
    }


def _load_provenance(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ManifestValidationError("unsupported manifest provenance")
    channels = payload.get("channels")
    if not isinstance(channels, dict):
        raise ManifestValidationError("manifest provenance has no channels")
    return channels


def validate_manifest_provenance(
    paths: dict[str, Path],
    provenance_path: Path = DEFAULT_PROVENANCE_PATH,
    *,
    root: Path = ROOT,
) -> None:
    provenance = _load_provenance(provenance_path)
    for channel in CHANNELS:
        entry = provenance.get(channel)
        if not isinstance(entry, dict):
            raise ManifestValidationError(
                f"provenance missing channel: {channel}"
            )
        path = paths.get(channel)
        if path is None:
            raise ManifestValidationError(
                f"manifest missing channel: {channel}"
            )
        service = entry.get("service")
        source_revision = entry.get("source_revision")
        source_path = entry.get("source_path")
        snapshot_path = entry.get("snapshot_path")
        digest = entry.get("sha256")
        if service != channel:
            raise ManifestValidationError(
                f"{channel}: invalid provenance service"
            )
        if (
            not isinstance(source_revision, str)
            or not COMMIT_RE.fullmatch(source_revision)
        ):
            raise ManifestValidationError(
                f"{channel}: invalid provenance source revision"
            )
        for label, value in (
            ("source_path", source_path),
            ("snapshot_path", snapshot_path),
        ):
            if (
                not isinstance(value, str)
                or not value
                or Path(value).is_absolute()
                or ".." in Path(value).parts
            ):
                raise ManifestValidationError(
                    f"{channel}: invalid provenance {label}"
                )
        expected_snapshot = f"contracts/manifests/{channel}.json"
        if snapshot_path != expected_snapshot:
            raise ManifestValidationError(
                f"{channel}: unexpected snapshot path {snapshot_path}"
            )
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ManifestValidationError(
                f"{channel}: invalid provenance digest"
            )
        if _sha256_file(path) != digest:
            raise ManifestValidationError(
                f"{channel}: stale snapshot digest"
            )
        payload = _load_json(path)
        if not isinstance(payload, dict):
            raise ManifestValidationError(
                f"{channel}: snapshot must be an object"
            )
        for key in ("manifest_version", "guide_version", "tool_count"):
            if payload.get(key) != entry.get(key):
                raise ManifestValidationError(
                    f"{channel}: stale provenance {key}"
                )
        try:
            relative_path = path.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        if relative_path.as_posix() != snapshot_path:
            raise ManifestValidationError(
                f"{channel}: snapshot path does not match provenance"
            )


def validate_optional_manifests(
    paths: dict[str, Path] | None = None,
    *,
    root: Path = ROOT,
    require_all: bool = False,
) -> tuple[str, ...]:
    validate_reference_contract(root)
    selected = manifest_paths_from_environment() if paths is None else paths
    messages: list[str] = []
    for channel in CHANNELS:
        path = selected.get(channel)
        if path is None:
            if require_all:
                raise ManifestValidationError(
                    f"manifest missing channel: {channel}"
                )
            messages.append(f"SKIP: {channel} public tool manifest not provided")
            continue
        validate_manifest(channel, path, root=root)
        messages.append(f"PASS: {channel} public tool manifest")
    return tuple(messages)


def validate_committed_manifests(
    *,
    root: Path = ROOT,
    paths: dict[str, Path] | None = None,
    provenance_path: Path | None = None,
) -> tuple[str, ...]:
    selected = (
        {
            channel: root / "contracts" / "manifests" / f"{channel}.json"
            for channel in CHANNELS
        }
        if paths is None
        else paths
    )
    provenance = (
        root / "contracts" / "manifests" / "provenance.json"
        if provenance_path is None
        else provenance_path
    )
    messages = validate_optional_manifests(
        selected,
        root=root,
        require_all=True,
    )
    validate_manifest_provenance(
        selected,
        provenance,
        root=root,
    )
    return messages


def _parse_manifest_args(values: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ManifestValidationError(
                "--manifest must use CHANNEL=PATH"
            )
        channel, raw_path = value.split("=", 1)
        if channel not in CHANNELS:
            raise ManifestValidationError(f"unsupported channel: {channel}")
        if channel in parsed:
            raise ManifestValidationError(
                f"duplicate manifest for channel: {channel}"
            )
        parsed[channel] = Path(raw_path).expanduser()
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        metavar="CHANNEL=PATH",
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        help="provenance lock for an explicit three-manifest set",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="developer-only compatibility mode; never use in release CI",
    )
    args = parser.parse_args()
    try:
        explicit_paths = (
            _parse_manifest_args(args.manifest)
            if args.manifest
            else manifest_paths_from_environment()
        )
        if explicit_paths:
            messages = validate_optional_manifests(
                explicit_paths,
                require_all=not args.allow_missing,
            )
            if args.provenance:
                validate_manifest_provenance(
                    explicit_paths,
                    args.provenance,
                )
        elif args.allow_missing:
            messages = validate_optional_manifests({})
        else:
            messages = validate_committed_manifests()
        for message in messages:
            print(message)
    except ManifestValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
