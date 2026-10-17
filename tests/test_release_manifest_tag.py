"""The release manifest on main must reference an already-published tag.

Sync clients fetch the tagged manifest by tag; pointing main at an
unpublished tag makes every sync run fail with 404 until the tag lands.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_release_manifest_tag import (
    ManifestTagError,
    validate_release_manifest_tag,
)

ROOT = Path(__file__).resolve().parents[1]


def _write(root: Path, *, version: str, tag: str) -> None:
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (root / "release-manifest.json").write_text(
        json.dumps({
            "schema_version": 1,
            "package": "adsagent-ai-skills",
            "repository": "adsagents/adsagent-ai-skills",
            "version": version,
            "tag": tag,
            "release_url": f"https://github.com/adsagents/adsagent-ai-skills/releases/tag/{tag}",
        }),
        encoding="utf-8",
    )


def test_existing_tag_passes(tmp_path):
    _write(tmp_path, version="0.7.76", tag="v0.7.76")
    assert validate_release_manifest_tag(tmp_path, tag_exists=lambda tag: True) == "v0.7.76"


def test_missing_tag_fails(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    with pytest.raises(ManifestTagError, match="not published"):
        validate_release_manifest_tag(tmp_path, tag_exists=lambda tag: False)


def test_version_tag_mismatch_fails_before_lookup(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.76")
    with pytest.raises(ManifestTagError, match="does not match"):
        validate_release_manifest_tag(
            tmp_path,
            tag_exists=lambda tag: pytest.fail("tag lookup must not run"),
        )


def test_repository_manifest_tag_is_published():
    # Integration guard against the live checkout: whichever tag main
    # currently references must resolve in this clone or on origin.
    from scripts.validate_release_manifest_tag import git_tag_exists

    assert validate_release_manifest_tag(ROOT, tag_exists=git_tag_exists)
