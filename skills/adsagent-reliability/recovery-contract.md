# AdsAgent Recovery Contract

## Query Plan

Use server-side batch.

Read `setup_get_status.capabilities`. For `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call one root `query_contract_version=1` `insights_query_consistent`.

Native fallback:

| Platform | One scope | Multiple scopes |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Never fan out. Trust top-level `complete=true` in profile mode; otherwise trust `meta.complete=true`. For Meta, combine AND `filters`; correct `adsagent_query_invalid` once.

Poll advertised `next_action`; Meta uses `tasks_get_status(task_ref=..., response_mode=compact)`. At `terminal=true`, consume `result`; never rerun page 1. For create/copy, require `result.create_reconciliation.reconciled=true` before claiming complete accounting. Map `creative_results` to created IDs, then report `result.failures.items`, obey retry/review flags, and stop on unclassified failures.

For terminal export, GET `result.artifact.download_url` byte-for-byte. `artifact_status=expired` requires export. Keep opaque continuation. Never move Meta `min_as_of` into Google or TikTok requests.

## Client Limits

- Let the MCP client negotiate the protocol. Modern `2026-07-28` uses stateless
  `server/discover`; session recovery is legacy-only and begins only from a
  structured `mcp_session_not_found` response. Never
  invent protocol/session headers, re-register, or replace a bearer solely
  because the guide or protocol changed.
- Retry only reads/idempotent operations; never parallel-retry or replay confirm.
- After Meta writes, follow `next_action` to `overview_get_live_configs`; recover via `operations_get_context(task_ref=...)`.
- Bulk Meta Ad writes may use configurable sequential chunks, not evidence of a fixed Meta limit. Preserve acknowledged objects; `manual_new_task_allowed=true` requires a fresh task and approval.
- `operations_get_context(response_mode=compact)` returns receipt totals, create reconciliation, and anomalous receipts. Use `standard` only when every receipt is required.
- A failed auxiliary `adimages` receipt marked `workflow_status=recovered_by_url_fallback` is compensated, has no final-Ad impact, and never authorizes retry or a new task.
- `meta_write_rejected` or `verified_not_created` is eligible only when flags permit. Reuse `verified_created`; keep `meta_write_verification_pending` or `verification_ambiguous` in `operations_get_context`, never replay.
- TikTok writes require advertised tools and `mutation_receipts=true`; recover on the original route.
- Parse backoff from headers, `data`, and `error.data`; see [retry-parser.md](retry-parser.md).

## Recovery Matrix

| Signal | Required action |
| --- | --- |
| Legacy 404 `mcp_session_not_found` + `discard_session_and_initialize` | Reconnect the existing transport, re-list, retry one read. Never apply this branch to modern stateless MCP. |
| 429 `mcp_fanout_detected` | Stop; batch pending scopes. |
| 429 `mcp_concurrency_limited` / 429 concurrency | Honor `Retry-After` plus jitter; retry one read serially. |
| 503 dependency unavailable structured tool error | Without `task_ref`, honor `retry_after_seconds` and retry the identical bounded read once; otherwise poll that task. |
| `snapshot_expired` / replayed continuation | Restart page 1 unchanged. Do not reuse the continuation or broaden. |
| `read_query_too_large` with `operator_review_required=false` | Do not escalate or repeat unchanged. Narrow the query; for one known entity use direct prepare or one typed `overview_get_live_configs` preflight; use export only for an explicitly requested large table. |
| 410 `confirm_token_invalid` | Do not retry; re-prepare, show the fresh summary, and obtain approval. |
| `mcp_meta_quota_deferred` with `request_sent=false`, `safe_to_retry=true`, `operator_review_required=false` | STOP before later confirms; preserve `completed_mutations`/`not_sent_mutations`/`remaining_mutations`/`safe_resume_from`/`support_refs`; wait; re-prepare unchanged remainder; fresh approval. See [meta-quota-plan.md](meta-quota-plan.md). |
| `no_create_permission` | Send the user to `/dashboard/assets/fb-users`, then prepare again. |
| Prepare call: `adsagent_request_incomplete` + `invalid_fields` | Correct public fields and prepare once; on repeat preserve any returned `support_ref`. |
| Rejected Meta template direct write, with or without bounded public fields | Stop; show fields if returned; any later template write is a new explicit request. Preserve `support_ref` when present, report when absent, and never infer a hidden schema or replay. |
| Indeterminate Meta template direct write without task/operation recovery | Never replay. Perform at most one exact-name template read-back when advertised; remain outcome-unknown without authoritative write-bound evidence, then hand off. |
| `scope_unavailable` | Do not infer permissions. Discover once; retry only if still listed. Never alter permissions. |

If retries fail, report the category. Task/operation-backed sent or uncertain
writes use operation recovery; indeterminate Meta template direct writes
follow the row above. On `operator_review_required`, stop, preserve any
returned `support_ref` and report when absent; it is not authorization.
