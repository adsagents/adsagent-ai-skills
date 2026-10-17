#!/usr/bin/env python3
"""Fail when release-manifest.json references a tag that is not published yet.

Release order is: tag the release commit and create the GitHub release
first, then update ``release-manifest.json`` (and ``VERSION``) on main.
Sync clients read the manifest from main and then fetch the tagged
manifest, so pointing main at an unpublished tag turns every sync run
into a 404 until the tag lands.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ManifestTagError(RuntimeError):
    pass


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def git_tag_exists(tag: str, *, root: Path = ROOT) -> bool:
    """Resolve a tag locally, then on origin (CI checkouts are shallow)."""
    local = _git(root, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
    if local.returncode == 0:
        return True
    remote = _git(root, "ls-remote", "--exit-code", "origin", f"refs/tags/{tag}")
    return remote.returncode == 0


def validate_release_manifest_tag(
    root: Path,
    *,
    tag_exists: Callable[[str], bool],
) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    manifest = json.loads(
        (root / "release-manifest.json").read_text(encoding="utf-8")
    )
    tag = manifest.get("tag")
    expected = f"v{version}"
    if manifest.get("version") != version or tag != expected:
        raise ManifestTagError(
            f"release-manifest.json version/tag does not match VERSION "
            f"(expected version={version} tag={expected}, "
            f"found version={manifest.get('version')} tag={tag})"
        )
    if not tag_exists(tag):
        raise ManifestTagError(
            f"release tag {tag} is not published yet; create the git tag "
            "and GitHub release before pointing release-manifest.json at it"
        )
    return tag


def main() -> int:
    try:
        tag = validate_release_manifest_tag(ROOT, tag_exists=git_tag_exists)
    except ManifestTagError as exc:
        print(f"release-manifest tag check failed: {exc}", file=sys.stderr)
        return 1
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"release-manifest tag check could not run: {exc}", file=sys.stderr)
        return 2
    print(f"release-manifest tag {tag} is published")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
