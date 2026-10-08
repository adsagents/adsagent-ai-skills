from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_tri_channel_pack as validator


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ".codex-plugin/plugin.json"


class CodexPluginManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name in (".codex-plugin", "skills", "assets"):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copy(ROOT / ".mcp.json", self.root / ".mcp.json")
        self.expected_mcp = json.loads((ROOT / ".mcp.json").read_text("utf-8"))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _manifest(self) -> dict:
        return json.loads((self.root / MANIFEST).read_text("utf-8"))

    def _write(self, manifest: dict) -> None:
        (self.root / MANIFEST).write_text(json.dumps(manifest), "utf-8")

    def _validate(self) -> None:
        with patch.object(validator, "ROOT", self.root):
            validator.validate_codex_plugin(self.expected_mcp)

    def _assert_rejected(self, mutate) -> None:
        manifest = self._manifest()
        mutate(manifest)
        self._write(manifest)
        with self.assertRaises(SystemExit):
            self._validate()

    def test_repository_manifest_is_valid(self) -> None:
        self._validate()

    def test_manifest_matches_openai_plugin_shape(self) -> None:
        manifest = self._manifest()
        self.assertEqual(manifest["name"], "adsagent")
        self.assertEqual(manifest["version"], (ROOT / "VERSION").read_text().strip())
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
        self.assertEqual(
            manifest["extensions"]["com.openai"]["onboardingSkill"],
            "./skills/adsagent-setup/SKILL.md",
        )
        self.assertEqual(manifest["author"]["email"], "support@adsagent.md")

    def test_icons_are_square_transparent_svgs(self) -> None:
        for name in ("icon.svg", "icon-dark.svg"):
            svg = (ROOT / "assets" / name).read_text("utf-8")
            self.assertIn('viewBox="0 0 48 48"', svg, name)
            self.assertIn('fill="none"', svg, name)
            self.assertNotIn("<image", svg, name)

    def test_version_drift_is_rejected(self) -> None:
        self._assert_rejected(lambda m: m.update(version="0.0.0"))

    def test_missing_skills_dir_is_rejected(self) -> None:
        self._assert_rejected(lambda m: m.update(skills="./missing/"))

    def test_missing_onboarding_skill_is_rejected(self) -> None:
        self._assert_rejected(
            lambda m: m["extensions"]["com.openai"].update(
                onboardingSkill="./skills/missing/SKILL.md"
            )
        )

    def test_unprefixed_or_escaping_paths_are_rejected(self) -> None:
        self._assert_rejected(lambda m: m.update(mcpServers=".mcp.json"))
        self._assert_rejected(lambda m: m.update(mcpServers="./../.mcp.json"))

    def test_mcp_file_must_be_valid_json_with_three_urls(self) -> None:
        (self.root / ".mcp.json").write_text("{not json", "utf-8")
        with self.assertRaises(SystemExit):
            self._validate()

        broken = json.loads(json.dumps(self.expected_mcp))
        del broken["mcpServers"]["tiktok"]
        (self.root / ".mcp.json").write_text(json.dumps(broken), "utf-8")
        with self.assertRaises(SystemExit):
            self._validate()

    def test_bearer_headers_are_rejected(self) -> None:
        tainted = json.loads(json.dumps(self.expected_mcp))
        tainted["mcpServers"]["meta"]["headers"] = {"Authorization": "Bearer x"}
        (self.root / ".mcp.json").write_text(json.dumps(tainted), "utf-8")
        with patch.object(validator, "ROOT", self.root):
            with self.assertRaises(SystemExit):
                validator.validate_codex_plugin(tainted)

    def test_interface_limits_are_enforced(self) -> None:
        self._assert_rejected(
            lambda m: m["interface"].update(shortDescription="x" * 31)
        )
        self._assert_rejected(
            lambda m: m["interface"].update(defaultPrompt=["@AdsAgent hi"])
        )
        self._assert_rejected(
            lambda m: m["interface"].update(defaultPrompt=["a", "b", "c", "d"])
        )
        self._assert_rejected(lambda m: m["interface"].pop("composerIcon"))
        self._assert_rejected(
            lambda m: m["interface"].update(privacyPolicyURL="http://x")
        )


if __name__ == "__main__":
    unittest.main()
