from __future__ import annotations

import json
from pathlib import Path

from scripts.sync_claude_plugin_tree import (
    PLUGIN_SOURCE,
    plugin_tree_problems,
    write_plugin_tree,
)


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PLUGIN_PARTS = {
    "scripts",
    "tests",
    "submissions",
    "docs",
    "assets",
    "skill_pack_mcp",
    ".cursor-plugin",
    "Dockerfile",
    "contracts",
    "registry",
}


def test_marketplace_publishes_adsagent_from_plugin_directory() -> None:
    marketplace = json.loads(
        (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    plugin = marketplace["plugins"][0]

    assert marketplace["name"] == "adsagent"
    assert plugin["name"] == "adsagent"
    assert plugin["source"] == PLUGIN_SOURCE == "./plugin"


def test_generated_plugin_tree_matches_sources_and_stays_clean() -> None:
    assert plugin_tree_problems(ROOT) == []
    for path in (ROOT / "plugin").rglob("*"):
        assert FORBIDDEN_PLUGIN_PARTS.isdisjoint(path.parts)

    assert (ROOT / "plugin" / ".mcp.json").read_bytes() == (
        ROOT / ".mcp.json"
    ).read_bytes()
    assert (ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_bytes() == (
        ROOT / ".claude-plugin" / "plugin.json"
    ).read_bytes()
    skill = ROOT / "skills" / "adsagent-router" / "SKILL.md"
    assert (ROOT / "plugin" / skill.relative_to(ROOT)).read_bytes() == skill.read_bytes()


def test_other_channel_manifests_still_read_the_repository_root() -> None:
    cursor = json.loads(
        (ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert cursor["name"] == "adsagent"
    assert cursor["skills"] == "./skills/"
    assert cursor["mcpServers"] == "./mcp.json"
    assert cursor["logo"] == "assets/logo.png"
    assert (ROOT / "assets" / "logo.png").is_file()
    assert "COPY --chown=app:app skills /app/skills" in dockerfile
    assert "mcp.json" in dockerfile
    assert (ROOT / "glama.json").is_file()
    assert "codex plugin marketplace add adsagents/adsagent-ai-skills" in readme
    assert "codex plugin add adsagent@adsagent" in readme
    assert (ROOT / "mcp.json").read_bytes() == (ROOT / ".mcp.json").read_bytes()


def _sample_root(tmp_path: Path) -> Path:
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text(
        "Use when demonstrating the plugin tree.\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        '{"name":"adsagent"}\n',
        encoding="utf-8",
    )
    (tmp_path / ".mcp.json").write_text('{"mcpServers":{}}\n', encoding="utf-8")
    return tmp_path


def test_sync_is_idempotent_and_rejects_a_stale_copy(tmp_path: Path) -> None:
    root = _sample_root(tmp_path)
    write_plugin_tree(root)
    assert plugin_tree_problems(root) == []

    write_plugin_tree(root)
    assert plugin_tree_problems(root) == []

    skill = root / "plugin" / "skills" / "demo" / "SKILL.md"
    skill.write_text("stale\n", encoding="utf-8")
    problems = plugin_tree_problems(root)
    assert any("differs from skills/demo/SKILL.md" in problem for problem in problems)


def test_plugin_tree_rejects_credential_reads_images_and_extra_files(
    tmp_path: Path,
) -> None:
    root = _sample_root(tmp_path)
    write_plugin_tree(root)
    skill = root / "plugin" / "skills" / "demo" / "SKILL.md"
    skill.write_text(
        "token = os.environ['ADSAGENT_DRIFT_GITHUB_TOKEN']\n"
        "also os.getenv('TOKEN')\n"
        "see assets/logo.png and fonts/Inter.ttf\n",
        encoding="utf-8",
    )
    leaked = root / "plugin" / "scripts"
    leaked.mkdir()
    (leaked / "check_drift.py").write_text(
        "import os\nos.getenv('ADSAGENT_DRIFT_GITHUB_TOKEN')\n",
        encoding="utf-8",
    )
    (root / "plugin" / "logo.png").write_bytes(b"\x89PNG")

    problems = plugin_tree_problems(root)
    assert any("reads environment credentials" in problem for problem in problems)
    assert any("references an image or font" in problem for problem in problems)
    assert any(
        problem == "unexpected plugin file plugin/scripts/check_drift.py"
        for problem in problems
    )
    assert any(problem == "plugin/logo.png is an image or font file" for problem in problems)


def test_authorization_prose_in_a_skill_is_not_a_credential_read(tmp_path: Path) -> None:
    root = _sample_root(tmp_path)
    (root / "skills" / "demo" / "SKILL.md").write_text(
        "Do not add `headers.Authorization` to either file.\n",
        encoding="utf-8",
    )
    write_plugin_tree(root)
    assert plugin_tree_problems(root) == []
