#!/usr/bin/env python3
"""Pin committed tri-channel service manifests into the public Skill Pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from validate_public_tool_manifests import (
        CHANNELS,
        ManifestValidationError,
        validate_manifest,
    )
except ModuleNotFoundError:  # Imported as scripts.sync_public_tool_manifests.
    from scripts.validate_public_tool_manifests import (
        CHANNELS,
        ManifestValidationError,
        validate_manifest,
    )


ROOT = Path(__file__).resolve().parents[1]
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ManifestSyncError(RuntimeError):
    """Raised when a source is not an immutable committed manifest."""


def _git(repo: Path, *args: str) -> bytes:
    process = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise ManifestSyncError(
            f"git {' '.join(args)} failed in {repo}: {detail}"
        )
    return process.stdout


def _source_provenance(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    repo = Path(
        _git(resolved.parent, "rev-parse", "--show-toplevel")
        .decode("utf-8")
        .strip()
    ).resolve()
    try:
        relative = resolved.relative_to(repo)
    except ValueError as exc:
        raise ManifestSyncError(f"source is outside its git repo: {path}") from exc
    relative_text = relative.as_posix()
    _git(repo, "cat-file", "-e", f"HEAD:{relative_text}")
    status = _git(
        repo,
        "status",
        "--porcelain",
        "--untracked-files=all",
    ).decode("utf-8")
    if status.strip():
        raise ManifestSyncError(
            f"source repository is not committed and clean: {repo}"
        )
    committed = _git(repo, "show", f"HEAD:{relative_text}")
    current = resolved.read_bytes()
    if committed != current:
        raise ManifestSyncError(
            f"source manifest differs from HEAD: {path}"
        )
    commit = _git(repo, "rev-parse", "HEAD").decode("utf-8").strip()
    if not COMMIT_RE.fullmatch(commit):
        raise ManifestSyncError(f"invalid source commit for {path}")
    return {
        "source_revision": commit,
        "source_path": relative_text,
        "bytes": current,
    }


def _parse_sources(values: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ManifestSyncError("--source must use CHANNEL=PATH")
        channel, raw_path = value.split("=", 1)
        if channel not in CHANNELS:
            raise ManifestSyncError(f"unsupported channel: {channel}")
        if channel in parsed:
            raise ManifestSyncError(f"duplicate source for channel: {channel}")
        parsed[channel] = Path(raw_path).expanduser()
    missing = [channel for channel in CHANNELS if channel not in parsed]
    if missing:
        raise ManifestSyncError(
            "all three committed source manifests are required: "
            + ", ".join(missing)
        )
    return parsed


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def sync_manifests(
    sources: dict[str, Path],
    *,
    destination_root: Path = ROOT,
    contract_root: Path = ROOT,
) -> dict[str, Any]:
    target_dir = destination_root / "contracts" / "manifests"
    prepared: dict[str, tuple[bytes, dict[str, Any], dict[str, Any]]] = {}
    for channel in CHANNELS:
        source = sources[channel]
        try:
            validate_manifest(channel, source, root=contract_root)
        except ManifestValidationError as exc:
            raise ManifestSyncError(
                f"{channel} source does not satisfy the Skill Pack: {exc}"
            ) from exc
        provenance = _source_provenance(source)
        try:
            manifest = json.loads(provenance["bytes"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ManifestSyncError(
                f"{channel} source is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(manifest, dict):
            raise ManifestSyncError(
                f"{channel} source manifest must be an object"
            )
        prepared[channel] = (
            provenance.pop("bytes"),
            provenance,
            manifest,
        )

    lock_channels: dict[str, Any] = {}
    for channel in CHANNELS:
        payload, source_info, manifest = prepared[channel]
        snapshot_relative = f"contracts/manifests/{channel}.json"
        lock_channels[channel] = {
            "service": channel,
            **source_info,
            "snapshot_path": snapshot_relative,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "manifest_version": manifest.get("manifest_version"),
            "guide_version": manifest.get("guide_version"),
            "tool_count": manifest.get("tool_count"),
        }

    provenance_payload = (
        json.dumps(
            {
                "schema_version": 1,
                "channels": lock_channels,
            },
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    for channel in CHANNELS:
        _write_atomic(target_dir / f"{channel}.json", prepared[channel][0])
    _write_atomic(target_dir / "provenance.json", provenance_payload)
    return {
        "schema_version": 1,
        "channels": lock_channels,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        metavar="CHANNEL=PATH",
    )
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=ROOT,
    )
    args = parser.parse_args()
    try:
        sources = _parse_sources(args.source)
        result = sync_manifests(
            sources,
            destination_root=args.destination_root.resolve(),
        )
    except (ManifestSyncError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    for channel in CHANNELS:
        entry = result["channels"][channel]
        print(
            f"PINNED: {channel}@{entry['source_revision']} "
            f"({entry['tool_count']} tools)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
