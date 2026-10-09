#!/usr/bin/env python3
"""Offline repository consistency checks; official schema/API checks are separate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
CHANNELS = {"meta": "meta", "google-ads": "google", "tiktok": "tiktok"}


def main():
    clients = [json.loads((ROOT / p).read_text())["mcpServers"]
               for p in ("mcp.json", ".mcp.json")]
    errors = []
    expected = {ROOT / "registry" / slug / "server.json" for slug in CHANNELS}
    if set((ROOT / "registry").rglob("server.json")) != expected:
        errors.append("Expected exactly the three hosted Registry manifests")
    for slug, channel in CHANNELS.items():
        path = ROOT / "registry" / slug / "server.json"
        try:
            data = json.loads(path.read_text())
            checks = {
                "schema": data.get("$schema") == SCHEMA,
                "name": data.get("name") == f"io.github.adsagents/adsagent-{slug}",
                "description": isinstance(data.get("description"), str)
                    and 1 <= len(data["description"]) <= 100,
                "version": isinstance(data.get("version"), str) and bool(data["version"]),
                "repository": data.get("repository") == {
                    "url": "https://github.com/adsagents/adsagent-ai-skills", "source": "github"},
                "remote-only": "packages" not in data,
                "OAuth URL parity": all(data.get("remotes") == [{
                    "type": "streamable-http", "url": client[channel]["url"]}]
                    for client in clients),
            }
            errors.extend(f"{slug}: {key}" for key, valid in checks.items() if not valid)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{slug}: {exc}")
    if errors:
        raise SystemExit("Registry consistency failed:\n" + "\n".join(errors))
    print("PASS: three remote-only Registry manifests match both OAuth client configurations")


if __name__ == "__main__":
    main()
