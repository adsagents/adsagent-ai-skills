#!/usr/bin/env python3
"""Warn when the skills drift from the services' current public tool manifests.

Each channel (meta, google, tiktok) publishes a names-only tool manifest. This
script fetches those manifests and compares them with the tools the skills
reference (contracts/public-tool-references.json). By default it only reports:
it never blocks a merge or a release. See docs/drift-check.md.

Exit codes: 0 clean or nothing to compare, 10 warnings, 1 a finding the policy
file says must block, 2 a source could not be read.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from validate_public_tool_manifests import (
        CHANNELS,
        MAX_MANIFEST_BYTES,
        ManifestValidationError,
        _load_json,
        _load_reference_contract,
        _manifest_entries,
        _merge_entry_indexes,
        load_deprecated_tools,
    )
except ModuleNotFoundError:  # Imported as scripts.check_drift.
    from scripts.validate_public_tool_manifests import (
        CHANNELS,
        MAX_MANIFEST_BYTES,
        ManifestValidationError,
        _load_json,
        _load_reference_contract,
        _manifest_entries,
        _merge_entry_indexes,
        load_deprecated_tools,
    )

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts" / "drift-policy.json"
SOURCE_ENV = {
    channel: f"ADSAGENT_DRIFT_SOURCE_{channel.upper()}" for channel in CHANNELS
}
TOKEN_ENV = "ADSAGENT_DRIFT_GITHUB_TOKEN"
FETCH_TIMEOUT_SECONDS = 20
MAX_LISTED_NAMES = 60

EXIT_CLEAN = 0
EXIT_BLOCKING = 1
EXIT_SOURCE_ERROR = 2
EXIT_WARNINGS = 10


class DriftSourceError(RuntimeError):
    """A manifest source could not be read."""


@dataclass
class ChannelReport:
    channel: str
    source: str
    guide_version: str = "unknown"
    removed: list[str] = field(default_factory=list)
    deprecated: dict[str, dict[str, str]] = field(default_factory=dict)
    unlisted_deprecations: list[str] = field(default_factory=list)
    gate_mismatches: list[str] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return bool(
            self.removed
            or self.deprecated
            or self.unlisted_deprecations
            or self.gate_mismatches
        )


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    payload = _load_json(path)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ManifestValidationError("unsupported drift policy")
    mode = payload.get("mode")
    if mode not in {"warn", "block-removed"}:
        raise ManifestValidationError(f"unknown drift policy mode: {mode!r}")
    return payload


def _read_url(url: str, headers: dict[str, str]) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise DriftSourceError("manifest sources must be https URLs")
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(  # noqa: S310 - https only, checked above
            request, timeout=FETCH_TIMEOUT_SECONDS
        ) as response:
            data = response.read(MAX_MANIFEST_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise DriftSourceError(f"could not fetch manifest: {exc}") from exc
    if len(data) > MAX_MANIFEST_BYTES:
        raise DriftSourceError("manifest exceeds size limit")
    return data


def _github_url(spec: str) -> str:
    # github:OWNER/REPO/PATH/IN/REPO@REF
    body = spec[len("github:"):]
    path, _, ref = body.partition("@")
    owner, repo, *rest = path.split("/")
    if not owner or not repo or not rest:
        raise DriftSourceError("github source must be github:OWNER/REPO/PATH[@REF]")
    quoted = "/".join(urllib.parse.quote(part) for part in rest)
    return (
        f"https://api.github.com/repos/{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(repo)}/contents/{quoted}"
        f"?ref={urllib.parse.quote(ref or 'main')}"
    )


def fetch_manifest(spec: str) -> Any:
    """Load a manifest from a local path, an https URL, or github:OWNER/REPO/PATH@REF."""
    if spec.startswith("github:"):
        token = os.environ.get(TOKEN_ENV, "")
        if not token:
            raise DriftSourceError(f"{TOKEN_ENV} is required for github sources")
        raw = _read_url(
            _github_url(spec),
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.raw",
                "User-Agent": "adsagent-skill-pack-drift-check",
            },
        )
    elif spec.startswith("https://"):
        raw = _read_url(
            spec,
            {
                "Accept": "application/json",
                "User-Agent": "adsagent-skill-pack-drift-check",
            },
        )
    else:
        path = Path(spec).expanduser()
        if not path.is_file():
            raise DriftSourceError(f"manifest does not exist: {path}")
        raw = path.read_bytes()
        if len(raw) > MAX_MANIFEST_BYTES:
            raise DriftSourceError("manifest exceeds size limit")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DriftSourceError(f"manifest is not valid JSON: {exc}") from exc


def _deprecations(payload: dict[str, Any]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    sections = [payload.get("call_only_tools") or [], payload.get("tools") or []]
    for section in sections:
        if not isinstance(section, list):
            continue
        for entry in section:
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
                continue
            if section is sections[0] or entry.get("deprecated_since") or entry.get(
                "deprecated"
            ):
                found[entry["name"]] = {
                    key: str(entry[key])
                    for key in ("deprecated_since", "remove_after", "replacement")
                    if entry.get(key)
                }
    return found


def compare_channel(
    channel: str,
    payload: Any,
    *,
    source: str,
    root: Path = ROOT,
) -> ChannelReport:
    """Compare one channel's manifest with the tools the skills reference."""
    contract = _load_reference_contract(root)[channel]
    report = ChannelReport(channel=channel, source=source)
    if isinstance(payload, dict):
        report.guide_version = str(payload.get("guide_version", "unknown"))
    tools, gated = _manifest_entries(payload)
    available = _merge_entry_indexes(tools, gated)
    deprecations = _deprecations(payload)
    known_deprecated = load_deprecated_tools(root)

    referenced = {reference["name"]: reference for reference in contract["tools"]}
    for name, reference in sorted(referenced.items()):
        actual = available.get(name)
        if actual is None:
            report.removed.append(name)
            continue
        if name in deprecations:
            report.deprecated[name] = deprecations[name]
        expected_capabilities = set()
        for key in ("required_capability", "required_capabilities"):
            value = reference.get(key)
            expected_capabilities |= (
                {value} if isinstance(value, str) else set(value or [])
            )
        unproven = expected_capabilities - actual["required_capabilities"]
        if unproven:
            report.gate_mismatches.append(
                f"{name} (does not prove {', '.join(sorted(unproven))})"
            )
    report.unlisted_deprecations = sorted(
        name
        for name in deprecations
        if name not in known_deprecated and name not in referenced
    )
    # Confirmation tools are reached through the prepare result's next_action,
    # so a skill is not expected to name them.
    report.uncovered = sorted(
        name
        for name in set(tools) - set(referenced)
        if not name.endswith(("_confirm", "_deny"))
    )
    return report


def render_report(
    reports: list[ChannelReport],
    skipped: list[str],
    *,
    mode: str,
) -> str:
    lines = [
        "# Skill pack drift report",
        "",
        f"Policy mode: `{mode}`. This report is advisory unless the policy says "
        "otherwise; it never blocks a merge or release in `warn` mode.",
        "",
    ]
    for report in reports:
        lines.append(f"## {report.channel} (guide `{report.guide_version}`)")
        lines.append("")
        if not report.has_warnings:
            lines.append("No drift in the tools the skills reference.")
        if report.removed:
            lines.append(
                "- **Removed** (skills still reference tools the service no "
                "longer lists): " + ", ".join(f"`{name}`" for name in report.removed)
            )
        for name, info in sorted(report.deprecated.items()):
            detail = ", ".join(f"{key}={value}" for key, value in sorted(info.items()))
            lines.append(
                f"- **Deprecated** tool still referenced: `{name}`"
                + (f" ({detail})" if detail else "")
            )
        if report.unlisted_deprecations:
            lines.append(
                "- Newly deprecated by the service, not yet in "
                "`contracts/deprecated-tools.json`: "
                + ", ".join(f"`{name}`" for name in report.unlisted_deprecations)
            )
        if report.gate_mismatches:
            lines.append(
                "- Capability no longer proven: " + "; ".join(report.gate_mismatches)
            )
        if report.uncovered:
            shown = report.uncovered[:MAX_LISTED_NAMES]
            extra = len(report.uncovered) - len(shown)
            lines.append(
                f"- Info: {len(report.uncovered)} service tools are not referenced "
                "by any skill (decide per tool whether a skill should cover it): "
                + ", ".join(f"`{name}`" for name in shown)
                + (f" and {extra} more" if extra > 0 else "")
            )
        lines.append("")
    if skipped:
        lines.append(
            "Not compared (no source configured): " + ", ".join(sorted(skipped))
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run(
    sources: dict[str, str],
    *,
    root: Path = ROOT,
    policy: dict[str, Any] | None = None,
) -> tuple[int, str]:
    policy = policy or load_policy(root / "contracts" / "drift-policy.json")
    mode = policy["mode"]
    reports: list[ChannelReport] = []
    skipped: list[str] = []
    for channel in CHANNELS:
        spec = sources.get(channel)
        if not spec:
            skipped.append(channel)
            continue
        label = "local file" if not spec.startswith(("https://", "github:")) else "published manifest"
        payload = fetch_manifest(spec)
        reports.append(compare_channel(channel, payload, source=label, root=root))
    text = render_report(reports, skipped, mode=mode)
    if mode == "block-removed" and any(report.removed for report in reports):
        return EXIT_BLOCKING, text
    if any(report.has_warnings for report in reports):
        return EXIT_WARNINGS, text
    return EXIT_CLEAN, text


def sources_from_environment() -> dict[str, str]:
    return {
        channel: value.strip()
        for channel, key in SOURCE_ENV.items()
        if (value := os.environ.get(key, "").strip())
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="CHANNEL=PATH_OR_URL",
        help=(
            "manifest for one channel; overrides "
            + ", ".join(SOURCE_ENV.values())
        ),
    )
    parser.add_argument("--report", type=Path, help="write the markdown report here")
    args = parser.parse_args(argv)

    sources = sources_from_environment()
    for item in args.source:
        channel, _, spec = item.partition("=")
        if channel not in CHANNELS or not spec:
            print(f"FAIL: --source must be CHANNEL=PATH_OR_URL: {item}", file=sys.stderr)
            return EXIT_SOURCE_ERROR
        sources[channel] = spec

    try:
        code, text = run(sources)
    except (DriftSourceError, ManifestValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return EXIT_SOURCE_ERROR
    print(text)
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    if not sources:
        print("SKIP: no manifest source configured; nothing was compared.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
