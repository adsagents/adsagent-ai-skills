from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentMethodProfileGuidanceTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_all_platform_guidance_prefers_profile_when_advertised(self) -> None:
        paths = (
            "skills/meta-insights/SKILL.md",
            "skills/google-ads-insights/SKILL.md",
            "skills/tiktok-insights/SKILL.md",
            "skills/adsagent-router/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
        )
        for path in paths:
            text = self._read(path)
            self.assertIn("adsagent_agent_methods_v1", text, path)
            self.assertIn("insights_query_consistent", text, path)
            self.assertIn("query_contract_version=1", text, path)

    def test_google_guidance_keeps_ledger_only_limits(self) -> None:
        text = self._read("skills/google-ads-insights/SKILL.md")
        for term in (
            "consistency=cached",
            "read-only ledger",
            "does not advertise require_fresh",
            "google_ads_insights_overview_query",
            "google_ads_insights_overview_batch",
        ):
            self.assertIn(term, text)

    def test_tiktok_guidance_is_capability_gated(self) -> None:
        text = self._read("skills/tiktok-insights/SKILL.md")
        for term in (
            "insights_query_contract.consistency_modes",
            "date_range_mode=since_launch",
            "mutation_receipts=true",
            "delivery_prepare_tool",
            "delivery_confirm_tool",
            "operation_get_tool",
            "insights_query_overview",
            "insights_query_batch_overview",
        ):
            self.assertIn(term, text)
        self.assertNotIn("Keep native task IDs until TikTok", text)
        self.assertNotIn("does not advertise require_fresh", text)

    def test_profile_does_not_claim_cross_platform_evidence_parity(self) -> None:
        text = "\n".join(
            self._read(path)
            for path in (
                "skills/adsagent-router/SKILL.md",
                "skills/adsagent-reliability/SKILL.md",
                "skills/google-ads-insights/SKILL.md",
                "skills/tiktok-insights/SKILL.md",
                "docs/output-contract.md",
            )
        )
        self.assertIn("shared profile", text.lower())
        self.assertIn("config_verified_live", text)
        self.assertIn("cached read-only ledger", text)

    def test_meta_candidate_selection_is_server_side_and_bounded(self) -> None:
        text = self._read("skills/meta-insights/SKILL.md")
        for term in (
            "page_size<=50",
            "search",
            "spend_gt",
            "dedupe_by=name",
            "adsagent_query_invalid",
            "products_list",
        ):
            self.assertIn(term, text)
        self.assertIn("Do not enlarge the page", text)


if __name__ == "__main__":
    unittest.main()
