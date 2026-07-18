---
name: adsagent-reliability
description: Use when AdsAgent MCP repeats, fans out, queues, returns partial data, or fails with session, 429, 503, Retry-After, or dependency signals.
---

# AdsAgent Reliability

Use server-side batch.

## Query Plan

Read `setup_get_status.capabilities`; never broaden scope. With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, send one `insights_query_consistent` request with root `query_contract_version=1` and bounded `scope` or `scopes`.

Otherwise use native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never launch one overview per scope. Trust top-level `complete=true` in profile mode or `meta.complete=true` natively.

For Meta, combine allowlisted AND `filters`; never fan out by Campaign/Ad. Correct `adsagent_query_invalid` once.

For queued work, follow `next_action`/`poll_after_ms`; Meta uses `tasks_get_status(task_ref=..., response_mode=compact)`. At `terminal=true`, consume `result`; never rerun page 1. Return artifact links.

Pagination is platform-specific. Meta keeps page and `min_as_of`; Google/TikTok keep opaque continuation, route, query shape, page size, and source snapshot. Never move Meta `min_as_of` into Google or TikTok requests or parallelize pages.

## Client Limits

- Cache discovery; keep 4-6 calls.
- Never parallel-retry, rotate tokens around caps, or retry confirm.
- Retry only reads/idempotent operations.
- After Meta writes, follow `next_action` to `overview_get_live_configs`; recover uncertainty with `operations_get_context(task_ref=...)`, never replay.
- TikTok writes require advertised tools and `mutation_receipts=true`; recover on the original authorization route, never by name-match or replay.
- Parse backoff from headers, top-level `data`, and JSON-RPC `error.data`; see [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect, re-list, retry one read once. |
| 429 `mcp_fanout_detected` | Stop; batch current and pending scopes. |
| 429 `mcp_concurrency_limited` | Treat as 429 concurrency; honor `Retry-After` plus jitter and retry one read serially. |
| 503 dependency unavailable / `dependency_unavailable` structured tool error | Without `task_ref`, honor `retry_after_seconds`/`Retry-After` and retry the identical bounded read once. With `task_ref`, poll only it. Never fan out. |
| `snapshot_expired` or continuation replay rejection | Restart at page 1 with the same route, scope, dates, filters, grouping, order, and page size. Do not reuse the continuation or broaden/fan out. |
| 410 `confirm_token_invalid` | Do not retry; re-prepare, show the fresh summary, and obtain approval. |
| `no_create_permission` | Send the user to `/dashboard/assets/fb-users`, then prepare again. |
| `adsagent_request_incomplete` + public `invalid_fields` | Correct advertised prepare fields and rerun prepare once. Never reuse/call a confirm token; on repeat, preserve `support_ref` and stop. |
| `scope_unavailable` | Do not infer workspace/token or Meta permissions. Run setup/discovery once; retry once only if scope remains listed, then preserve `support_ref`. Never broaden or alter permissions. |

If retry fails, report the category. Never modify customer permissions automatically.

## Output

Return Markdown with scope, metrics, completeness, and next action. Never expose raw data, traces, tokens, logs, or diagnostics.

On `operator_review_required`, stop probing. Preserve `support_ref` verbatim; it is not authorization. Never replace it with a token, raw request, or log.
