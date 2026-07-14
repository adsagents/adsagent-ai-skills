from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MetaCopyGroupedGeoGuidanceTests(unittest.TestCase):
    def test_grouped_copy_is_two_stage_and_geo_is_approval_visible(self) -> None:
        text = (ROOT / "skills/meta-copy/SKILL.md").read_text(encoding="utf-8")

        for term in (
            "deduplicate only exact Ad names",
            "`ad_num` duplicates one source Ad",
            'mode="clone_all"',
            "target AdSet ID",
            'mode="new_ads"',
            "one bounded second approval set",
            "countries_override",
            "worldwide_override=true",
            "excluded_countries_override",
            "geo_targeting_override",
            "Do not pass geography to `new_ads`",
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
