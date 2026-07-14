---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
---

# Meta Insights Through AdsAgent

Use bounded aggregate reads and public handles. Never expose raw rows, schemas, or diagnostics.

## Scope First

Run `setup_get_status`, then `products_list` when scope is missing. Ask for explicit scope and dates. Read only the needed guide topic.

## Totals And Completeness

Report server `summary`/`totals`; never sum pages. Trust native totals only with `meta.complete=true`, follow `meta.has_more`, and treat missing scopes as unknown.

## Query Routing

- One scope -> `insights_query_overview`; multiple scopes -> one `insights_query_batch_overview`.
- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once using root `query_contract_version=1`, `consistency=require_fresh`, and one scope or up to 20 ordered scopes.
- `mcp_fanout_detected` -> stop the loop, batch current plus pending scopes, and do not retry the blocked call.

## Structured Candidate Filtering

For `insights_query_consistent`, use `page_size<=50` and allowlisted `filters`. All conditions are AND; each has only `field`, `op`, and `value`.

- Text `contains`/`prefix`/`eq`: applicable hierarchy IDs/names, `pixel_id`, `app_id`.
- Number `gt`/`gte`/`lt`/`lte`/`eq`: metrics, `daily_budget`, `lifetime_budget`, `bid_amount`.
- Enum `eq`/`in`: statuses, `objective`, `optimization_goal`, `billing_event`, `conversion_event`, budget/bid/product/currency fields.

`configured_status` is `ACTIVE`/`PAUSED`; `effective_status` is Meta's actual outcome, including `DISAPPROVED`, `PENDING_REVIEW`, and parent-paused. Legacy `status` aliases `effective_status`.

With `group_by=ad`, preserve `ad_account_id`, `ad_account_name`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `ad_id`, and `ad_name`. Do not prefetch or fan out parents. Legacy `search` and `spend_gt` remain compatible, but do not use `dedupe_by` in new workflows. Exact Ad-name deduplication, language classification, and business grouping are client-side.

For all matches, preserve each `ad_id`; advance `page` serially while `data.meta.has_more=true`. Keep filters unchanged. Pin `min_as_of` to task `result.meta.source_observed_at` or immediate `result.query_contract.coverage.source_observed_at`; use the earliest multi-scope anchor. Never enlarge or parallelize pages. For large exhaustive output, call grouped `insights_export_csv` with identical filters and consume the artifact.

On `adsagent_query_invalid`, correct the named public field once. On `scope_unavailable`, choose via `products_list` for the current tenant/token. It is not a Meta create-permission verdict; never alter permissions.

In profile mode trust only top-level `complete=true`. Poll distinct `task_ref` values serially with `tasks_get_status(task_ref=..., response_mode=compact)`. Consume a terminal result only when task `status=completed`, `result.status=complete`, and `result.meta.complete=true`; never rerun page 1. Stop otherwise.

`freshness_kind=age_only` is not mutation coverage. Do not decide on `verification_pending`, `data_not_fresh`, unknown launch date, or incomplete data.

## Write Verification And Recovery

After confirm, follow `next_action` to `overview_get_live_configs`; `config_verified_live` proves configuration. `after_mutation_ref=mutation_ref` is for post-write metrics and does not verify delivery configuration. Recover with `operations_get_context`; never repeat writes.

## MMP

Keep Meta and MMP distinct; report partial channels.

## Export

Poll export `tasks_get_status(task_ref=...)` to terminal; return the artifact, never raw CSV.

## Output

Return concise Markdown with scope, metrics, completeness, and limits.
