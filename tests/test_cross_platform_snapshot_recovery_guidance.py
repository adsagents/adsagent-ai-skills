from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CrossPlatformSnapshotRecoveryGuidanceTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_release_version_is_consistent(self) -> None:
        self.assertEqual(self._read("VERSION").strip(), "0.7.32")
        for path in (
            "README.md",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "scripts/validate_tri_channel_pack.py",
        ):
            self.assertIn("0.7.32", self._read(path), path)

    def test_google_keeps_platform_route_and_read_only_capability_truth(self) -> None:
        text = self._read("skills/google-ads-insights/SKILL.md")
        for term in (
            "opaque continuation",
            "login-customer route",
            "page size",
            "source snapshot",
            "Never add Meta `min_as_of`",
            "does not add a public MCP write capability",
            "snapshot_expired",
        ):
            self.assertIn(term, text)

    def test_tiktok_keeps_single_use_continuation_and_write_route(self) -> None:
        text = self._read("skills/tiktok-insights/SKILL.md")
        for term in (
            "opaque continuation",
            "single-use",
            "authorization route",
            "page size",
            "source snapshot",
            "Never add Meta `min_as_of`",
            "Never replay",
        ):
            self.assertIn(term, text)

    def test_shared_contract_separates_meta_anchor_from_other_channels(self) -> None:
        text = "\n".join(
            self._read(path)
            for path in (
                "skills/adsagent-reliability/SKILL.md",
                "docs/output-contract.md",
                "docs/examples.md",
            )
        )
        for term in (
            "Never move Meta `min_as_of` into Google or TikTok requests",
            "Never send Meta `min_as_of` to Google or TikTok",
            "continuation replay rejection",
            "exact original tenant, advertiser, and authorization route",
        ):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
