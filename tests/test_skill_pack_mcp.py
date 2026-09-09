from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from skill_pack_mcp.pack import (
    DOCS_ONLY_NOTICE,
    HOSTED_OAUTH_NOTICE,
    PackError,
    get_hosted_mcp_urls,
    get_pack_readme,
    get_skill,
    list_skills,
)

ROOT = Path(__file__).resolve().parents[1]


def test_list_skills_reads_frontmatter_without_network() -> None:
    payload = list_skills(ROOT)
    ids = [row["id"] for row in payload["skills"]]
    assert payload["notice"] == DOCS_ONLY_NOTICE
    assert "adsagent-router" in ids
    assert "meta-insights" in ids
    assert "google-ads-insights" in ids
    assert "tiktok-insights" in ids
    by_id = {row["id"]: row for row in payload["skills"]}
    assert "connecting" in by_id["adsagent-setup"]["description"].lower()
    assert by_id["meta-insights"]["title"]


def test_get_skill_returns_skill_md_and_named_reference() -> None:
    payload = get_skill(
        ROOT, "meta-insights", references=["query-contract.md"]
    )
    paths = [item["path"] for item in payload["files"]]
    assert paths[0] == "SKILL.md"
    assert "query-contract.md" in paths
    skill_md = payload["files"][0]["content"]
    assert skill_md.startswith("---\n")
    assert "name: meta-insights" in skill_md
    assert payload["notice"] == DOCS_ONLY_NOTICE


def test_get_skill_rejects_unknown_and_escaping_paths() -> None:
    with pytest.raises(PackError, match="unknown skill_id"):
        get_skill(ROOT, "not-a-real-skill")
    with pytest.raises(PackError, match="skill_id"):
        get_skill(ROOT, "../secrets")
    with pytest.raises(PackError, match="references"):
        get_skill(ROOT, "meta-insights", references=["../../README.md"])
    with pytest.raises(PackError, match="references"):
        get_skill(ROOT, "meta-insights", references=["/etc/passwd"])


def test_get_hosted_mcp_urls_matches_public_mcp_json() -> None:
    payload = get_hosted_mcp_urls(ROOT)
    declared = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    urls = {row["id"]: row["url"] for row in payload["servers"]}
    assert urls["meta"] == declared["mcpServers"]["meta"]["url"]
    assert urls["google"] == declared["mcpServers"]["google"]["url"]
    assert urls["tiktok"] == declared["mcpServers"]["tiktok"]["url"]
    assert "OAuth" in payload["oauth"]
    assert payload["oauth"] == HOSTED_OAUTH_NOTICE
    assert "does not proxy" in payload["oauth"]


def test_get_pack_readme_returns_version_and_identity_excerpt() -> None:
    payload = get_pack_readme(ROOT)
    assert payload["version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert payload["server"] == "AdsAgent Skill Pack (docs)"
    assert "What This Is Not" in payload["readme_excerpt"]
    assert "## Included Skills" not in payload["readme_excerpt"]


def test_server_module_is_docs_only_stdio() -> None:
    tree = ast.parse((ROOT / "skill_pack_mcp" / "server.py").read_text(encoding="utf-8"))
    tool_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "tool"
                ):
                    tool_names.add(node.name)
    assert tool_names == {
        "list_skills",
        "get_skill",
        "get_hosted_mcp_urls",
        "get_pack_readme",
    }
    source = (ROOT / "skill_pack_mcp" / "server.py").read_text(encoding="utf-8")
    assert 'transport="stdio"' in source
    assert "AdsAgent Skill Pack (docs)" in (
        ROOT / "skill_pack_mcp" / "__init__.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "insights_query",
        "campaigns_quick_create",
        "Authorization",
        "ADSAGENT_TOKEN",
        "META_ACCESS_TOKEN",
    ):
        assert forbidden not in source


def test_dockerfile_is_stdio_docs_image_without_secrets() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert text.startswith("# AdsAgent Skill Pack (docs) MCP")
    assert "FROM python:3.12-slim-bookworm" in text
    assert "USER app" in text
    assert 'CMD ["python", "-m", "skill_pack_mcp"]' in text
    assert ".env" not in text
    assert "TOKEN" not in text
    assert "SECRET" not in text
    assert "contracts" not in text


def test_honest_surfaces_say_image_is_not_hosted_backend() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    glama = (ROOT / "docs" / "glama-release.md").read_text(encoding="utf-8")
    combined = "\n".join([readme, notice, security, glama]).lower()
    assert "skill pack (docs)" in combined
    assert "not the hosted" in combined
    assert "oauth" in combined
    glama_json = json.loads((ROOT / "glama.json").read_text(encoding="utf-8"))
    assert glama_json["maintainers"] == ["kimlucky7"]
    assert set(glama_json) <= {"$schema", "maintainers"}
