---
name: tiktok-insights
description: Use when handling TikTok advertisers, insights, creative readiness, Quick Create, or append workflows.
---

# TikTok Through AdsAgent

## Start

1. Run `setup_get_status`.
2. Inspect `agent_method_profile` and `insights_query_contract`.
3. Discover the TikTok tenant and advertiser.

## Insights

- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with `query_contract_version=1` and one `scope` or ordered `scopes` up to `max_scopes`.
- Use `require_fresh` and `date_range_mode=since_launch` only when advertised by `insights_query_contract.consistency_modes`.
- Trust top-level `complete=true` and server summary/total; never sum visible rows. Missing scopes are unknown, never zero.
- Follow `next_action` with its `task_ref` and `poll_after_ms`; never resubmit. Consume terminal results only when `source_anchor` matches `result.source_snapshot`; never rerun page 1.
- Without it, use `insights_query_overview` for one scope and `insights_query_batch_overview` for many. Never client fan-out.
- On `mcp_fanout_detected`, combine scopes through the profile or batch.
- Later pages use the opaque continuation. Preserve tenant, advertiser, authorization route, dates, grouping, filters, order, page size, and source snapshot. It is single-use. Never add Meta `min_as_of`. On replay rejection or `snapshot_expired`, restart identical page 1 serially.
- Data may be age-only; immediate write success is not mutation verification. Never claim `config_verified_live` unless returned.

## Creative And Append

- Read `creatives_list` or `creatives_get`. Use local `creative_id` only when `readiness.create_eligible=true`.
- Inspect `readiness.status`, `readiness.reason_code`, `readiness.retryable`, `readiness.supported_ad_formats`, and `readiness.next_action`; legacy status alone is insufficient.
- For pending, `verification_pending`, or historical verification rows with `next_action=creatives_reconcile`, send 1..20 tenant-owned IDs once; never client-side fan out.
- Treat `upload_failed` as terminal for that upload attempt. Reconcile again only when the returned row is retryable and explicitly asks for it; otherwise report the redacted reason and follow its next action, including a new explicit upload when required.
- Give `campaigns_quick_create` one creative source: eligible local `creative_id`, or hosted-schema provider fields.
- `append_mode=append-campaign` plus only `target_campaign_id` creates one ad group and ad; omit `campaign_params`.
- `append_mode=append-adgroup` plus only `target_adgroup_id` creates one ad; omit campaign and ad-group params.
- Never supply both target IDs, guess by name, use Meta `append-adset`, or replace a prepared target.
- Show sanitized parents, inherited settings, creative count, ad name, and expiry. Get explicit approval. Confirm once, then poll.
- For uncertainty, call `operations_get` on the exact original route. Never replay or name-match.
- After a Hosted schema release, reconnect the MCP transport before trusting cached tool descriptions.

## Other Writes

Only with `mutation_receipts=true`: use advertised `delivery_prepare_tool`, `delivery_confirm_tool`, and `operation_get_tool` on the original route.

## Retry

- For `429` `mcp_concurrency_limited`, honor `Retry-After` plus jitter.
- For fan-out 429, switch to profile scopes or batch; do not repeat the single-scope loop.
- For `dependency_unavailable` with no `task_ref`, honor `retry_after_seconds`/`Retry-After` and retry the identical bounded read once. With a task, poll it.
- Treat HTTP `503` as dependency unavailable. Parse structured fields, never message text.

Answer with scope, compact metrics, freshness, completeness, and next safe action. Never dump raw JSON.
