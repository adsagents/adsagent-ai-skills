from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MetaCopyGroupedGeoGuidanceTests(unittest.TestCase):
    def test_grouped_copy_is_one_server_owned_prepare(self) -> None:
        text = (ROOT / "skills/meta-copy/SKILL.md").read_text(encoding="utf-8")

        for term in (
            "deduplicate only exact Ad names",
            "`ad_num` duplicates one source Ad",
            "multiple distinct source Ads",
            "`grouped_plan`",
            "1-1-N",
            "1-N-1",
            "one paused-by-default approval summary",
            "settings_source_ad_id",
            "cgb_confirm_*",
            "copy_ad_quick_copy_confirm",
            "countries_override",
            "worldwide_override=true",
            "excluded_countries_override",
            "geo_targeting_override",
            "Do not fall back to a client-built multi-stage copy",
        ):
            self.assertIn(term, text)

        self.assertNotIn('mode="clone_all"', text)
        self.assertNotIn('mode="new_ads"', text)

    def test_router_distinguishes_single_grouped_structure_and_recreate(self) -> None:
        text = (ROOT / "skills/adsagent-router/SKILL.md").read_text(encoding="utf-8")

        for term in (
            "One ad -> `copy_ad_quick_copy`",
            "Multiple distinct source Ads",
            "`grouped_plan`",
            "Campaign/ad set -> `copy_ad_clone_structure`",
            "Repeat prior creation -> `campaigns_recreate_from_task`",
        ):
            self.assertIn(term, text)

    def test_missing_settings_reference_stops_before_prepare(self) -> None:
        text = (ROOT / "skills/meta-copy/SKILL.md").read_text(encoding="utf-8")

        for term in (
            "omits its Campaign, AdSet, or template reference",
            "stop before preparing",
            "Ask for one concrete reference",
            "never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings",
        ):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
