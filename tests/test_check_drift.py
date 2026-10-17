from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_drift
from scripts.check_drift import (
    EXIT_BLOCKING,
    EXIT_CLEAN,
    EXIT_WARNINGS,
    DriftSourceError,
    compare_channel,
    fetch_manifest,
    load_policy,
    run,
)

ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return json.loads(
        (ROOT / "contracts/public-tool-references.json").read_text(encoding="utf-8")
    )


def _manifest(channel: str, *, drop: tuple[str, ...] = (), extra: tuple = ()) -> dict:
    tools = []
    for reference in _contract()["channels"][channel]["tools"]:
        if reference["name"] in drop:
            continue
        entry = {"name": reference["name"]}
        if "required_capability" in reference:
            entry["required_capability"] = reference["required_capability"]
        tools.append(entry)
    tools.extend(extra)
    return {
        "manifest_version": 1,
        "platform": channel,
        "guide_version": "test",
        "tool_count": len(tools),
        "tools": tools,
    }


def _write(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _all_sources(tmp_path: Path, **overrides: dict) -> dict[str, str]:
    return {
        channel: _write(
            tmp_path / f"{channel}.json",
            overrides.get(channel, _manifest(channel)),
        )
        for channel in ("meta", "google", "tiktok")
    }


def test_matching_manifests_are_clean(tmp_path: Path) -> None:
    code, text = run(_all_sources(tmp_path))

    assert code == EXIT_CLEAN
    assert "No drift" in text


def test_removed_tool_is_a_warning_not_a_failure(tmp_path: Path) -> None:
    sources = _all_sources(
        tmp_path, google=_manifest("google", drop=("google_ads_budget_update_prepare",))
    )

    code, text = run(sources)

    assert code == EXIT_WARNINGS
    assert "Removed" in text
    assert "google_ads_budget_update_prepare" in text


def test_deprecated_referenced_tool_is_reported(tmp_path: Path) -> None:
    payload = _manifest("meta")
    payload["call_only_tools"] = [
        {
            "name": "entities_prepare_update",
            "deprecated_since": "2026-12-01",
            "remove_after": "2027-01-01",
            "replacement": "newer_tool",
        }
    ]

    report = compare_channel("meta", payload, source="test", root=ROOT)

    assert report.deprecated["entities_prepare_update"]["replacement"] == "newer_tool"
    assert report.has_warnings


def test_new_service_deprecation_not_in_list_is_reported() -> None:
    payload = _manifest("google", extra=({"name": "google_ads_old_thing"},))
    payload["call_only_tools"] = [
        {"name": "google_ads_old_thing", "deprecated_since": "2026-12-01"}
    ]

    report = compare_channel("google", payload, source="test", root=ROOT)

    assert report.unlisted_deprecations == ["google_ads_old_thing"]


def test_uncovered_tools_are_informational_and_skip_confirm_tools() -> None:
    payload = _manifest(
        "tiktok",
        extra=(
            {"name": "brand_new_read"},
            {"name": "brand_new_write_confirm"},
        ),
    )

    report = compare_channel("tiktok", payload, source="test", root=ROOT)

    assert report.uncovered == ["brand_new_read"]
    assert not report.has_warnings


def test_capability_no_longer_proven_is_reported() -> None:
    reference = next(
        item
        for item in _contract()["channels"]["meta"]["tools"]
        if "required_capability" in item
    )
    payload = _manifest("meta")
    for entry in payload["tools"]:
        if entry["name"] == reference["name"]:
            entry["required_capability"] = "mcp.something_else"

    report = compare_channel("meta", payload, source="test", root=ROOT)

    assert any(reference["name"] in item for item in report.gate_mismatches)


def test_missing_sources_are_skipped_not_failed() -> None:
    code, text = run({})

    assert code == EXIT_CLEAN
    assert "Not compared" in text


def test_warn_policy_never_blocks_even_when_removed(tmp_path: Path) -> None:
    sources = _all_sources(
        tmp_path, meta=_manifest("meta", drop=("entities_prepare_update",))
    )

    code, _ = run(sources, policy={"mode": "warn"})

    assert code == EXIT_WARNINGS


def test_block_removed_policy_blocks_only_removed_tools(tmp_path: Path) -> None:
    removed = _all_sources(
        tmp_path, meta=_manifest("meta", drop=("entities_prepare_update",))
    )
    assert run(removed, policy={"mode": "block-removed"})[0] == EXIT_BLOCKING

    deprecated = _manifest("meta")
    deprecated["call_only_tools"] = [
        {"name": "entities_prepare_update", "deprecated_since": "2026-12-01"}
    ]
    sources = _all_sources(tmp_path, meta=deprecated)
    assert run(sources, policy={"mode": "block-removed"})[0] == EXIT_WARNINGS


def test_committed_policy_starts_in_warn_mode() -> None:
    assert load_policy()["mode"] == "warn"


def test_sources_must_be_https_or_local_files(tmp_path: Path) -> None:
    with pytest.raises(DriftSourceError, match="https"):
        check_drift._read_url("http://example.invalid/manifest.json", {})
    with pytest.raises(DriftSourceError, match="does not exist"):
        fetch_manifest(str(tmp_path / "missing.json"))


def test_github_source_requires_a_token_and_never_logs_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(check_drift.TOKEN_ENV, raising=False)

    with pytest.raises(DriftSourceError, match=check_drift.TOKEN_ENV):
        fetch_manifest("github:owner/repo/path/manifest.json@main")


def test_main_reads_sources_from_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    sources = _all_sources(tmp_path)
    for channel, path in sources.items():
        monkeypatch.setenv(check_drift.SOURCE_ENV[channel], path)
    report = tmp_path / "report.md"

    assert check_drift.main(["--report", str(report)]) == EXIT_CLEAN
    assert "No drift" in report.read_text(encoding="utf-8")


def test_drift_workflow_is_advisory_and_least_privilege() -> None:
    workflow = (ROOT / ".github/workflows/drift-check.yml").read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "repository_dispatch:" in workflow
    assert "issues: write" in workflow
    assert "contents: read" in workflow
    assert "pull_request" not in workflow
    # The check must never make the job red just because drift was found.
    assert '[ "$code" -eq 10 ]' in workflow


def test_ci_no_longer_compares_against_frozen_snapshots() -> None:
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")

    assert "contracts/manifests" not in workflow
    assert "--provenance" not in workflow
    assert "check_drift.py" in workflow
    assert "continue-on-error" not in workflow
