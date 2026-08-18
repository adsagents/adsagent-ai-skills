from __future__ import annotations

import unittest
from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


class MutationLifecyclePhase6GuidanceTests(unittest.TestCase):
    def test_mutation_lifecycle_contract_advertises_phase6_tools(self) -> None:
        text = read_contract(
            ROOT, "skills/adsagent-reliability/mutation-lifecycle-contract.md"
        )
        for term in (
            "capabilities.mutation_lifecycle",
            "operations_confirm_approval",
            "operations_get_approval",
            "operations_deny_approval",
            "expected_plan_digest",
            "upload_ref",
            "launch_confirm",
            "compatibility window",
        ):
            self.assertIn(term, text)

    def test_phase5_direct_write_families_documented(self) -> None:
        text = read_contract(
            ROOT, "skills/adsagent-reliability/mutation-lifecycle-contract.md"
        )
        for term in (
            "Phase 5 complete",
            "templates_create",
            "products_save_funnel_events",
            "mmp_connect",
            "fb_users_update_permissions",
            "tasks_cancel",
            "2026-08-14.13",
        ):
            self.assertIn(term, text)

    def test_setup_and_examples_document_durable_ref_confirm(self) -> None:
        text = "\n".join(
            read_contract(ROOT, path)
            for path in (
                "skills/adsagent-setup/setup-contract.md",
                "skills/adsagent-reliability/recovery-contract.md",
                "docs/examples.md",
            )
        )
        self.assertIn("operations_confirm_approval", text)
        self.assertIn("expected_plan_digest", text)
        self.assertIn("operations_get_approval", text)
        self.assertIn("operations_get(mutation_ref", text)
        self.assertIn("upload_ref", text)

    def test_version_bumped_to_0760(self) -> None:
        self.assertEqual(read_contract(ROOT, "VERSION").strip(), "0.7.64")


if __name__ == "__main__":
    unittest.main()
