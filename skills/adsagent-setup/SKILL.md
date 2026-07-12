---
name: adsagent-setup
description: Use when connecting or verifying AdsAgent Meta, Google Ads, or TikTok hosted MCP, refreshing platform authorization, checking readiness, or troubleshooting first-time OAuth setup.
argument-hint: "<connect AdsAgent, verify setup, refresh MCP>"
version: 0.7.0
---

# AdsAgent Setup

The dashboard-generated install prompt is authoritative:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

Do not invent local relays, stdio setup, URLs, or credentials.

## Hosted Endpoints

| Channel | URL |
| --- | --- |
| Meta default | `https://adsagent.md/mcp/v2` |
| Meta legacy fallback | `https://adsagent.md/mcp` |
| Google Ads | `https://google.adsagent.md/mcp` |
| TikTok | `https://tiktok.adsagent.md/mcp` |

Use Meta v2 for new connections. Keep `/mcp` only as the legacy fallback for clients that cannot initialize stateless JSON v2.

## Setup Flow

1. Ask the user to paste the dashboard install prompt into the MCP client.
2. Reconnect the transport and re-list tools.
3. Read `adsagent://guide/brief`, then one bounded `adsagent://guide/catalog/<domain>` topic if needed. Never read `adsagent://guide/tools` end-to-end.
4. Run that server's `setup_get_status` and report the user-facing readiness state, blockers, and next action.
5. Inspect `setup_get_status.capabilities`; use optional consistency, live verification, recovery, or direct task refs only when advertised.
6. Never infer readiness from screenshots or a valid central token alone.

## Platform Authorization

- Meta uses the begin/check Facebook-connect flow exposed by Meta MCP; the human opens the returned URL.
- For Google Ads/TikTok, call `connections_create_intent(channel=...)`, let the human complete the single-use browser flow, then poll its check tool.
- The same AdsAgent bearer / OAuth identity can route across servers when issued by central auth, but each platform authorization is independent.
- Missing central-auth identity requires a fresh dashboard prompt or OAuth. Do not use email fallback, guessed email, manually entered identity, passwords, cookies, or authorization codes.

## Safety

- Never print/store bearer tokens in notes, logs, generated docs, or chat.
- Follow returned authorization links and status actions; do not scrape the dashboard.
- Use public handles only.
- On `operator_review_required`, stop and ask the AdsAgent operator to inspect internal diagnostics.
- Return a concise Markdown status summary, not raw setup JSON.
