---
name: adsagent-router
description: Use when the user mentions AdsAgent, Meta/Facebook, Google Ads, TikTok, hosted MCP setup, product or campaign performance, AppsFlyer, copy/recreate, Retry-After, 429/503, stale sessions, or operator review.
---

# AdsAgent Router

## Route Map

- Meta / Facebook / FB / Page / pixel / campaign copy: `meta-insights` for reads; `meta-copy` for copy/prepare.
- Google Ads / MCC / customer / search / PMax: `google-ads-insights`.
- TikTok / advertiser / TT: `tiktok-insights`.
- 429 / 503 / Retry-After / concurrency / stale session: `adsagent-reliability` before retrying.
- setup / connect / OAuth / MCP token: `adsagent-setup`.
- scheduled task / automation / cron / reminder: `agent-scheduled-tasks`.

Meta defaults to `https://adsagent.md/mcp/v2`; `/mcp` is legacy fallback.

## Copy Routing

Never guess:

- One ad -> `copy_ad_quick_copy`.
- Multiple distinct source Ads regrouped into one destination tree -> `copy_ad_quick_copy` with `grouped_plan`.
- Campaign/ad set -> `copy_ad_clone_structure`.
- Repeat prior creation -> `campaigns_recreate_from_task`.
- Ask deep versus fresh.

## First Test

When scope is missing:

1. Read setup status.
2. Inspect `setup_get_status.capabilities`; capability truth overrides guessed cross-platform parity.
3. Discover platform accounts.
4. Ask for scope and dates.
5. When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, route one or many scopes through its advertised `consistent_query_tool` with root `query_contract_version=1`; otherwise use native single/batch tools.

## Shared Rules

- Hosted HTTP MCP is authoritative.
- Use public handles and Markdown.
- Never read raw rows for normal questions or fan out across scopes/days.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- Route exports through the channel skill's artifact workflow.
- On `mcp_fanout_detected`, stop the loop and use the platform batch tool.
- Consequential writes require prepare, sanitized summary, explicit approval, then confirm.
- Meta creation uses `creation_contract_version=3`; read `adsagent://guide/creation-contract` and `adsagent://guide/name-contract`, then emit only explicit role fields.
- Meta metadata: read `adsagent://guide/metadata-contract`; status writes use `target_configured_status`.
- On `adsagent_request_incomplete` with public `invalid_fields`, correct those fields and rerun prepare once. Never reuse or automatically retry confirm; after a second failure preserve `support_ref` and stop.
- QuickCreate tokens are single-use for 15 minutes. On `confirm_token_invalid`, prepare again; never retry old confirm.
- Poll returned `task_ref`. On `no_create_permission`, use `/dashboard/assets/fb-users`; never change permissions.
- Meta delivery config verification follows the returned `next_action` to `overview_get_live_configs`; never substitute an Insights watermark.
- Meta decisions use `insights_query_consistent(require_fresh)` only when advertised; uncertain task writes use `operations_get_context` and are never replayed.
- Meta candidate reads use one allowlisted AND plan; keep hierarchy IDs; deduplicate and group client-side.
- Continue Meta page 2 and later with the unchanged complete cached contract and first-page `min_as_of`; never rerun page 1.
- Use the common envelope only for `agent_method_profile.profile_id=adsagent_agent_methods_v1`; otherwise preserve native output.
- When an error includes `support_ref`, preserve it verbatim and show it for unresolved/operator-review handoff. It is not authorization; never invent, modify, enumerate, or replace it with raw tokens, request bodies, or logs.
- Google is a cached read-only ledger. TikTok freshness, tasks, since-launch reads, and receipts are capability-gated; shared profiles do not imply evidence parity.
