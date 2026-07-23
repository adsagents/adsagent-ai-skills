---
name: tiktok-insights
description: Use when the user asks AdsAgent TikTok questions about advertisers, insights, creative readiness, Quick Create, or appending to an existing campaign or ad group.
---

# TikTok Through AdsAgent

Keep TikTok tenant, advertiser, hierarchy, and metric semantics.

## Start

1. Run `setup_get_status`.
2. Inspect `agent_method_profile` and `insights_query_contract`.
3. Discover the tenant and advertiser; never assume Meta or Google identifiers.

## Insights

- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with root `query_contract_version=1` and exactly one `scope` or ordered `scopes` batch up to advertised `max_scopes`.
- Use `require_fresh` only when `insights_query_contract.consistency_modes` advertises it; use `date_range_mode=since_launch` only when supported.
- Trust top-level `complete=true` and server summary/total; never sum visible rows. Missing scopes are unknown, never zero.
- Follow `next_action` with the exact `task_ref` and `poll_after_ms`; never resubmit pending work. At terminal completion consume the bounded result only when `source_anchor` matches `result.source_snapshot`; never rerun page 1.
- Without the profile, use `insights_query_overview` for one scope and `insights_query_batch_overview` for many. Never client fan-out.
- On `mcp_fanout_detected`, combine scopes through the profile or batch tool.
- Later pages use the opaque continuation through its advertised path. Preserve tenant, advertiser, authorization route, dates, grouping, filters, order, page size, and source snapshot. It is single-use. Never add Meta `min_as_of`. On replay rejection or `snapshot_expired`, restart identical page 1 serially.
- Data may be age-only; immediate write success is not mutation verification. Never claim `config_verified_live` unless returned.

## Creative And Append

- Read `creatives_list` or `creatives_get`. Use local `creative_id` only when `readiness.create_eligible=true`.
- For `readiness.status=verification_pending`, call `creatives_confirm_upload` once. Stop on failure; never auto-retry.
- Give `campaigns_quick_create` one creative source: verified local `creative_id`, or hosted-schema provider fields. Local media syncs only after explicit confirm.
- `append_mode=append-campaign` plus only `target_campaign_id` creates one ad group and ad; omit `campaign_params`.
- `append_mode=append-adgroup` plus only `target_adgroup_id` creates one ad; omit campaign and ad-group params.
- Never supply both target IDs, guess by name, use Meta `append-adset`, or replace a prepared target.
- Show the sanitized parents, inherited settings, creative count, ad name, and expiry. Obtain explicit approval. Confirm once, then poll the returned task/receipt.
- For uncertainty, call `operations_get` on the exact original route. Never replay or name-match.
- After a Hosted schema release, reconnect the MCP transport before trusting cached tool descriptions.

## Other Writes

Only with `mutation_receipts=true` and advertised names: call `delivery_prepare_tool`, obtain approval, call `delivery_confirm_tool` once, then recover with `operation_get_tool` on the original route. Never switch credentials.

## Retry

- For `429` `mcp_concurrency_limited`, honor `Retry-After` plus jitter.
- For fan-out 429, switch to profile scopes or batch; do not repeat the single-scope loop.
- For `dependency_unavailable` with no `task_ref`, honor `retry_after_seconds`/`Retry-After` and retry the identical bounded read once. With a task, poll only it.
- Treat HTTP `503` as dependency unavailable. Parse structured fields, never message text.

Answer in Markdown with scope, compact metrics, freshness, completeness, and next safe action. Never dump raw JSON. Return artifact links only for requested exports.
