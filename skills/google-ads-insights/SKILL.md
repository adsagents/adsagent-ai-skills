---
name: google-ads-insights
description: Use when the user asks AdsAgent Google Ads MCP questions about Google Ads accounts, MCC, customer IDs, Search, PMax, spend, conversions, CPA, ROAS, campaigns, ad groups, ads, keywords, assets, or multi-account Google performance summaries.
---

# Google Ads Insights Through AdsAgent

Use Google Ads fields and tools only.

## First Steps

1. Run `setup_get_status` before analysis.
2. Inspect `setup_get_status.capabilities.agent_method_profile` before choosing a query tool.
3. Discover accessible Google Ads accounts with `google_ads_accounts_list`.
4. Choose an `enabled`, `non-manager` account; never analyze an MCC as a spend account.
5. Verify named customer IDs, and report customer/date/grouping.

## Freshness Boundary

Google is a read-only ledger; report `as_of` as observation time. Its public profile accepts only `consistency=cached` and does not advertise require_fresh, mutation receipts, since-launch, product refresh, public mutation tools, or live config verification. Internal receipt handling does not add a public MCP write capability.

## Query Pattern

- When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call its advertised `consistent_query_tool` once with root `query_contract_version=1`, `consistency=cached`, and exactly one `scope` or one ordered `scopes` batch up to advertised `max_scopes`.
- Trust top-level `complete=true`, ordered result contracts, and server `summary/total`; missing scopes are unknown, never zero.
- Follow returned `next_action` only; poll its task tool with exact `task_ref` and `poll_after_ms`. Consume a completed bounded terminal `result` directly; never rerun page 1 or invent a refresh task.
- Without the profile, use `google_ads_insights_overview_query` for one scope and `google_ads_insights_overview_batch` for multiple scopes.
- Do not create client-side fan-out by customer or date.
- If the server returns `mcp_fanout_detected`, stop the loop and combine current plus pending scopes through profile `insights_query_consistent` when advertised, otherwise `google_ads_insights_overview_batch`.
- For later pages, use the opaque continuation only through its advertised path. Keep customer, login-customer route, dates, grouping, filters, order, page size, and source snapshot unchanged. Never add Meta `min_as_of`.
- Never sum visible rows; distinguish rows shown from totals.

## Retry And Backoff

If Google Ads MCP returns `429` with `mcp_concurrency_limited`:

1. Honor `Retry-After + jitter`.
2. Retry serially within a small budget.
3. Prefer one profile `scopes` request or the native server-side batch tool instead of parallel calls.
4. Do not use token rotation or multiple sessions to bypass limits.

Parse backoff from the header, top-level `data`, or JSON-RPC `error.data`; never regex messages.

Treat `503` as dependency unavailable, not as a concurrency cap. Follow `/adsagent-reliability` for retry boundaries.

On `snapshot_expired` or continuation replay rejection, restart at page 1 with the same customer, dates, grouping, filters, and order, plus the original login-customer route and page size. Do not reuse the continuation, broaden scope, or fan out.

If Google Ads MCP returns `429` with `mcp_fanout_detected`, do not backoff-retry the same call. Switch to the profile batch shape or native batch overview tool.

## User-Facing Output

Return Markdown with a direct answer, customer/date/grouping, compact metrics table, `as_of`, completeness, and rows shown versus total. Do not dump raw JSON, diagnostics, schemas, or every field.

For explicit full-table/export requests, poll the returned task handle to terminal and return the artifact link instead of raw rows.
