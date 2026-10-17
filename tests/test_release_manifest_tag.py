"""The release manifest on main must reference an already-published tag.

Sync clients fetch the tagged manifest by tag; pointing main at an
unpublished tag makes every sync run fail with 404 until the tag lands.
"Published" means all three hold on the remote, not just locally:

- origin advertises the tag (an unpushed local tag does not count);
- the tagged tree itself carries this version (its ``VERSION`` and its
  own ``release-manifest.json`` agree with the tag);
- a GitHub release exists for the tag, so ``release_url`` resolves.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import scripts.validate_release_manifest_tag as tag_module
from scripts.validate_release_manifest_tag import (
    ManifestTagError,
    git_remote_tag_exists,
    git_tagged_release_files,
    github_release_exists,
    validate_release_manifest_tag,
)

ROOT = Path(__file__).resolve().parents[1]

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        env=_GIT_ENV,
        capture_output=True,
        text=True,
    )


def _manifest(version: str, tag: str) -> dict:
    return {
        "schema_version": 1,
        "package": "adsagent-ai-skills",
        "repository": "adsagents/adsagent-ai-skills",
        "version": version,
        "tag": tag,
        "release_url": f"https://github.com/adsagents/adsagent-ai-skills/releases/tag/{tag}",
    }


def _write(root: Path, *, version: str, tag: str, release_url: str | None = None) -> None:
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    manifest = _manifest(version, tag)
    if release_url is not None:
        manifest["release_url"] = release_url
    (root / "release-manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def _fakes(*, version: str = "0.7.76", remote=True, tagged="same", release=True):
    """Keyword fakes for validate_release_manifest_tag; override one leg per test."""
    if tagged == "same":
        tagged = (version, _manifest(version, f"v{version}"))
    return {
        "remote_tag_exists": lambda tag: remote,
        "tagged_files": lambda tag: tagged,
        "release_exists": lambda release_url: release,
    }


def _must_not_run(name: str):
    def fake(arg):
        pytest.fail(f"{name} must not run")

    return fake


def test_published_tag_with_matching_contents_and_release_passes(tmp_path):
    _write(tmp_path, version="0.7.76", tag="v0.7.76")
    assert validate_release_manifest_tag(tmp_path, **_fakes()) == "v0.7.76"


def test_tag_missing_on_origin_fails_before_content_and_release_checks(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    with pytest.raises(ManifestTagError, match="not published"):
        validate_release_manifest_tag(
            tmp_path,
            remote_tag_exists=lambda tag: False,
            tagged_files=_must_not_run("tagged_files"),
            release_exists=_must_not_run("release_exists"),
        )


def test_tag_pointing_at_previous_version_fails(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    tagged = ("0.7.76", _manifest("0.7.76", "v0.7.76"))
    with pytest.raises(ManifestTagError, match="contains"):
        validate_release_manifest_tag(
            tmp_path, **_fakes(version="0.7.77", tagged=tagged)
        )


def test_tag_whose_manifest_names_another_tag_fails(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    tagged = ("0.7.77", _manifest("0.7.77", "v0.7.76"))
    with pytest.raises(ManifestTagError, match="contains"):
        validate_release_manifest_tag(
            tmp_path, **_fakes(version="0.7.77", tagged=tagged)
        )


def test_unreadable_tagged_files_fail(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    with pytest.raises(ManifestTagError, match="does not contain"):
        validate_release_manifest_tag(
            tmp_path, **_fakes(version="0.7.77", tagged=None)
        )


def test_missing_github_release_fails(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.77")
    with pytest.raises(ManifestTagError, match="GitHub release"):
        validate_release_manifest_tag(
            tmp_path, **_fakes(version="0.7.77", release=False)
        )


def test_version_tag_mismatch_fails_before_lookup(tmp_path):
    _write(tmp_path, version="0.7.77", tag="v0.7.76")
    with pytest.raises(ManifestTagError, match="does not match"):
        validate_release_manifest_tag(
            tmp_path,
            remote_tag_exists=_must_not_run("remote_tag_exists"),
            tagged_files=_must_not_run("tagged_files"),
            release_exists=_must_not_run("release_exists"),
        )


def test_release_url_mismatch_fails_before_lookup(tmp_path):
    _write(
        tmp_path,
        version="0.7.77",
        tag="v0.7.77",
        release_url="https://example.invalid/releases/tag/v0.7.77",
    )
    with pytest.raises(ManifestTagError, match="release_url"):
        validate_release_manifest_tag(
            tmp_path,
            remote_tag_exists=_must_not_run("remote_tag_exists"),
            tagged_files=_must_not_run("tagged_files"),
            release_exists=_must_not_run("release_exists"),
        )


def test_git_remote_tag_exists_ignores_local_only_tag(tmp_path):
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    (work / "VERSION").write_text("0.7.77\n", encoding="utf-8")
    _git(work, "add", "VERSION")
    _git(work, "commit", "-qm", "x")
    _git(work, "remote", "add", "origin", str(origin))
    _git(work, "tag", "v0.7.77")

    assert git_remote_tag_exists("v0.7.77", root=work) is False
    _git(work, "push", "-q", "origin", "v0.7.77")
    assert git_remote_tag_exists("v0.7.77", root=work) is True


def test_git_tagged_release_files_reads_origin_tag_without_local_tag(tmp_path):
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    reader = tmp_path / "reader"
    subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    _write(work, version="0.7.77", tag="v0.7.77")
    _git(work, "add", "VERSION", "release-manifest.json")
    _git(work, "commit", "-qm", "x")
    _git(work, "remote", "add", "origin", str(origin))
    _git(work, "tag", "v0.7.77")
    _git(work, "push", "-q", "origin", "v0.7.77")
    subprocess.run(["git", "init", "-q", str(reader)], check=True)
    _git(reader, "remote", "add", "origin", str(origin))

    tagged = git_tagged_release_files("v0.7.77", root=reader)
    assert tagged is not None
    version, manifest = tagged
    assert version == "0.7.77"
    assert manifest["version"] == "0.7.77"
    assert manifest["tag"] == "v0.7.77"
    assert git_tagged_release_files("v9.9.9", root=reader) is None


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_github_release_exists_status_classification(monkeypatch):
    url = "https://github.com/adsagents/adsagent-ai-skills/releases/tag/v0.7.76"

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda request, timeout: _FakeResponse()
    )
    assert github_release_exists(url) is True

    def raise_http(code):
        def fake(request, timeout):
            raise urllib.error.HTTPError(url, code, "x", hdrs=None, fp=None)

        return fake

    monkeypatch.setattr(urllib.request, "urlopen", raise_http(404))
    assert github_release_exists(url) is False

    monkeypatch.setattr(urllib.request, "urlopen", raise_http(500))
    with pytest.raises(OSError):
        github_release_exists(url)

    monkeypatch.setattr(tag_module.urllib.request, "urlopen", raise_http(404))
    with pytest.raises(ValueError, match="https"):
        github_release_exists("http://github.com/x/releases/tag/v1")


def test_repository_manifest_tag_is_published():
    # Integration guard against the live checkout: whichever tag main
    # currently references must resolve on origin, carry this version,
    # and have a GitHub release.
    assert validate_release_manifest_tag(ROOT)
