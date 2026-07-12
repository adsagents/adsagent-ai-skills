from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "scripts" / "update_reminder.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("update_reminder", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("update reminder helper cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateReminderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.helper = load_helper()
        self.helper._SESSION_REMINDERS.clear()

    def test_semver_comparison_is_numeric_and_prerelease_aware(self) -> None:
        compare = self.helper.compare_semver
        self.assertEqual(compare("0.7.10", "0.7.9"), 1)
        self.assertEqual(compare("1.0.0", "1.0.0"), 0)
        self.assertEqual(compare("1.0.0-rc.1", "1.0.0"), -1)
        self.assertEqual(compare("1.0.0-rc.10", "1.0.0-rc.2"), 1)

    def test_classification_covers_current_between_below_and_invalid(self) -> None:
        classify = self.helper.classify_versions
        self.assertEqual(classify("0.7.1", "0.7.1", "0.7.0"), "up_to_date")
        self.assertEqual(classify("0.7.0", "0.7.1", "0.7.0"), "update_available")
        self.assertEqual(classify("0.6.9", "0.7.1", "0.7.0"), "below_minimum")
        self.assertEqual(classify("v0.7.0", "0.7.1", "0.7.0"), "unknown")
        self.assertEqual(classify("0.7.1", "0.7.1", "0.8.0"), "unknown")

    def test_invalid_interval_makes_the_policy_unknown(self) -> None:
        result = self.helper.evaluate_update("0.7.1", "0.7.1", "0.7.0", 0)
        self.assertEqual(result, {"status": "unknown", "should_remind": False})

    def test_reminder_is_suppressed_for_interval_and_new_version_is_immediate(self) -> None:
        start = datetime(2026, 7, 12, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as cache_root:
            with mock.patch.dict(
                os.environ,
                {"XDG_CACHE_HOME": cache_root},
                clear=False,
            ), mock.patch.object(self.helper, "_now_utc", return_value=start):
                first = self.helper.evaluate_update("0.7.0", "0.7.1", "0.7.0", 24)

            self.assertEqual(
                first,
                {"status": "update_available", "should_remind": True},
            )
            cache_path = (
                Path(cache_root)
                / "adsagent-ai-skills"
                / "update-reminder-v1.json"
            )
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            self.assertLess(cache_path.stat().st_size, 512)
            self.assertEqual(stat.S_IMODE(cache_path.stat().st_mode), 0o600)
            self.assertEqual(
                set(cache),
                {
                    "checked_at",
                    "installed_version",
                    "recommended_version",
                    "reminded_for_version",
                },
            )

            self.helper._SESSION_REMINDERS.clear()
            with mock.patch.dict(
                os.environ,
                {"XDG_CACHE_HOME": cache_root},
                clear=False,
            ), mock.patch.object(
                self.helper,
                "_now_utc",
                return_value=start + timedelta(hours=1),
            ):
                repeated = self.helper.evaluate_update(
                    "0.7.0", "0.7.1", "0.7.0", 24
                )
                newer = self.helper.evaluate_update(
                    "0.7.0", "0.7.2", "0.7.0", 24
                )

            self.assertEqual(repeated["should_remind"], False)
            self.assertEqual(
                newer,
                {"status": "update_available", "should_remind": True},
            )

            self.helper._SESSION_REMINDERS.clear()
            with mock.patch.dict(
                os.environ,
                {"XDG_CACHE_HOME": cache_root},
                clear=False,
            ), mock.patch.object(
                self.helper,
                "_now_utc",
                return_value=start + timedelta(hours=26),
            ):
                after_interval = self.helper.evaluate_update(
                    "0.7.0", "0.7.2", "0.7.0", 24
                )
            self.assertEqual(after_interval["should_remind"], True)

    def test_cache_failure_is_non_blocking_and_session_deduplicated(self) -> None:
        with mock.patch.object(self.helper, "_read_cache", side_effect=OSError("denied")):
            first = self.helper.evaluate_update("0.7.0", "0.7.1", "0.7.0", 24)
            second = self.helper.evaluate_update("0.7.0", "0.7.1", "0.7.0", 24)

        self.assertEqual(first, {"status": "update_available", "should_remind": True})
        self.assertEqual(second, {"status": "update_available", "should_remind": False})

    def test_invalid_input_continues_silently_without_cache_write(self) -> None:
        with tempfile.TemporaryDirectory() as cache_root, mock.patch.dict(
            os.environ,
            {"XDG_CACHE_HOME": cache_root},
            clear=False,
        ):
            result = self.helper.evaluate_update("unknown", "0.7.1", "0.7.0", 24)

        self.assertEqual(result, {"status": "unknown", "should_remind": False})
        self.assertFalse((Path(cache_root) / "adsagent-ai-skills").exists())

    def test_oversized_or_non_regular_cache_is_ignored(self) -> None:
        start = datetime(2026, 7, 12, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as cache_root, mock.patch.dict(
            os.environ,
            {"XDG_CACHE_HOME": cache_root},
            clear=False,
        ), mock.patch.object(self.helper, "_now_utc", return_value=start):
            cache_path = (
                Path(cache_root)
                / "adsagent-ai-skills"
                / "update-reminder-v1.json"
            )
            cache_path.parent.mkdir(parents=True)
            cache_path.write_text("x" * 4097, encoding="utf-8")
            oversized = self.helper.evaluate_update(
                "0.7.0", "0.7.1", "0.7.0", 24
            )

            self.helper._SESSION_REMINDERS.clear()
            cache_path.unlink()
            cache_path.symlink_to(Path(cache_root) / "missing-target")
            symlinked = self.helper.evaluate_update(
                "0.7.0", "0.7.2", "0.7.0", 24
            )

        self.assertEqual(
            oversized,
            {"status": "update_available", "should_remind": True},
        )
        self.assertEqual(
            symlinked,
            {"status": "update_available", "should_remind": True},
        )

    def test_cli_accepts_only_scalar_policy_fields(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(HELPER_PATH),
                "--installed-version",
                "0.7.0",
                "--recommended-version",
                "0.7.1",
                "--minimum-safe-version",
                "0.7.0",
                "--check-interval-hours",
                "24",
                "--raw-setup-json",
                "{}",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("{}", proc.stdout)

    def test_skill_contains_fixed_local_update_instructions(self) -> None:
        setup = (ROOT / "skills" / "adsagent-setup" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "claude plugin update --scope user adsagent-ai-skills@adsagent-ai-skills",
            setup,
        )
        self.assertIn(
            "git -C ~/.codex/skills/adsagent-ai-skills pull --ff-only",
            setup,
        )
        self.assertIn("No automatic update", setup)
        self.assertIn("fresh session", setup)
        self.assertIn("package root `VERSION` file", setup)


if __name__ == "__main__":
    unittest.main()
