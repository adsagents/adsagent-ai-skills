from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseContractTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

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
            "codex plugin add adsagent-ai-skills@adsagent-ai-skills",
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
