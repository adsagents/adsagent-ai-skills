---
name: adsagent-router
description: Use when the user mentions AdsAgent, Meta/Facebook, Google Ads, TikTok, hosted MCP setup, product or campaign performance, AppsFlyer, copy/recreate, Retry-After, 429/503, stale sessions, or operator review.
argument-hint: "<AdsAgent request>"
version: 0.7.0
---

# AdsAgent Router

Pick the platform skill and the narrowest safe workflow. Do not analyze heavily here.

## Route Map

- Meta / Facebook / FB / Page / pixel / campaign copy: `meta-insights` for reads; `meta-copy` for copy, recreate, compare, or write preparation.
- Google Ads / MCC / customer / search / PMax: `google-ads-insights`.
- TikTok / advertiser / TT: `tiktok-insights`.
- 429 / 503 / Retry-After / concurrency / stale session: `adsagent-reliability` before retrying.
- setup / connect / OAuth / MCP token: `adsagent-setup`.

New Meta connections use `https://adsagent.md/mcp/v2`; `/mcp` is the legacy fallback.

## Copy Routing

Ask; never guess:

- One ad -> `copy_ad_quick_copy`.
- Campaign/ad set -> `copy_ad_clone_structure`.
- Repeat prior creation -> `campaigns_recreate_from_task`.
- Then ask deep-post reuse versus fresh creative upload.

## First Test

When no platform or scope is named:

1. Read setup status.
2. Inspect `setup_get_status.capabilities`; capability truth overrides guessed cross-platform parity.
3. Discover Meta products, Google Ads enabled non-manager customers, or TikTok advertisers.
4. Report a bounded count/list and ask which scope and date range to inspect.
5. Route one scope to its single overview tool or multiple scopes to the platform server-side batch tool.

Never use hardcoded account/product names or carry Meta fields into Google/TikTok.

## Shared Rules

- Hosted HTTP MCP is authoritative.
- Use public handles and Markdown.
- Never read raw rows for normal questions or fan out across scopes/days.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- Return full tables through an artifact workflow.
- On `mcp_fanout_detected`, stop the loop and use the platform batch tool.
- Consequential writes require prepare, sanitized summary, explicit approval, then confirm.
- Meta decisions use `insights_query_consistent(require_fresh)` only when advertised; recovery uses `operations_get_context`.
- Google stays read-only and TikTok keeps native semantics until their capabilities advertise parity. Never copy unsupported tool names across servers.
