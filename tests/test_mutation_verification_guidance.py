from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MutationVerificationGuidanceTests(unittest.TestCase):
    def test_meta_guidance_uses_live_config_for_delivery_configuration(self) -> None:
        paths = [
            ROOT / "skills" / "meta-insights" / "SKILL.md",
            ROOT / "skills" / "meta-copy" / "SKILL.md",
            ROOT / "skills" / "adsagent-router" / "SKILL.md",
            ROOT / "skills" / "adsagent-reliability" / "SKILL.md",
            ROOT / "docs" / "output-contract.md",
            ROOT / "docs" / "examples.md",
        ]

        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("overview_get_live_configs", text, path)
            self.assertIn("next_action", text, path)

    def test_insights_mutation_watermark_is_metrics_only(self) -> None:
        text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
