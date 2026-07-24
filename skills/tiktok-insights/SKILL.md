---
name: tiktok-insights
description: Use when handling TikTok insights, creatives, create/append, management, copy, optimization, support, or MMP.
---

# TikTok Through AdsAgent

## Start And Read

- Run `setup_get_status`; inspect capability names before advertiser discovery.
- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with `query_contract_version=1` and one `scope` or ordered `scopes`. Otherwise use `insights_query_overview` or `insights_query_batch_overview`; never client-side fan out.
- Use `date_range_mode=since_launch` or `require_fresh` only when listed by `insights_query_contract.consistency_modes`. Trust top-level `complete=true` and server summary/total; missing scopes are unknown.
- Poll returned `task_ref`; consume terminal `source_anchor`/`result.source_snapshot` directly and never rerun page 1.
- The opaque continuation is single-use. Preserve tenant, advertiser, authorization route, dates, grouping, filters, order, page size, and source snapshot. Never add Meta `min_as_of`. On `snapshot_expired` or replay rejection, restart identical page 1 serially.
- On 503 `dependency_unavailable` with no `task_ref`, honor `retry_after_seconds`/Retry-After and retry the identical bounded read once. For 429 fan-out, use one batch; immediate write success is not mutation verification or `config_verified_live`; age-only data is limited.

## Creative And Create

- Use local `creative_id` only with `readiness.create_eligible=true`; inspect `readiness.reason_code`, `readiness.retryable`, and `readiness.next_action`.
- Send 1..20 requested `verification_pending` IDs once to `creatives_reconcile`. `upload_failed` needs returned remediation and a new explicit upload. Use advertised `creatives_abandon_upload` to remove a cancelled pending attempt, not provider media.
- Give `campaigns_quick_create` one source. `append_mode=append-campaign` plus `target_campaign_id` creates ad group/ad; `append_mode=append-adgroup` plus `target_adgroup_id` creates ad only.
- For Smart+ image, the server verifies ownership and maps `creative_info.image_info[].web_uri`. Do not send a CDN image URL, synthesize `CAROUSEL_ADS`, or invent provider CTA, music, or identity IDs.
- Never supply both target IDs, guess names, use Meta `append-adset`, or replace prepared parents. Show sanitized parents, settings, count, expiry, and `call_to_action_configured`; get explicit approval. Confirm once.
- Use `task_ref` only for `tasks_get_status`. Use canonical `operation_ref` only for `operations_get` on the original route. `failed_proven` needs corrected input, new prepare, and fresh approval. Never replay; reconnect the MCP transport after Hosted schema release.

## Receipt Workflows

- Require `mutation_receipts=true` and exact advertised names: `delivery_prepare_tool`, `delivery_confirm_tool`, `operation_get_tool`, budget/bid, copy/clone/recreate prepares and confirms.
- Read `overview_get_live_configs`; keep configured/effective/operation status, budget, bid, currency, receipt, and metrics distinct. TikTok money is decimal advertiser-currency major units; bid is native `ad_group` scoped.
- `copy_ad_quick_copy`, `copy_ad_clone_structure`, and `campaigns_recreate_from_task` are same-advertiser only. One approval/task covers 1..20 grouped items with item receipts and disabled initial delivery. Reject cross-advertiser transfer, failed/partial/foreign sources, name matching, and uncertain replay.
- Every write is prepare, sanitized review, explicit approval, confirm once, then exact-route recovery.

## Optimization, MMP, Support

- With `agent_method_profile.optimization.available=true`, `optimization_evaluate` creates complete-evidence recommendations, not mutations. Read `notifications_list`; `optimization_prepare_action` starts a new approved management flow; never auto-confirm; notifications are in-app only.
- With `mmp_product_aggregate_reads.available=true`, use one `mmp_insights_get_product_event_today` or `mmp_insights_query_product_event_summary`. The server fixes `channel_pid=tiktokglobal_int`; never fan out. AppsFlyer `adset` is an adapter source field for native `ad_group`.
- When `support_reporting.mode=manual_only`, call `support_report_error` only on explicit intent with an existing `support_ref`; poll `support_get_report_status`. Never include prompts, tokens, advertiser IDs, bodies, provider responses, descriptions, or logs.

Return compact evidence and the next safe action, never raw JSON.
