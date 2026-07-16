---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
---

# Meta Insights Through AdsAgent

Use bounded aggregates and public handles. Never expose raw rows, schemas, or diagnostics.

## Scope And Routing

When scope is missing, run `setup_get_status`, then `products_list`; ask for scope and dates.

- One scope: `insights_query_overview`; multiple scopes: one `insights_query_batch_overview`. Native reads pass `metadata_contract_version=1`.
- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with root `query_contract_version=1`, `consistency=require_fresh`, and one scope or up to 20 ordered scopes.
- On `mcp_fanout_detected`, stop, batch current plus pending scopes, and do not retry the blocked call.

## Filtering And Metadata

For `insights_query_consistent`, use `page_size<=50` and allowlisted `filters`. All conditions are AND.

- Text `contains`/`prefix`/`eq`: hierarchy IDs/names, `pixel_id`, `app_id`.
- Number `gt`/`gte`/`lt`/`lte`/`eq`: metrics, `daily_budget`, `lifetime_budget`, `bid_amount`.
- Enum `eq`/`in`: statuses, `objective`, `optimization_goal`, `billing_event`, `conversion_event`, budget/bid/product/currency fields.

Read `adsagent://guide/metadata-contract` once per guide version. `configured_status` is `ACTIVE`/`PAUSED`; `effective_status` is Meta's outcome, including `DISAPPROVED`, `PENDING_REVIEW`, and parent-paused. Legacy `status` aliases `effective_status`; task/batch/notification/connection status is not delivery status.

Money uses returned account currency and `money_unit=major`. `budget_level` is `campaign|adset`; `bid_strategy` and `optimization_goal` are canonical lower-case. `objective` and `billing_event` are Meta-native uppercase; `conversion_event` is separate lower-case metadata.

With `group_by=ad`, preserve `ad_account_id`, `ad_account_name`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `ad_id`, and `ad_name`. Do not prefetch or fan out parents. Legacy `search` and `spend_gt` remain compatible; do not use `dedupe_by`. Exact Ad-name deduplication, language classification, and business grouping remain client-side.

For all matches, preserve each `ad_id`; advance pages serially while `data.meta.has_more=true`, keeping filters unchanged. Pin `min_as_of` to task `result.meta.source_observed_at` or immediate `result.query_contract.coverage.source_observed_at`; use the earliest multi-scope anchor. Never enlarge or parallelize pages. Large exhaustive output uses grouped `insights_export_csv` with identical filters.

On `adsagent_query_invalid`, correct the public field once. On `scope_unavailable`, do not infer another workspace/token or Meta permission. Run setup and matching discovery (`products_list` or `accounts_list_linked_accounts`) once; if still listed, retry the identical bounded read once. If it persists, stop and preserve `support_ref` for operator review. Never broaden scope or alter permissions.

## Completeness And Freshness

Report server totals; never sum pages. Native totals require `meta.complete=true`; profile totals require top-level `complete=true`. Missing scopes are unknown.

Poll distinct `task_ref` values serially with `tasks_get_status(task_ref=..., response_mode=compact)`. Consume only task `status=completed`, `result.status=complete`, and `result.meta.complete=true`; never rerun page 1. Stop otherwise.

`freshness_kind=age_only` is not mutation coverage. Do not decide on `verification_pending`, `data_not_fresh`, unknown launch date, or incomplete data.

## Verification And Output

After confirm, follow `next_action` to `overview_get_live_configs`; `config_verified_live` proves configuration. Stored Insights is ledger evidence. `after_mutation_ref=mutation_ref` covers post-write metrics and does not verify delivery configuration. Recover with `operations_get_context`; never repeat writes.

Keep Meta and MMP distinct. Poll exports to terminal and return the artifact, never raw CSV. Return concise Markdown with scope, metrics, completeness, and limits.
