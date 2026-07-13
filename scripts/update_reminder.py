#!/usr/bin/env python3
"""Evaluate the bounded AdsAgent skill-pack reminder policy."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_CACHE_KEYS = {
    "checked_at",
    "installed_version",
    "recommended_version",
    "reminded_for_version",
}
_SESSION_REMINDERS: set[str] = set()
_MAX_CACHE_BYTES = 4096


def _parse_semver(value: str) -> tuple[int, int, int, tuple[int | str, ...] | None]:
    if not isinstance(value, str):
        raise ValueError("version must be a string")
    match = _SEMVER_RE.fullmatch(value)
    if match is None:
        raise ValueError("version is not strict semantic versioning")
    prerelease_text = match.group(4)
    prerelease: tuple[int | str, ...] | None = None
    if prerelease_text is not None:
        parsed: list[int | str] = []
        for identifier in prerelease_text.split("."):
            if identifier.isdigit():
                if len(identifier) > 1 and identifier.startswith("0"):
                    raise ValueError("numeric prerelease identifier has a leading zero")
                parsed.append(int(identifier))
            else:
                parsed.append(identifier)
        prerelease = tuple(parsed)
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), prerelease


def compare_semver(left: str, right: str) -> int:
    """Return -1, 0, or 1 using SemVer precedence."""
    left_major, left_minor, left_patch, left_pre = _parse_semver(left)
    right_major, right_minor, right_patch, right_pre = _parse_semver(right)
    left_core = (left_major, left_minor, left_patch)
    right_core = (right_major, right_minor, right_patch)
    if left_core != right_core:
        return 1 if left_core > right_core else -1
    if left_pre is None or right_pre is None:
        if left_pre is right_pre:
            return 0
        return 1 if left_pre is None else -1
    for left_item, right_item in zip(left_pre, right_pre):
        if left_item == right_item:
            continue
        left_numeric = isinstance(left_item, int)
        right_numeric = isinstance(right_item, int)
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return 1 if left_item > right_item else -1
    if len(left_pre) == len(right_pre):
        return 0
    return 1 if len(left_pre) > len(right_pre) else -1


def classify_versions(
    installed_version: str,
    recommended_version: str,
    minimum_safe_version: str,
) -> str:
    try:
        if compare_semver(minimum_safe_version, recommended_version) > 0:
            return "unknown"
        installed_vs_recommended = compare_semver(
            installed_version,
            recommended_version,
        )
        installed_vs_minimum = compare_semver(
            installed_version,
            minimum_safe_version,
        )
    except (TypeError, ValueError):
        return "unknown"
    if installed_vs_recommended >= 0:
        return "up_to_date"
    if installed_vs_minimum >= 0:
        return "update_available"
    return "below_minimum"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _cache_path() -> Path:
    cache_root = os.environ.get("XDG_CACHE_HOME")
    base = Path(cache_root).expanduser() if cache_root else Path.home() / ".cache"
    return base / "adsagent-ai-skills" / "update-reminder-v1.json"


def _read_cache() -> dict[str, str]:
    path = _cache_path()
    file_stat = path.lstat()
    if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_size > _MAX_CACHE_BYTES:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != _CACHE_KEYS:
        return {}
    if not all(isinstance(raw.get(key), str) for key in _CACHE_KEYS):
        return {}
    return {key: raw[key] for key in _CACHE_KEYS}


def _write_cache(payload: dict[str, str]) -> None:
    path = _cache_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        descriptor, raw_temp_path = tempfile.mkstemp(
            prefix=".update-reminder-",
            dir=path.parent,
        )
        temp_path = Path(raw_temp_path)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, separators=(",", ":"), sort_keys=True)
            handle.write("\n")
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _parse_checked_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc)


def evaluate_update(
    installed_version: str,
    recommended_version: str,
    minimum_safe_version: str,
    check_interval_hours: int,
) -> dict[str, str | bool]:
    """Return a bounded decision and persist only version/timestamp state."""
    status = classify_versions(
        installed_version,
        recommended_version,
        minimum_safe_version,
    )
    interval_valid = (
        not isinstance(check_interval_hours, bool)
        and isinstance(check_interval_hours, int)
        and 1 <= check_interval_hours <= 8760
    )
    if not interval_valid:
        return {"status": "unknown", "should_remind": False}
    if status not in {"update_available", "below_minimum"}:
        return {
            "status": status,
            "should_remind": False,
        }

    now = _now_utc()
    try:
        cache = _read_cache()
    except (OSError, ValueError, json.JSONDecodeError):
        cache = {}

    checked_at = _parse_checked_at(cache.get("checked_at"))
    same_recommendation = (
        cache.get("reminded_for_version") == recommended_version
    )
    within_interval = (
        checked_at is not None
        and now >= checked_at
        and now - checked_at < timedelta(hours=check_interval_hours)
    )
    should_remind = not (same_recommendation and within_interval)
    if recommended_version in _SESSION_REMINDERS:
        should_remind = False

    if should_remind:
        _SESSION_REMINDERS.add(recommended_version)
        payload = {
            "checked_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "installed_version": installed_version,
            "recommended_version": recommended_version,
            "reminded_for_version": recommended_version,
        }
        try:
            _write_cache(payload)
        except OSError:
            pass

    return {"status": status, "should_remind": should_remind}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-version", required=True)
    parser.add_argument("--recommended-version", required=True)
    parser.add_argument("--minimum-safe-version", required=True)
    parser.add_argument("--check-interval-hours", required=True, type=int)
    args, unknown = parser.parse_known_args()
    if unknown:
        parser.error("unsupported argument")
    return args


def main() -> int:
    args = _parse_args()
    result = evaluate_update(
        args.installed_version,
        args.recommended_version,
        args.minimum_safe_version,
        args.check_interval_hours,
    )
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
