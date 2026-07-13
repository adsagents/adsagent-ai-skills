---
name: adsagent-reliability
description: Use when AdsAgent Meta, Google Ads, or TikTok MCP calls repeat, fan out, return partial data, queue work, or fail with stale-session, 429, 503, Retry-After, concurrency, or dependency signals.
---

# AdsAgent Reliability

Keep calls narrow, use server-side batch work, and branch on structured fields.

## Query Plan

Ask for missing entity/date scope; never broaden silently. Read `setup_get_status.capabilities`. With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, use one `insights_query_consistent` request with root `query_contract_version=1` and one `scope` or ordered `scopes` within `max_scopes`.

Without that profile, use the native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never launch one overview per scope. In profile mode, trust only top-level `complete=true` and each ordered result's contract. In native mode, trust `meta.complete=true`. Missing scopes are unknown, never zero; follow `meta.has_more`.

For queued work, follow `next_action` and `poll_after_ms`; call the advertised task tool, normally `tasks_get_status(task_ref=..., response_mode=compact)`, until `terminal=true`. Compact responses preserve safe codes such as `no_create_permission`. Return artifact links, never raw rows.

## Client Limits

- Keep 4-6 calls in flight; cache initialize/tool discovery.
- Never parallel-retry or rotate tokens around a cap.
- Retry only reads/idempotent operations; never auto-retry confirm.
- After an accepted Meta write, follow read-only `next_action` to `overview_get_live_configs`; retry only while verification is pending.
- For uncertain Meta writes, use `operations_get` or `operations_get_context`; never repeat the write. An Insights watermark does not verify delivery configuration.
- For TikTok writes, use advertised prepare/confirm/recovery tools only when `mutation_receipts=true`; shared names do not imply Meta evidence.
- Parse backoff from the HTTP header, top-level `data`, and JSON-RPC `error.data`. Use [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect without the stale session ID, re-list tools, retry one read once. Meta v2 skips this. |
| 429 `mcp_fanout_detected` | Stop the loop. Batch current and pending scopes. Do not retry the blocked single-scope call. |
| 429 `mcp_concurrency_limited` | Treat as 429 concurrency; honor `Retry-After` plus jitter and retry one read serially. |
| 503 `dependency_unavailable` | Treat as 503 dependency unavailable; honor `Retry-After` plus jitter and retry one read within budget. |
| 410 `confirm_token_invalid` | Do not retry confirm. A single-use token may be expired, used, or rejected. Re-prepare, show the fresh summary, and obtain explicit approval again. |
| `no_create_permission` | Do not retry the task. Send the user to `/dashboard/assets/fb-users` to enable Create on an active eligible connection, then prepare again. |

If retries exhaust, report the category and narrow or retry later.

Never enable or modify customer permissions automatically.

## Output

Return Markdown: direct answer, explicit scope, compact metric table, completeness/freshness, and next safe action. Do not expose raw JSON/CSV, stack traces, bearer tokens, internal IDs, task logs, or hidden diagnostics.

On `operator_review_required`, stop probing and ask the AdsAgent operator to inspect internal diagnostics.
