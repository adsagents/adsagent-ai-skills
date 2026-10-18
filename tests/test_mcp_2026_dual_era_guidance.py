from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_setup_and_recovery_explain_dual_era_without_reregistration() -> None:
    setup = _read("skills/adsagent-setup/setup-contract.md")
    recovery = _read("skills/adsagent-reliability/recovery-contract.md")
    public = "\n".join((setup, recovery, _read("README.md"), _read("docs/faq.md")))

    for literal in (
        "2026-07-28",
        "server/discover",
        "initialize",
        "stateless",
        "MCP-Protocol-Version",
        "Mcp-Session-Id",
        "never requires MCP re-registration",
        "bearer replacement",
    ):
        assert literal in public

    assert "session recovery is legacy-only" in public
    assert "customer-permission changes" in public
    assert "automatic Skill Pack" in public


def test_release_identity_is_current() -> None:
    version = _read("VERSION").strip()
    release = json.loads(_read("release-manifest.json"))
    assert version == "0.7.77"
    assert release["version"] == version
    assert release["tag"] == f"v{version}"
