from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseContractTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return read_contract(ROOT, relative_path)

    def test_public_surfaces_do_not_describe_an_unpublished_private_pack(self) -> None:
        text = "\n".join(
            self._read(path)
            for path in (
                "README.md",
                ".claude-plugin/marketplace.json",
                "docs/safety.md",
            )
        ).lower()

        for stale_term in (
            "private skill pack",
            "private github staging repo",
            "safe to publish later",
        ):
            self.assertNotIn(stale_term, text)

    def test_codex_public_install_uses_anonymous_https_clone(self) -> None:
        readme = self._read("README.md")

        self.assertIn(
            "codex plugin marketplace add adsagents/adsagent-ai-skills",
            readme,
        )
        self.assertIn(
            "codex plugin add adsagent@adsagent",
            readme,
        )
        self.assertIn(
            "git clone https://github.com/adsagents/adsagent-ai-skills.git",
            readme,
        )
        self.assertNotIn("git@github.com:adsagents/adsagent-ai-skills.git", readme)

    def test_validator_never_executes_documentation_code(self) -> None:
        tree = ast.parse(self._read("scripts/validate_tri_channel_pack.py"))
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

        self.assertNotIn("exec", called_names)
        self.assertNotIn("eval", called_names)

    def test_validation_helpers_have_no_network_or_process_capability(self) -> None:
        imported_roots: set[str] = set()
        for path in (
            "scripts/skill_contract.py",
            "scripts/skill_routing_contract.py",
            "scripts/validate_public_tool_manifests.py",
        ):
            tree = ast.parse(self._read(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_roots.update(
                        alias.name.split(".", 1)[0]
                        for alias in node.names
                    )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_roots.add(node.module.split(".", 1)[0])

        self.assertTrue(
            imported_roots.isdisjoint(
                {
                    "httpx",
                    "requests",
                    "socket",
                    "subprocess",
                    "urllib",
                }
            )
        )

    def test_validation_workflow_pins_third_party_actions(self) -> None:
        workflow = self._read(".github/workflows/validate.yml")

        self.assertIn(
            "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
            workflow,
        )
        self.assertIn(
            "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
            workflow,
        )
        self.assertNotIn("actions/checkout@v", workflow)
        self.assertNotIn("actions/setup-python@v", workflow)

    def test_root_mcp_json_declares_oauth_http_servers_without_bearer(self) -> None:
        mcp = json.loads(self._read(".mcp.json"))
        servers = mcp.get("mcpServers", {})
        self.assertEqual(set(servers), {"meta", "google", "tiktok"})
        for name, config in servers.items():
            self.assertEqual(config.get("type"), "http", name)
            self.assertIn("url", config, name)
            self.assertNotIn("headers", config, name)
            self.assertNotIn("Authorization", json.dumps(config), name)

    def test_cursor_mcp_json_matches_claude_mcp_contract(self) -> None:
        claude_mcp = json.loads(self._read(".mcp.json"))
        cursor_mcp = json.loads(self._read("mcp.json"))
        self.assertEqual(cursor_mcp, claude_mcp)

    def test_cursor_plugin_manifest_declares_skills_and_mcp(self) -> None:
        manifest = json.loads(self._read(".cursor-plugin/plugin.json"))
        self.assertEqual(manifest.get("name"), "adsagent")
        self.assertEqual(manifest.get("mcpServers"), "./mcp.json")
        self.assertEqual(manifest.get("skills"), "./skills/")
        self.assertEqual(manifest.get("logo"), "assets/logo.png")
        self.assertEqual(
            manifest.get("version"),
            self._read("VERSION").strip(),
        )

    def test_release_files_do_not_hardcode_local_checkout_paths(self) -> None:
        text_parts: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue
            if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
                continue
            if path.name == ".DS_Store":
                continue
            try:
                text_parts.append(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                continue
        text = "\n".join(text_parts)

        self.assertNotIn("/" + "Users/", text)
        self.assertNotIn("/private" + "/tmp/", text)

    def test_update_reminder_has_no_network_or_process_capability(self) -> None:
        tree = ast.parse(self._read("scripts/update_reminder.py"))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])

        self.assertTrue(
            imported_roots.isdisjoint(
                {"httpx", "requests", "socket", "subprocess", "urllib"}
            )
        )

    def test_release_manifest_is_bounded_and_matches_public_identity(self) -> None:
        manifest = json.loads(self._read("release-manifest.json"))
        version = self._read("VERSION").strip()

        self.assertEqual(
            manifest,
            {
                "schema_version": 1,
                "package": "adsagent-ai-skills",
                "repository": "adsagents/adsagent-ai-skills",
                "version": version,
                "tag": f"v{version}",
                "release_url": (
                    "https://github.com/adsagents/adsagent-ai-skills/releases/tag/"
                    f"v{version}"
                ),
            },
        )
        self.assertLess(
            len(json.dumps(manifest, separators=(",", ":")).encode("utf-8")),
            512,
        )

    def test_quickcreate_confirmation_and_permission_contract_is_documented(self) -> None:
        text = "\n".join(
            self._read(path)
            for path in (
                "skills/meta-copy/SKILL.md",
                "skills/adsagent-reliability/SKILL.md",
                "docs/output-contract.md",
                "docs/examples.md",
                "docs/faq.md",
            )
        )

        for term in (
            "15 minutes",
            "single-use",
            "expires_at",
            "confirm_token_invalid",
            "no_create_permission",
            "/dashboard/assets/fb-users",
            "response_mode=compact",
            "Never enable or modify customer permissions automatically",
        ):
            self.assertIn(term, text)

    def test_proprietary_license_grants_anthropic_directory_mirror_exception(self) -> None:
        license_text = self._read("LICENSE.md")

        for term in (
            "Anthropic Claude Plugin Directory Exception",
            "anthropics/claude-plugins-community",
            "does not make this package open source",
        ):
            self.assertIn(term, license_text)

    def test_proprietary_license_file_is_present(self) -> None:
        license_text = self._read("LICENSE.md")

        self.assertIn("All rights reserved", license_text)

    def test_official_identity_and_restricted_use_notice_are_present(self) -> None:
        public_text = "\n".join(
            self._read(path)
            for path in (
                "README.md",
                "SECURITY.md",
                "LICENSE.md",
                "NOTICE.md",
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                ".cursor-plugin/plugin.json",
            )
        )

        for term in (
            "https://adsagent.md",
            "support@adsagent.md",
            "https://github.com/adsagents/adsagent-ai-skills",
            "adsagents LLC",
            "Proprietary",
            "redistribute",
            "mirror",
            "derivative works",
            "competing product",
            "does not grant any additional intellectual-property license",
        ):
            self.assertIn(term, public_text)
        self.assertNotIn("published as private product documentation", public_text)


if __name__ == "__main__":
    unittest.main()
