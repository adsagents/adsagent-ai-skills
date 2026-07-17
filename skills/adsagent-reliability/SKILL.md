---
name: adsagent-reliability
description: Use when AdsAgent Meta, Google Ads, or TikTok MCP calls repeat, fan out, return partial data, queue work, or fail with stale-session, 429, 503, Retry-After, concurrency, or dependency signals.
---

# AdsAgent Reliability

Use server-side batch.

## Query Plan

Read `setup_get_status.capabilities`; never broaden scope. With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, send one `insights_query_consistent` request using root `query_contract_version=1` and bounded `scope` or `scopes`.

Otherwise use native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never launch one overview per scope. Trust top-level `complete=true` in profile mode or `meta.complete=true` natively.

For Meta, combine allowlisted AND `filters`; never fan out by Campaign/Ad. Correct `adsagent_query_invalid` once.

For queued work, follow advertised `next_action`/`poll_after_ms`; Meta uses `tasks_get_status(task_ref=..., response_mode=compact)`. At `terminal=true`, consume bounded `result` when completion and source-anchor checks pass; never rerun page 1. Pin pages to that anchor. Return artifact links, not rows.

## Client Limits

- Keep 4-6 calls in flight; cache discovery.
- Never parallel-retry, rotate tokens around caps, or auto-retry confirm.
- Retry only reads/idempotent operations.
- After Meta writes, follow `next_action` to `overview_get_live_configs`; for task-write uncertainty use `operations_get_context(task_ref=...)`, never replay the write.
- TikTok writes require advertised tools and `mutation_receipts=true`.
- Parse backoff from headers, top-level `data`, and JSON-RPC `error.data`; see [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect, re-list, retry one read once. |
| 429 `mcp_fanout_detected` | Stop; batch current and pending scopes. |
| 429 `mcp_concurrency_limited` | Treat as 429 concurrency; honor `Retry-After` plus jitter and retry one read serially. |
| 503 dependency unavailable / `dependency_unavailable` | Treat HTTP 503 or a structured tool error alike. Without `task_ref`, honor `retry_after_seconds`/`Retry-After` plus jitter and retry the identical bounded read once. With `task_ref`, poll only that task. Never fan out. |
| `snapshot_expired` | Restart at page 1 with the same scope, dates, filters, grouping, and order. Do not reuse the continuation or broaden/fan out. |
| 410 `confirm_token_invalid` | Do not retry; re-prepare, show the fresh summary, and obtain approval. |
| `no_create_permission` | Send the user to `/dashboard/assets/fb-users`, then prepare again. |
| `adsagent_request_incomplete` + public `invalid_fields` | Correct advertised prepare fields and rerun prepare once. Never reuse/call a confirm token; on repeat, preserve `support_ref` and stop. |
| `scope_unavailable` | Do not infer workspace/token or Meta permissions. Run setup and matching discovery once; retry the identical bounded read once only if scope remains listed, then preserve `support_ref`. Never broaden scope or alter permissions. |

If retry fails, report the category. Never modify customer permissions automatically.

## Output

Return Markdown with scope, metrics, completeness, and next action. Never expose raw JSON/CSV, stack traces, tokens, task logs, or diagnostics.

On `operator_review_required`, stop probing. Preserve `support_ref` verbatim; it is not authorization. Never replace it with a token, raw request, or log.
