"""Stdio MCP server that exposes public skill-pack docs.

Uses the official MCP Python SDK (MCPServer). Tools only read local files.
"""

from __future__ import annotations

from typing import Annotated

from mcp.server import MCPServer

from skill_pack_mcp import SERVER_INSTRUCTIONS, SERVER_NAME
from skill_pack_mcp.pack import (
    PackError,
    default_root,
    get_hosted_mcp_urls as pack_hosted_urls,
    get_pack_readme as pack_readme,
    get_skill as pack_get_skill,
    list_skills as pack_list_skills,
    read_version,
)

_ROOT = default_root()

mcp = MCPServer(
    SERVER_NAME,
    title=SERVER_NAME,
    description=(
        "Read-only public skill-pack documentation MCP. "
        "Not the hosted AdsAgent Meta, Google Ads, or TikTok ads backend."
    ),
    instructions=SERVER_INSTRUCTIONS,
    website_url="https://github.com/adsagents/adsagent-ai-skills",
    version=read_version(_ROOT),
)


def _ok(payload: object) -> object:
    return payload


def _fail(exc: PackError) -> dict[str, str]:
    return {"error": str(exc)}


@mcp.tool()
def list_skills() -> dict:
    """List public AdsAgent skills shipped in this repository.

    Use this first when you need a catalog of documentation skills (router,
    setup, reliability, notifications, scheduled tasks, Meta, Google Ads,
    TikTok) before opening a specific SKILL.md.

    Returns each skill id, YAML frontmatter description, and first Markdown
    heading. This tool only reads local files under skills/. It does not
    connect to Meta, Google Ads, or TikTok and does not run campaigns.
    """
    try:
        return _ok(pack_list_skills(_ROOT))
    except PackError as exc:
        return _fail(exc)


@mcp.tool()
def get_skill(
    skill_id: Annotated[
        str,
        "Skill folder name under skills/, for example meta-insights or adsagent-router.",
    ],
    references: Annotated[
        list[str] | None,
        "Optional skill-local .md filenames to include with SKILL.md, such as query-contract.md. Paths must stay inside that skill folder.",
    ] = None,
) -> dict:
    """Return one skill's SKILL.md and optional named reference files.

    Use this after list_skills when you need the full public instructions for
    a single skill. Pass references only for Markdown files that live in that
    skill folder (progressive-disclosure contracts).

    Rejects unknown skill ids and any path that leaves the skill directory.
    This is documentation retrieval, not a live ads API.
    """
    try:
        return _ok(pack_get_skill(_ROOT, skill_id, references))
    except PackError as exc:
        return _fail(exc)


@mcp.tool()
def get_hosted_mcp_urls() -> dict:
    """Return AdsAgent hosted HTTP MCP URLs from this repo's mcp.json.

    Use this when a client needs the real Meta, Google Ads, or TikTok ads MCP
    endpoints. Those services require AdsAgent OAuth on the hosted URLs.

    This docs server does not implement ads tools, does not accept tokens, and
    does not proxy those endpoints. Copy the https URLs into an MCP client and
    authenticate against AdsAgent hosted services.
    """
    try:
        return _ok(pack_hosted_urls(_ROOT))
    except PackError as exc:
        return _fail(exc)


@mcp.tool()
def get_pack_readme() -> dict:
    """Return this skill-pack VERSION and a README.md identity excerpt.

    Use this to confirm pack version and the public 'what this is / is not'
    wording, including that a Glama or Docker image of this repo is not the
    hosted AdsAgent ads backend.

    The excerpt stops before the per-skill table. It does not include secrets.
    """
    try:
        return _ok(pack_readme(_ROOT))
    except PackError as exc:
        return _fail(exc)


def main() -> None:
    mcp.run(transport="stdio")
