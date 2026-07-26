from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.sync_public_tool_manifests import (
    ManifestSyncError,
    sync_manifests,
)
from scripts.validate_public_tool_manifests import CHANNELS


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "contracts" / "manifests"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _service_sources(tmp_path: Path) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for channel in CHANNELS:
        repo = tmp_path / f"{channel}-service"
        source = repo / "docs" / "mcp" / "manifests" / f"{channel}-tools.json"
        source.parent.mkdir(parents=True)
        source.write_bytes((MANIFEST_DIR / f"{channel}.json").read_bytes())
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "ci@example.invalid")
        _git(repo, "config", "user.name", "Manifest CI")
        _git(
            repo,
            "remote",
            "add",
            "origin",
            f"https://github.com/example/{channel}-service.git",
        )
        _git(repo, "add", source.relative_to(repo).as_posix())
        _git(repo, "commit", "-qm", "Publish public tool manifest")
        sources[channel] = source
    return sources


def test_sync_is_offline_deterministic_and_copies_committed_bytes(
    tmp_path: Path,
) -> None:
    sources = _service_sources(tmp_path)
    output = tmp_path / "output"

    first = sync_manifests(
        sources,
        destination_root=output,
        contract_root=ROOT,
    )
    first_bytes = {
        path.name: path.read_bytes()
        for path in (output / "contracts" / "manifests").iterdir()
    }
    second = sync_manifests(
        sources,
        destination_root=output,
        contract_root=ROOT,
    )
    second_bytes = {
        path.name: path.read_bytes()
        for path in (output / "contracts" / "manifests").iterdir()
    }

    assert first == second
    assert first_bytes == second_bytes
    for channel in CHANNELS:
        assert (
            first_bytes[f"{channel}.json"]
            == (MANIFEST_DIR / f"{channel}.json").read_bytes()
        )
        assert first["channels"][channel]["service"] == channel
        assert len(first["channels"][channel]["source_revision"]) == 40


def test_sync_rejects_a_dirty_service_repository(tmp_path: Path) -> None:
    sources = _service_sources(tmp_path)
    sources["meta"].parent.joinpath("unfinished.txt").write_text(
        "not committed\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ManifestSyncError,
        match="source repository is not committed and clean",
    ):
        sync_manifests(
            sources,
            destination_root=tmp_path / "output",
            contract_root=ROOT,
        )
