---
name: adsagent-reliability
description: Use when AdsAgent Meta, Google Ads, or TikTok MCP calls repeat, fan out, return partial data, queue work, exceed result budgets, or fail with stale-session, 429, 503, Retry-After, concurrency, or dependency signals.
argument-hint: "<retry, backoff, concurrency, MCP stability>"
version: 0.7.0
---

# AdsAgent Reliability

Use this for every non-trivial AdsAgent MCP session. Keep calls narrow, batch multi-scope work server-side, and branch on structured fields rather than message text.

## Query Plan

Ask for missing product/account/advertiser/customer and date scope. Do not silently broaden.
Read `setup_get_status.capabilities` before using optional consistency or recovery tools.

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never launch one overview request per scope. Use the server-side batch tool. Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero. Follow `meta.has_more` instead of inferring completion from item count.

For queued work, call `tasks_get_status(task_ref=...)` until `terminal=true`. Return the artifact metadata/link, never raw CSV or oversized rows.

## Client Limits

- Keep 4-6 in-flight calls per token.
- Cache initialize and tool discovery per transport.
- Never parallel-retry or rotate tokens to bypass a customer cap.
- Retry only reads/idempotent operations. Never automatically retry confirm or another consequential write.
- If a Meta write outcome is uncertain, use `operations_get` or `operations_get_context`; do not repeat the write.
- Parse backoff from the HTTP header, top-level `data`, and JSON-RPC `error.data`. Use [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Close transport, initialize without the stale session ID, re-list tools, retry one read once. Meta v2 is stateless and skips this flow. |
| 429 `mcp_fanout_detected` | Stop the loop. Batch current and pending scopes. Do not retry the blocked single-scope call. |
| 429 `mcp_concurrency_limited` | Treat as 429 concurrency: honor `Retry-After` plus jitter, reduce concurrency, retry one read serially. Token rotation does not fix customer scope. |
| 503 `dependency_unavailable` | Treat as 503 dependency unavailable: honor `Retry-After` plus jitter, retry one read within a small budget; keep session and token. |
| 409/410 confirm conflict | Do not retry. Re-prepare only if the user still wants the action. |

If retries exhaust, report the structured category and ask whether to retry later or narrow the request.

## Output

Return Markdown: direct answer, explicit scope, compact metric table, completeness/freshness, and next safe action. Do not expose raw JSON/CSV, stack traces, bearer tokens, internal IDs, task logs, or hidden diagnostics.

On `operator_review_required`, stop probing and ask the AdsAgent operator to inspect internal diagnostics.
