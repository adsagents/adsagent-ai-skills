#!/usr/bin/env python3
"""Validate the AdsAgent tri-channel skill pack contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.6.2"

REQUIRED_SKILLS = {
    "adsagent-router",
    "adsagent-setup",
    "adsagent-reliability",
    "meta-insights",
    "meta-copy",
    "google-ads-insights",
    "tiktok-insights",
}
MAX_SKILL_WORDS = 500

REQUIRED_REPO_TERMS = [
    "google_ads_insights_overview_batch",
    "insights_query_batch_overview",
    "mcp_concurrency_limited",
    "Retry-After",
    "connections_create_intent",
    "https://adsagent.md/mcp/v2",
    "legacy fallback",
    "error.data",
    "meta.complete=true",
    "missing scopes",
    "artifact",
]

FORBIDDEN_REPO_TERMS = [
    "Meta" + "-only",
    "meta" + "-only",
    "only " + "Meta",
    "Meta " + "package",
]

ROUTER_TERMS = [
    "Meta / Facebook / FB / Page / pixel / campaign copy",
    "Google Ads / MCC / customer / search / PMax",
    "TikTok / advertiser / TT",
    "429 / 503 / Retry-After / concurrency / stale session",
    "setup / connect / OAuth / MCP token",
]

GOOGLE_TERMS = [
    "setup_get_status",
    "google_ads_accounts_list",
    "enabled",
    "non-manager",
    "google_ads_insights_overview_query",
    "google_ads_insights_overview_batch",
    "client-side fan-out",
    "summary/total",
    "mcp_concurrency_limited",
    "Retry-After + jitter",
]

TIKTOK_TERMS = [
    "setup_get_status",
    "tenant",
    "advertiser",
    "insights_query_overview",
    "insights_query_batch_overview",
    "fan-out",
    "server summary/total",
    "429",
    "503",
    "Retry-After",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} missing YAML frontmatter")
    try:
        _, frontmatter, _ = text.split("---\n", 2)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has malformed YAML frontmatter")
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    for key in ("name", "description", "version"):
        if not data.get(key):
            fail(f"{path.relative_to(ROOT)} missing frontmatter field {key}")
    if len(frontmatter.encode("utf-8")) > 1024:
        fail(f"{path.relative_to(ROOT)} frontmatter exceeds 1024 bytes")
    if re.fullmatch(r"[a-z0-9-]+", data["name"]) is None:
        fail(f"{path.relative_to(ROOT)} has invalid skill name")
    if not data["description"].startswith("Use when"):
        fail(f"{path.relative_to(ROOT)} description must start with 'Use when'")
    return data


def assert_terms(label: str, text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term not in text]
    if missing:
        fail(f"{label} missing terms: {', '.join(missing)}")


def assert_forbidden_terms_absent(label: str, text: str, terms: list[str]) -> None:
    matches = [term for term in terms if term in text]
    if matches:
        fail(f"{label} has forbidden single-channel wording: {', '.join(matches)}")


def main() -> None:
    version = read("VERSION").strip()
    if version != VERSION:
        fail(f"VERSION is {version}, expected {VERSION}")

    plugin = json.loads(read(".claude-plugin/plugin.json"))
    marketplace = json.loads(read(".claude-plugin/marketplace.json"))
    if plugin.get("version") != VERSION:
        fail(f"plugin.json version is {plugin.get('version')}, expected {VERSION}")
    if marketplace.get("metadata", {}).get("version") != VERSION:
        fail("marketplace metadata version mismatch")
    marketplace_plugins = marketplace.get("plugins", [])
    if not marketplace_plugins or marketplace_plugins[0].get("version") != VERSION:
        fail("marketplace plugin version mismatch")

    listed_skills = {Path(entry).name for entry in plugin.get("skills", [])}
    missing_listed = sorted(REQUIRED_SKILLS - listed_skills)
    if missing_listed:
        fail(f"plugin.json missing skills: {', '.join(missing_listed)}")

    for skill in sorted(REQUIRED_SKILLS):
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")
        frontmatter = parse_skill_frontmatter(path)
        if frontmatter["name"] != skill:
            fail(f"{path.relative_to(ROOT)} name is {frontmatter['name']}, expected {skill}")
        if frontmatter["version"] != VERSION:
            fail(f"{path.relative_to(ROOT)} version is {frontmatter['version']}, expected {VERSION}")
        word_count = len(path.read_text(encoding="utf-8").split())
        if word_count > MAX_SKILL_WORDS:
            fail(
                f"{path.relative_to(ROOT)} has {word_count} words; "
                f"maximum is {MAX_SKILL_WORDS}"
            )

    assert_terms("adsagent-router", read("skills/adsagent-router/SKILL.md"), ROUTER_TERMS)
    assert_terms("google-ads-insights", read("skills/google-ads-insights/SKILL.md"), GOOGLE_TERMS)
    assert_terms("tiktok-insights", read("skills/tiktok-insights/SKILL.md"), TIKTOK_TERMS)

    setup = read("skills/adsagent-setup/SKILL.md")
    assert_terms(
        "adsagent-setup",
        setup,
        [
            "https://adsagent.md/mcp",
            "https://adsagent.md/mcp/v2",
            "legacy fallback",
            "https://google.adsagent.md/mcp",
            "https://tiktok.adsagent.md/mcp",
            "same AdsAgent bearer / OAuth identity",
            "connections_create_intent(channel=",
            "central-auth identity",
            "Do not use email fallback",
        ],
    )

    reliability = read("skills/adsagent-reliability/SKILL.md")
    assert_terms(
        "adsagent-reliability",
        reliability,
        [
            "mcp_concurrency_limited",
            "503 dependency unavailable",
            "429 concurrency",
            "server-side batch",
            "google_ads_insights_overview_batch",
            "insights_query_batch_overview",
            "error.data",
            "meta.complete=true",
            "artifact",
        ],
    )

    retry_reference = read("skills/adsagent-reliability/retry-parser.md")
    try:
        code = retry_reference.split("```python\n", 1)[1].split("\n```", 1)[0]
    except IndexError:
        fail("retry-parser.md missing executable Python block")
    namespace: dict[str, object] = {}
    exec(code, namespace)
    parser = namespace.get("retry_after_seconds")
    if not callable(parser):
        fail("retry-parser.md does not define retry_after_seconds")
    cases = [
        ({}, {"Retry-After": "7"}, 7.0),
        ({"data": {"retry_after": 3}}, {}, 3.0),
        ({"error": {"data": {"retry_after_seconds": "2.5"}}}, {}, 2.5),
    ]
    for payload, headers, expected in cases:
        if parser(payload, headers) != expected:
            fail(f"retry parser failed case expected={expected}")

    repo_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in list((ROOT / "skills").glob("*/SKILL.md"))
        + [ROOT / "README.md", ROOT / "docs/examples.md", ROOT / "docs/output-contract.md"]
    )
    assert_terms("repository docs", repo_text, REQUIRED_REPO_TERMS)
    assert_forbidden_terms_absent("repository docs", repo_text, FORBIDDEN_REPO_TERMS)

    readme = read("README.md")
    assert_terms(
        "README",
        readme,
        ["AdsAgent tri-channel", "Meta", "Google", "TikTok", "mcp_fanout_detected"],
    )
    stale_readme_terms = ["five skills", "five directories"]
    readme_lower = readme.lower()
    stale_matches = [term for term in stale_readme_terms if term in readme_lower]
    if stale_matches:
        fail(f"README has stale skill-count wording: {', '.join(stale_matches)}")
    if readme.count("Meta") > 3 and "Google" not in readme and "TikTok" not in readme:
        fail("README still reads as Meta scoped only")

    print("PASS: tri-channel skill pack contract satisfied")


if __name__ == "__main__":
    main()
