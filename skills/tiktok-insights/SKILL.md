---
name: tiktok-insights
description: Use when the user asks AdsAgent TikTok MCP questions about TikTok advertisers, tenants, TT accounts, campaign/ad group/ad performance, spend, conversions, CPA, ROAS, impressions, clicks, or multi-advertiser TikTok summaries.
---

# TikTok Insights Through AdsAgent

Use TikTok tenant, advertiser, and metric fields only.

## First Steps

1. Run `setup_get_status` before analysis.
2. Inspect `setup_get_status.capabilities.agent_method_profile` and `insights_query_contract`.
3. Discover TikTok tenant and advertiser scopes; never assume Meta or Google identifiers.
4. Verify the requested advertiser, then report advertiser/date/grouping.

## Freshness And Write Boundary

Capabilities are independently gated. Use `require_fresh`, `since_launch`, direct `task_ref`, or receipts only when advertised. Report evidence exactly: age-only data or immediate write success is not mutation verification, and TikTok receipts do not imply Meta verification.

## Query Pattern

- When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call its advertised `consistent_query_tool` once with root `query_contract_version=1` and exactly one `scope` or one ordered `scopes` batch up to advertised `max_scopes`.
- Use `consistency=require_fresh` only when `insights_query_contract.consistency_modes` advertises it. Use `date_range_mode=since_launch` only when profile `since_launch=true` and the grouping supports it.
- Trust top-level `complete=true`, ordered result contracts, and server summary/total; missing scopes are unknown, never zero.
- Follow `next_action` using the advertised task tool, exact `task_ref`, and `poll_after_ms`; never resubmit pending work. At `terminal=true`, consume the bounded `result` directly only when completed and its `source_anchor` matches `result.source_snapshot`; never rerun page 1.
- Without the profile, use `insights_query_overview` for one scope and `insights_query_batch_overview` for multiple scopes.
- Do not create client-side fan-out by advertiser.
- If the server returns `mcp_fanout_detected`, stop the loop and combine current plus pending scopes through profile `insights_query_consistent` when advertised, otherwise `insights_query_batch_overview`.
- Never sum visible rows; distinguish them from server totals.

## Write Recovery

Only with profile `mutation_receipts=true` and all tool names: use `delivery_prepare_tool`, confirm once with `delivery_confirm_tool`, and recover through `operation_get_tool`. Never replay or claim `config_verified_live` unless returned.

## Retry And Backoff

- For `429` `mcp_concurrency_limited`, honor `Retry-After` plus jitter and retry serially.
- For `429` with `mcp_fanout_detected`, do not retry the same single-scope request; switch to profile `scopes` or `insights_query_batch_overview`.
- For structured `dependency_unavailable` with no `task_ref`, honor `retry_after_seconds`/`Retry-After` and retry the identical bounded read once. Do not poll, fan out, or invent a task. With a `task_ref`, poll only that task.
- For HTTP `503`, follow `/adsagent-reliability` as dependency unavailable.
- Prefer one profile `scopes` request or `insights_query_batch_overview` before parallel reads.
- Parse backoff from headers, top-level `data`, or JSON-RPC `error.data`; never regex messages.

## User-Facing Output

Return Markdown with a direct answer, scope, compact metrics table, freshness, completeness, and next safe action. Never dump raw JSON, diagnostics, catalogs, schemas, or rows. For explicit full exports, poll the task to terminal and return its artifact link.
