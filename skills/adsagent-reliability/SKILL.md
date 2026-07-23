---
name: adsagent-reliability
description: Use when AdsAgent MCP repeats, fans out, queues, returns partial data, or signals session, 429, 503, Retry-After, or dependency failures.
---

# AdsAgent Reliability

Use server-side batch.

## Query Plan

Read `setup_get_status.capabilities`. For `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call one root `query_contract_version=1` `insights_query_consistent`.

Native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never fan out. Trust top-level `complete=true` in profile mode; otherwise trust `meta.complete=true`.

For Meta, combine AND `filters`; correct `adsagent_query_invalid` once.

Poll advertised `next_action`; Meta uses `tasks_get_status(task_ref=..., response_mode=compact)`. At `terminal=true`, consume `result`; never rerun page 1. Report `result.failures.items`, obey `automatic_retry_allowed`, `manual_new_task_allowed`, and `operator_review_required`, and stop on unclassified failures.

For terminal export, GET `result.artifact.download_url` byte-for-byte. Never rewrite it. `artifact_status=expired` requires a new export.

Meta keeps page/`min_as_of`; Google/TikTok keep opaque continuation and snapshot. Never move Meta `min_as_of` into Google or TikTok requests.

## Client Limits

- Cache discovery; keep 4-6 calls.
- Retry only reads/idempotent operations; never parallel-retry, rotate tokens, or replay confirm.
- After Meta writes, follow `next_action` to `overview_get_live_configs`; recover via `operations_get_context(task_ref=...)`.
- Bulk Meta Ad writes may use configurable sequential chunks, not evidence of a fixed Meta limit. Preserve acknowledged objects; `manual_new_task_allowed=true` requires a fresh task and approval.
- `meta_write_rejected` or `verified_not_created` is eligible only when flags permit. Reuse `verified_created`; keep `meta_write_verification_pending` or `verification_ambiguous` in `operations_get_context`, never replay.
- TikTok writes require advertised tools and `mutation_receipts=true`; recover on the original authorization route.
- Parse backoff from headers, `data`, and `error.data`; see [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect, re-list, retry one read. |
| 429 `mcp_fanout_detected` | Stop; batch pending scopes. |
| 429 `mcp_concurrency_limited` / 429 concurrency | Honor `Retry-After` plus jitter; retry one read serially. |
| 503 dependency unavailable structured tool error | Without `task_ref`, honor `retry_after_seconds` and retry the identical bounded read once; otherwise poll that task. |
| `snapshot_expired` / replayed continuation | Restart page 1 unchanged. Do not reuse the continuation or broaden. |
| 410 `confirm_token_invalid` | Do not retry; re-prepare, show the fresh summary, and obtain approval. |
| `mcp_meta_quota_deferred` with `request_sent=false`, `safe_to_retry=true`, `operator_review_required=false` | STOP before later confirms; preserve `completed_mutations`/`not_sent_mutations`/`remaining_mutations`/`safe_resume_from`/`support_refs`; wait; re-prepare unchanged remainder; fresh approval. See [meta-quota-plan.md](meta-quota-plan.md). |
| `no_create_permission` | Send the user to `/dashboard/assets/fb-users`, then prepare again. |
| `adsagent_request_incomplete` + `invalid_fields` | Correct public fields and prepare once; on repeat preserve `support_ref`. |
| `scope_unavailable` | Do not infer permissions. Discover once; retry only if still listed. Never alter permissions. |

If retries fail, report the category. Sent/uncertain writes use operation recovery, never replay or modify permissions.

## Output

Return Markdown with scope, metrics, completeness, and next action. Never expose tokens or diagnostics.

On `operator_review_required`, stop. Preserve `support_ref`; it is not authorization and never replaces a token, request, or log.
