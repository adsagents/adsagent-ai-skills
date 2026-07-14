---
name: adsagent-router
description: Use when the user mentions AdsAgent, Meta/Facebook, Google Ads, TikTok, hosted MCP setup, product or campaign performance, AppsFlyer, copy/recreate, Retry-After, 429/503, stale sessions, or operator review.
---

# AdsAgent Router

Pick the platform skill and narrowest safe workflow.

## Route Map

- Meta / Facebook / FB / Page / pixel / campaign copy: `meta-insights` for reads; `meta-copy` for copy, recreate, compare, or write preparation.
- Google Ads / MCC / customer / search / PMax: `google-ads-insights`.
- TikTok / advertiser / TT: `tiktok-insights`.
- 429 / 503 / Retry-After / concurrency / stale session: `adsagent-reliability` before retrying.
- setup / connect / OAuth / MCP token: `adsagent-setup`.
- scheduled task / automation / cron / reminder: `agent-scheduled-tasks` before creating or changing the schedule.

New Meta connections use `https://adsagent.md/mcp/v2`; `/mcp` is the legacy fallback.

## Copy Routing

Never guess:

- One ad -> `copy_ad_quick_copy`.
- Campaign/ad set -> `copy_ad_clone_structure`.
- Repeat prior creation -> `campaigns_recreate_from_task`.
- Then ask deep-post reuse versus fresh creative upload.

## First Test

When scope is missing:

1. Read setup status.
2. Inspect `setup_get_status.capabilities`; capability truth overrides guessed cross-platform parity.
3. Discover platform accounts.
4. Ask which scope and dates to inspect.
5. When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, route one or many scopes through its advertised `consistent_query_tool` with root `query_contract_version=1`; otherwise use native single/batch tools.

Never hardcode scope or carry Meta fields into Google/TikTok.

## Shared Rules

- Hosted HTTP MCP is authoritative.
- Use public handles and Markdown.
- Never read raw rows for normal questions or fan out across scopes/days.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- Return full tables through an artifact workflow.
- On `mcp_fanout_detected`, stop the loop and use the platform batch tool.
- Consequential writes require prepare, sanitized summary, explicit approval, then confirm.
- QuickCreate confirm tokens are single-use for 15 minutes. On `confirm_token_invalid`, prepare again and obtain fresh approval; never retry the old confirm.
- Poll creation using its returned `task_ref`. On `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never change customer permissions automatically.
- Meta delivery config verification follows the returned `next_action` to `overview_get_live_configs`; never substitute an Insights watermark.
- Meta decisions use `insights_query_consistent(require_fresh)` only when advertised; recovery uses `operations_get_context`.
- Meta candidate reads use one allowlisted AND `filters` plan; keep full hierarchy IDs, and leave exact name deduplication, language classification, and business grouping to the client.
- For a completed Meta consistency refresh, consume its terminal result; never rerun page 1. Pin later pages to the source anchor with `min_as_of`.
- Use the common envelope only for `agent_method_profile.profile_id=adsagent_agent_methods_v1`; otherwise preserve native output.
- When an error includes `support_ref`, preserve it verbatim and show it for unresolved/operator-review handoff. It is not authorization; never invent, modify, enumerate, or replace it with raw tokens, request bodies, or logs.
- Google remains a cached read-only ledger. TikTok freshness, task refs, since-launch reads, and mutation receipts remain capability-gated. A shared profile does not imply cross-platform evidence parity, so never copy unsupported behavior across servers.
