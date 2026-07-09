---
name: adsagent-setup
description: Connect and verify AdsAgent hosted MCP access without exposing internal tooling. Use when the user wants to install AdsAgent MCP, refresh a Meta, Google Ads, or TikTok connection, verify setup status, or troubleshoot first-time OAuth onboarding.
argument-hint: "<connect AdsAgent, verify setup, refresh MCP>"
version: 0.6.1
---

# AdsAgent Setup

Use this skill when the user wants to connect AdsAgent to an AI agent or verify that Meta, Google Ads, or TikTok hosted MCP access is ready.

When reporting setup status to the user, use Markdown with a short status summary, connected surfaces, blockers, and the next action. Do not dump raw setup JSON.

## Source Of Truth

The AdsAgent dashboard is the source of truth for MCP installation. The public hosted MCP endpoints are:

| Channel | Hosted MCP URL |
| --- | --- |
| Meta | `https://adsagent.md/mcp` |
| Google Ads | `https://google.adsagent.md/mcp` |
| TikTok | `https://tiktok.adsagent.md/mcp` |

Ask the user to open:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

The copied prompt contains the current hosted HTTP MCP URLs and bearer-token instructions. The same AdsAgent bearer / OAuth identity can be used across Meta, Google Ads, and TikTok when the token is issued by central auth. Do not invent a local setup, and do not ask the user to run AdsAgent MCP code on their computer.

## Setup Flow

1. Ask the user to paste the dashboard-generated install prompt into the AI client.
2. After the client saves the MCP config, perform a transport-level reconnect.
3. Re-list tools, then read the AdsAgent brief guide resource first (`adsagent://guide/brief`, a ~40-line rules digest — reading it is enough to operate safely). Do not read the full tool guide (`adsagent://guide/tools`) end-to-end; consult it on demand when a specific tool is unclear.
4. Run the setup status check exposed by AdsAgent MCP.
5. Use the returned readiness state and user-facing narrative instead of guessing from UI screenshots.

## Channel Connection Flow

- Meta readiness is checked through the Meta AdsAgent MCP at `https://adsagent.md/mcp`.
- Google Ads readiness is checked through the Google Ads MCP at `https://google.adsagent.md/mcp`.
- TikTok readiness is checked through the TikTok MCP at `https://tiktok.adsagent.md/mcp`.
- For Google Ads or TikTok disconnected states, prepare the platform OAuth flow with `connections_create_intent(channel=...)` when that tool is exposed by the hosted MCP.
- If a Google Ads or TikTok token has no central-auth identity, tell the user to refresh the dashboard install prompt or redo OAuth. Do not use email fallback, guessed account email, or manually entered identity as a substitute.

## Safe Defaults

- Hosted HTTP MCP only.
- Use bearer authentication from the dashboard prompt.
- Never print or store the bearer token in notes, logs, or generated docs.
- If setup reports that platform connection is incomplete, follow the AdsAgent-provided authorization link and status-check flow.
- If setup reports operator review, stop and ask the AdsAgent operator to inspect internal diagnostics.
- Summarize readiness in Markdown instead of exposing raw state objects.

## What Not To Do

- Do not use a local relay.
- Do not use stdio transport.
- Do not reconstruct config from memory when the dashboard prompt is available.
- Do not scrape the dashboard to infer setup status.
- Do not disclose or request internal task logs, database rows, or hidden validation details.
