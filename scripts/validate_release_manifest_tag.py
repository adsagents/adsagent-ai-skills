#!/usr/bin/env python3
"""Fail when release-manifest.json references a tag that is not published yet.

Release order is: tag the release commit and create the GitHub release
first, then update ``release-manifest.json`` (and ``VERSION``) on main.
Sync clients read the manifest from main and then fetch the tagged
manifest, so pointing main at an unpublished tag turns every sync run
into a 404 until the tag lands.

"Published" is checked against the remote, never local state: origin
must advertise the tag, the tagged tree's own ``VERSION`` and
``release-manifest.json`` must name this version and tag, and the
GitHub release behind ``release_url`` must exist.
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FETCH_TIMEOUT_SECONDS = 20


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


def git_remote_tag_exists(tag: str, *, root: Path = ROOT) -> bool:
    """True only when origin advertises the tag.

    A local tag is not published: sync clients fetch from origin and
    still get a 404 until the tag is pushed.
    """
    remote = _git(root, "ls-remote", "--exit-code", "origin", f"refs/tags/{tag}")
    return remote.returncode == 0


def git_tagged_release_files(
    tag: str, *, root: Path = ROOT
) -> tuple[str, dict] | None:
    """Read ``VERSION`` and ``release-manifest.json`` from the tag on origin.

    Returns ``None`` when the tag cannot be fetched or either file is
    missing or unreadable in the tagged tree. Fetching the tag (rather
    than trusting a local copy, which may point elsewhere) proves the
    object clients will receive actually carries this release.
    """
    fetch = _git(root, "fetch", "--quiet", "--depth", "1", "origin", f"refs/tags/{tag}")
    if fetch.returncode != 0:
        return None
    version_file = _git(root, "show", "FETCH_HEAD:VERSION")
    manifest_file = _git(root, "show", "FETCH_HEAD:release-manifest.json")
    if version_file.returncode != 0 or manifest_file.returncode != 0:
        return None
    try:
        manifest = json.loads(manifest_file.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(manifest, dict):
        return None
    return version_file.stdout.strip(), manifest


def github_release_exists(release_url: str) -> bool:
    """True when the GitHub release page behind ``release_url`` resolves.

    Only a 404 proves the release is missing (a pushed tag without a
    release, or a draft, both 404 anonymously); any other HTTP or
    network error raises ``OSError`` so callers report "could not run"
    instead of a false "not published".
    """
    parsed = urllib.parse.urlparse(release_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("release_url must be an https URL")
    request = urllib.request.Request(
        release_url,
        method="HEAD",
        headers={"User-Agent": "adsagent-skill-pack-release-manifest-check"},
    )
    try:
        with urllib.request.urlopen(  # noqa: S310 - https only, checked above
            request, timeout=FETCH_TIMEOUT_SECONDS
        ):
            return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise OSError(f"release check returned HTTP {exc.code}") from exc


def validate_release_manifest_tag(
    root: Path,
    *,
    remote_tag_exists: Callable[[str], bool] | None = None,
    tagged_files: Callable[[str], tuple[str, dict] | None] | None = None,
    release_exists: Callable[[str], bool] | None = None,
) -> str:
    if remote_tag_exists is None:
        remote_tag_exists = lambda tag: git_remote_tag_exists(tag, root=root)  # noqa: E731
    if tagged_files is None:
        tagged_files = lambda tag: git_tagged_release_files(tag, root=root)  # noqa: E731
    if release_exists is None:
        release_exists = github_release_exists

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
    release_url = manifest.get("release_url")
    expected_release_url = (
        f"https://github.com/{manifest.get('repository')}/releases/tag/{tag}"
    )
    if release_url != expected_release_url:
        raise ManifestTagError(
            f"release-manifest.json release_url does not match the tag "
            f"(expected {expected_release_url}, found {release_url})"
        )
    if not remote_tag_exists(tag):
        raise ManifestTagError(
            f"release tag {tag} is not published on origin yet; push the "
            "git tag and create the GitHub release before pointing "
            "release-manifest.json at it"
        )
    tagged = tagged_files(tag)
    if tagged is None:
        raise ManifestTagError(
            f"release tag {tag} does not contain a readable VERSION and "
            "release-manifest.json on origin"
        )
    tagged_version, tagged_manifest = tagged
    if (
        tagged_version != version
        or tagged_manifest.get("version") != version
        or tagged_manifest.get("tag") != tag
    ):
        raise ManifestTagError(
            f"release tag {tag} contains a different release "
            f"(expected version={version} tag={tag}, found "
            f"VERSION={tagged_version} "
            f"manifest version={tagged_manifest.get('version')} "
            f"tag={tagged_manifest.get('tag')}); the tag must point at "
            "the commit that carries this version"
        )
    if not release_exists(release_url):
        raise ManifestTagError(
            f"release tag {tag} has no published GitHub release yet; "
            f"create the release so {release_url} resolves before "
            "pointing release-manifest.json at it"
        )
    return tag


def main() -> int:
    try:
        tag = validate_release_manifest_tag(ROOT)
    except ManifestTagError as exc:
        print(f"release-manifest tag check failed: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"release-manifest tag check could not run: {exc}", file=sys.stderr)
        return 2
    print(f"release-manifest tag {tag} is published")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
