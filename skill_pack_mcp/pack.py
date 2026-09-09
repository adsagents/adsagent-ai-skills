"""Read-only helpers for the public AdsAgent skill-pack files.

Stdlib only. Used by the docs MCP and by CI tests that must not install the
MCP SDK. This module never contacts Meta, Google Ads, TikTok, or AdsAgent
hosted services.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

SKILL_ID_RE = re.compile(r"^[a-z0-9-]+$")
REFERENCE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*$"
)
MAX_FILE_BYTES = 128_000
README_EXCERPT_CHARS = 6_000

HOSTED_OAUTH_NOTICE = (
    "These HTTP URLs are the production AdsAgent ads MCP endpoints. Clients "
    "must complete AdsAgent OAuth against those hosted services. This docs "
    "MCP does not proxy OAuth, accept tokens, or execute campaigns."
)

DOCS_ONLY_NOTICE = (
    "AdsAgent Skill Pack (docs) reads public repository Markdown only. "
    "It is not the hosted AdsAgent Meta, Google Ads, or TikTok MCP."
)


class PackError(ValueError):
    """Raised when a requested skill-pack path is missing or unsafe."""


def default_root() -> Path:
    override = os.environ.get("SKILL_PACK_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def read_version(root: Path) -> str:
    path = root / "VERSION"
    if not path.is_file():
        raise PackError("VERSION file is missing")
    version = path.read_text(encoding="utf-8").strip()
    if not version:
        raise PackError("VERSION file is empty")
    return version


def _skills_root(root: Path) -> Path:
    skills = (root / "skills").resolve()
    if not skills.is_dir():
        raise PackError("skills/ directory is missing")
    return skills


def _parse_frontmatter(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    if not text.startswith("---\n"):
        return data
    try:
        _, frontmatter, _ = text.split("---\n", 2)
    except ValueError:
        return data
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def _first_heading(text: str) -> str:
    body = text
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        body = parts[2] if len(parts) == 3 else text
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _read_bounded_text(path: Path) -> str:
    data = path.read_bytes()
    if len(data) > MAX_FILE_BYTES:
        raise PackError(f"{path.name} exceeds {MAX_FILE_BYTES} bytes")
    return data.decode("utf-8")


def list_skills(root: Path) -> dict[str, Any]:
    skills_root = _skills_root(root)
    skills: list[dict[str, str]] = []
    for entry in sorted(skills_root.iterdir(), key=lambda p: p.name):
        skill_md = entry / "SKILL.md"
        if not entry.is_dir() or not skill_md.is_file():
            continue
        text = _read_bounded_text(skill_md)
        frontmatter = _parse_frontmatter(text)
        skill_id = frontmatter.get("name") or entry.name
        skills.append(
            {
                "id": skill_id,
                "description": frontmatter.get("description", ""),
                "title": _first_heading(text),
            }
        )
    return {
        "notice": DOCS_ONLY_NOTICE,
        "skills": skills,
    }


def _safe_skill_dir(root: Path, skill_id: str) -> Path:
    if SKILL_ID_RE.fullmatch(skill_id) is None:
        raise PackError(
            "skill_id must be a lowercase hyphenated folder name under skills/"
        )
    skills_root = _skills_root(root)
    skill_dir = (skills_root / skill_id).resolve()
    if skills_root not in skill_dir.parents:
        raise PackError("skill_id escapes skills/")
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        known = sorted(
            p.name
            for p in skills_root.iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file()
        )
        raise PackError(
            f"unknown skill_id {skill_id!r}; known skills: {', '.join(known)}"
        )
    return skill_dir


def _safe_reference(skill_dir: Path, name: str) -> Path:
    if REFERENCE_RE.fullmatch(name) is None or name.endswith(".md") is False:
        raise PackError(
            "references must be skill-local .md filenames "
            "(no absolute paths or parent segments)"
        )
    candidate = (skill_dir / name).resolve()
    if skill_dir not in candidate.parents and candidate != skill_dir:
        raise PackError(f"reference escapes skill folder: {name}")
    if not candidate.is_file():
        raise PackError(f"missing skill reference: {name}")
    return candidate


def get_skill(
    root: Path,
    skill_id: str,
    references: list[str] | None = None,
) -> dict[str, Any]:
    skill_dir = _safe_skill_dir(root, skill_id)
    files = [
        {
            "path": "SKILL.md",
            "content": _read_bounded_text(skill_dir / "SKILL.md"),
        }
    ]
    for name in references or []:
        path = _safe_reference(skill_dir, name)
        rel = path.relative_to(skill_dir).as_posix()
        if rel == "SKILL.md":
            continue
        files.append({"path": rel, "content": _read_bounded_text(path)})
    return {
        "notice": DOCS_ONLY_NOTICE,
        "id": skill_id,
        "files": files,
    }


def get_hosted_mcp_urls(root: Path) -> dict[str, Any]:
    path = root / "mcp.json"
    if not path.is_file():
        raise PackError("mcp.json is missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_servers = payload.get("mcpServers")
    if not isinstance(raw_servers, dict):
        raise PackError("mcp.json is missing mcpServers")
    servers: list[dict[str, str]] = []
    for name, config in raw_servers.items():
        if not isinstance(config, dict):
            continue
        url = config.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise PackError(f"mcp.json server {name!r} has no https url")
        servers.append(
            {
                "id": str(name),
                "type": str(config.get("type") or "http"),
                "url": url,
            }
        )
    if not servers:
        raise PackError("mcp.json declares no hosted HTTP MCP URLs")
    return {
        "notice": DOCS_ONLY_NOTICE,
        "oauth": HOSTED_OAUTH_NOTICE,
        "servers": servers,
    }


def get_pack_readme(root: Path) -> dict[str, Any]:
    readme_path = root / "README.md"
    if not readme_path.is_file():
        raise PackError("README.md is missing")
    text = readme_path.read_text(encoding="utf-8")
    excerpt = text
    marker = "## Included Skills"
    if marker in excerpt:
        excerpt = excerpt.split(marker, 1)[0].rstrip()
    if len(excerpt) > README_EXCERPT_CHARS:
        excerpt = excerpt[:README_EXCERPT_CHARS].rstrip() + "\n…"
    return {
        "notice": DOCS_ONLY_NOTICE,
        "version": read_version(root),
        "server": "AdsAgent Skill Pack (docs)",
        "readme_excerpt": excerpt,
    }
