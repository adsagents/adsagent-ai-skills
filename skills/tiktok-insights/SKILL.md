---
name: tiktok-insights
description: Use when handling TikTok advertisers, insights, creative readiness, Quick Create, or append workflows.
---

# TikTok Through AdsAgent

## Start

1. Run `setup_get_status`.
2. Inspect capabilities; discover the tenant and advertiser.

## Insights

- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once using `query_contract_version=1` and one `scope` or ordered `scopes` within `max_scopes`.
- Use `require_fresh` and `date_range_mode=since_launch` only when advertised by `insights_query_contract.consistency_modes`.
- Trust top-level `complete=true` and server summary/total; never sum visible rows. Missing scopes are unknown.
- Follow `next_action`, `task_ref`, and `poll_after_ms`; never resubmit. Consume matching `source_anchor`/`result.source_snapshot`; never rerun page 1.
- Without it, use `insights_query_overview` for one scope and `insights_query_batch_overview` for many. Never client fan-out.
- On `mcp_fanout_detected`, combine scopes through the profile or batch.
- The opaque continuation is single-use; preserve tenant, advertiser, authorization route, dates, grouping, filters, order, page size, and source snapshot. Never add Meta `min_as_of`. Replay rejection or `snapshot_expired` restarts identical page 1 serially.
- Data may be age-only; immediate write success is not mutation verification. Never claim `config_verified_live` unless returned.

## Creative And Append

- Read `creatives_list` or `creatives_get`; use local `creative_id` only when `readiness.create_eligible=true`.
- Inspect `readiness.reason_code`, `readiness.retryable`, formats, and `readiness.next_action`; legacy status is insufficient.
- For pending, `verification_pending`, or historical verification with `next_action=creatives_reconcile`, send 1..20 tenant-owned IDs once; never client-side fan out.
- `upload_failed` is terminal. Reconcile only when instructed; otherwise follow remediation, including a new explicit upload.
- Give `campaigns_quick_create` one creative source: eligible local `creative_id`, or hosted-schema provider fields.
- `append_mode=append-campaign` + `target_campaign_id` creates ad group/ad; `append_mode=append-adgroup` + `target_adgroup_id` creates ad only. Omit parent params.
- Never supply both target IDs, guess names, use Meta `append-adset`, or replace prepared targets.
- Show sanitized parents, settings, creative count, name, and expiry. Get explicit approval. Confirm once.
- Poll returned opaque `ttask_*` via `tasks_get_status(task_ref=..., response_mode=compact)`. `task_id` is legacy, not an alias. For a historically mislabeled UUID, pass it once and use the corrected ref.
- Consume terminal `results.created_objects` and `results.failures`. Empty objects plus `failed_proven` means none acknowledged. Preserve `support_ref`; prepare anew, never replay.
- For uncertainty, call `operations_get` on the exact original route. Never replay or name-match.
- After a Hosted schema release, reconnect the MCP transport before trusting cached tool descriptions.

## Other Writes

Only with `mutation_receipts=true`: use advertised `delivery_prepare_tool`, `delivery_confirm_tool`, and `operation_get_tool` on the original route.

## Retry

- For `429` `mcp_concurrency_limited`, honor `Retry-After` plus jitter.
- For fan-out 429, switch to profile scopes or batch; do not repeat the single-scope loop.
- For `dependency_unavailable` with no `task_ref`, honor `retry_after_seconds`/`Retry-After` and retry the identical bounded read once. With a task, poll it.
- Treat HTTP `503` as dependency unavailable. Parse structured fields, never message text.

Return compact evidence and the next safe action, never raw JSON.
