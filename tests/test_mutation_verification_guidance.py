from __future__ import annotations

import unittest
from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


class MutationVerificationGuidanceTests(unittest.TestCase):
    def test_meta_guidance_uses_live_config_for_delivery_configuration(self) -> None:
        paths = [
            "skills/meta-insights/SKILL.md",
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-router/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
            "docs/output-contract.md",
            "docs/examples.md",
        ]

        for path in paths:
            text = read_contract(ROOT, path)
            self.assertIn("overview_get_live_configs", text, path)
            self.assertIn("next_action", text, path)

    def test_insights_mutation_watermark_is_metrics_only(self) -> None:
        text = "\n".join(
            read_contract(ROOT, path)
            for path in (
                "skills/meta-insights/SKILL.md",
                "skills/meta-copy/SKILL.md",
                "docs/output-contract.md",
                "docs/examples.md",
            )
        )

        self.assertIn("after_mutation_ref", text)
        self.assertIn("post-write metrics", text)
        self.assertIn("does not verify delivery configuration", text)
        self.assertNotIn("verify with `after_mutation_ref", text)
        self.assertNotIn("verify it with `insights_query_consistent", text)

    def test_meta_delivery_confirmation_consumes_inline_verification_first(
        self,
    ) -> None:
        paths = (
            "skills/meta-copy/SKILL.md",
            "skills/meta-copy/creation-and-copy-contract.md",
            "skills/meta-insights/query-contract.md",
            "skills/adsagent-reliability/recovery-contract.md",
            "skills/adsagent-router/routing-contract.md",
            "docs/output-contract.md",
            "docs/examples.md",
        )
        text = "\n".join(read_contract(ROOT, path) for path in paths)

        self.assertIn("verification_result", text)
        self.assertIn("mutation_applied=true", text)
        self.assertIn("client snapshot drift", text)
        self.assertIn("only while", text)
        self.assertIn("never reauthorize", text)
        self.assertIn("never reauthorize, replace the bearer, or replay", text)
        self.assertNotIn(
            "After an approved Meta confirm, call the returned `next_action` exactly",
            text,
        )


if __name__ == "__main__":
    unittest.main()
