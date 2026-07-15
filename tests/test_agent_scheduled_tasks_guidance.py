from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentScheduledTasksGuidanceTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_is_packaged_and_routed(self) -> None:
        plugin = json.loads(self._read(".claude-plugin/plugin.json"))
        self.assertIn("./skills/agent-scheduled-tasks", plugin["skills"])

        router = self._read("skills/adsagent-router/SKILL.md")
        self.assertIn("scheduled task / automation / cron / reminder", router)
        self.assertIn("`agent-scheduled-tasks`", router)

    def test_skill_distinguishes_configuration_from_execution_proof(self) -> None:
        text = self._read("skills/agent-scheduled-tasks/SKILL.md")

        for term in (
            "reminder_or_heartbeat",
            "auditable_execution",
            "consequential_execution",
            "scheduler_kind=heartbeat",
            "execution_history_available=false",
            "Creation is not execution proof",
            "run-now",
            "read back",
            "run ID",
            "terminal status",
            "result or artifact reference",
            "append-only run log",
        ):
            self.assertIn(term, text)

    def test_skill_requires_deterministic_schedule_and_safe_prompt(self) -> None:
        text = self._read("skills/agent-scheduled-tasks/SKILL.md")

        for term in (
            "IANA timezone",
            "cadence",
            "source freshness",
            "prevent overlapping runs",
            "stable jitter",
            "Preserve scheduler enum casing",
            "destination",
            "stable scope",
            "rule_id_and_version",
            "idempotency",
            "bounded retry",
            "Do not put bearer tokens",
            "Do not claim success",
        ):
            self.assertIn(term, text)

    def test_adsagent_automation_remains_capability_and_approval_gated(self) -> None:
        text = self._read("skills/agent-scheduled-tasks/SKILL.md")

        for term in (
            "setup_get_status.capabilities",
            "complete=true",
            "task_ref",
            "prepare",
            "confirm",
            "mutation_ref",
            "operations_get",
            "Never auto-enable permissions",
        ):
            self.assertIn(term, text)

    def test_release_version_is_consistent(self) -> None:
        plugin = json.loads(self._read(".claude-plugin/plugin.json"))
        marketplace = json.loads(self._read(".claude-plugin/marketplace.json"))
        expected = "0.7.14"

        self.assertEqual(expected, self._read("VERSION").strip())
        self.assertEqual(expected, plugin["version"])
        self.assertEqual(expected, marketplace["metadata"]["version"])
        self.assertEqual(expected, marketplace["plugins"][0]["version"])


if __name__ == "__main__":
    unittest.main()
