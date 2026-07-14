---
name: adsagent-reliability
description: Use when AdsAgent Meta, Google Ads, or TikTok MCP calls repeat, fan out, return partial data, queue work, or fail with stale-session, 429, 503, Retry-After, concurrency, or dependency signals.
---

# AdsAgent Reliability

Use narrow calls, server-side batch work, and structured fields.

## Query Plan

Read `setup_get_status.capabilities`; never broaden scope. With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, use one `insights_query_consistent` request with root `query_contract_version=1` and bounded `scope` or ordered `scopes`.

Without that profile, use the native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never launch one overview per scope. Trust top-level `complete=true` in profile mode and `meta.complete=true` in native mode. Missing scopes are unknown; follow `meta.has_more`.

For queued work, follow `next_action` and `poll_after_ms`; use the advertised task tool, normally `tasks_get_status(task_ref=..., response_mode=compact)`, until terminal. For a Meta consistency refresh, consume the bounded task `result` directly only when task `status=completed`, `result.status=complete`, and `result.meta.complete=true`; never rerun page 1. Stop on a missing/incomplete result. Pin a later page's `min_as_of` to the task `result.meta.source_observed_at`, or to the immediate response's `result.query_contract.coverage.source_observed_at`; use the earliest first-page anchor for multiple scopes. Return artifact links, never raw rows.

## Client Limits

- Keep 4-6 calls in flight; cache discovery.
- Never parallel-retry or rotate tokens around a cap.
- Retry only reads/idempotent operations; never auto-retry confirm.
- After Meta writes, follow `next_action` to `overview_get_live_configs`; for uncertainty use `operations_get` or `operations_get_context`, never repeat the write.
- TikTok writes require advertised tools and `mutation_receipts=true`.
- Parse backoff from the header, top-level `data`, and JSON-RPC `error.data`; see [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect, re-list tools, retry one read once. Meta v2 skips this. |
| 429 `mcp_fanout_detected` | Stop; batch current and pending scopes. |
| 429 `mcp_concurrency_limited` | Treat as 429 concurrency; honor `Retry-After` plus jitter and retry one read serially. |
| 503 `dependency_unavailable` | Treat as 503 dependency unavailable; honor `Retry-After` plus jitter and retry one read within budget. |
| 410 `confirm_token_invalid` | Do not retry; re-prepare, show the fresh summary, and obtain approval. |
| `no_create_permission` | Send the user to `/dashboard/assets/fb-users`, then prepare again. |
| `scope_unavailable` | Stop and select a product/account linked to the current MCP tenant/token. This is not a Meta create-permission verdict; do not alter customer permissions. |

If retries exhaust, report the category. Never enable or modify customer permissions automatically.

## Output

Return Markdown with answer, scope, compact metrics, completeness, and next action. Never expose raw JSON/CSV, stack traces, bearer tokens, internal IDs, task logs, or diagnostics.

On `operator_review_required`, stop probing and ask the AdsAgent operator to inspect internal diagnostics. If the error includes `support_ref`, preserve and show that exact value; it is a non-authoritative lookup handle, so never modify, enumerate, or replace it with a token, raw request, or log.
