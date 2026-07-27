# Meta Insights Query Contract

Use bounded aggregates and public handles. Never expose rows, schemas, or diagnostics.

## Scope And Routing

Missing scope: run `setup_get_status`, then `products_list`; ask for scope and dates.

- One scope: `insights_query_overview`; multiple scopes: one `insights_query_batch_overview`. Native reads pass `metadata_contract_version=1`.
- With `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with root `query_contract_version=1`, `consistency=require_fresh`, and one scope or up to 20 ordered scopes.
- On `mcp_fanout_detected`, stop, batch current plus pending scopes, and do not retry the blocked call.

## Filtering And Metadata

For `insights_query_consistent`, use `page_size<=50` and allowlisted `filters`. All conditions are AND.

- Text `contains`/`prefix`/`eq`: hierarchy IDs/names, `pixel_id`, `app_id`.
- Number `gt`/`gte`/`lt`/`lte`/`eq`: metrics, `daily_budget`, `lifetime_budget`, `bid_amount`.
- Enum `eq`/`in`: statuses, `objective`, `optimization_goal`, `billing_event`, `conversion_event`, budget/bid/product/currency fields.

Read `adsagent://guide/metadata-contract` once per guide version. `configured_status` is `ACTIVE`/`PAUSED`; `effective_status` includes `DISAPPROVED`, `PENDING_REVIEW`, and parent-paused. Legacy `status` aliases `effective_status`.

Read `delivery_status` and `delivery_issue_codes` independently from both
native status fields. Account and parent blockers may make an otherwise
`ACTIVE` child unable to deliver. Never rewrite child status from an inherited
blocker, and preserve simultaneous account, parent, review, and rejection
issues.

Money uses returned account currency and `money_unit=major`. `budget_level` is `campaign|adset`; `bid_strategy` and `optimization_goal` are canonical lower-case. `objective` and `billing_event` are Meta-native uppercase; `conversion_event` is separate lower-case metadata.

With `group_by=ad`, preserve `ad_account_id`, `ad_account_name`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `ad_id`, and `ad_name`. Do not prefetch or fan out parents. Legacy `search` and `spend_gt` remain compatible; do not use `dedupe_by`. Exact Ad-name deduplication, language classification, and business grouping remain client-side.

For matches, preserve each `ad_id`; advance pages serially while the single-scope
overview reports `data.meta.has_more=true` (or the corresponding
`data.items[].result.meta.has_more=true` for a batch item). Page 1 must be
complete. For page 2 and later, keep `consistency=cached`,
`query_contract_version=1`, `require_complete_range=true`, scope, dates,
timezone, grouping, filters, sorting, and `page_size` unchanged; increment only
`page` and pin `min_as_of` to task `result.meta.source_observed_at` or the scope
overview's `query_contract.coverage.source_observed_at`. Use the earliest
multi-scope source anchor.

Locate a single-scope overview at `data`, and each ordered multi-scope overview
at `data.items[].result`. Preserve every first-page overview
`meta.inventory_anchor` in original scope order. Pass those opaque values
through `inventory_anchors` on page 2 and later. If the server returns
`continuation_valid=false` or
rejects an inventory anchor, discard all partially collected rows and restart
from page 1 serially. Never combine rows from different inventory generations.
Do not rerun page 1 merely to continue or switch to `require_fresh`.
Never enlarge or parallelize pages. On `pagination_anchor_unavailable`, stop and
preserve `support_ref`; do not broaden, refresh, or treat it as a permission
error. Large output uses grouped `insights_export_csv` with identical filters.

On `adsagent_query_invalid`, correct the public field once. On `scope_unavailable`, do not infer another workspace/token or Meta permission. Run setup and matching discovery (`products_list`/`accounts_list_linked_accounts`) once; if still listed, retry the identical bounded read once. Then preserve `support_ref` for operator review. Never broaden scope or alter permissions.

## Completeness And Freshness

Report server totals; never sum pages. Native totals require `meta.complete=true`; profile totals require top-level `complete=true`. Missing scopes are unknown.

For Campaign, Ad Set, or Ad existence totals, additionally require
`meta.inventory_coverage=complete` and
`zero_insights_entities_included=true`. Partial, unavailable, or
Insights-rows-only inventory keeps absent entities unknown. Read
`inventory_freshness` separately from Insights freshness.

An inventory-only row uses `metrics_availability=unverified` and nullable
metrics. Preserve those `null` values and never convert unavailable metrics to
zero. Such a row proves the entity and its observed configuration/status, not
zero spend, zero impressions, or fresh performance evidence.

Poll distinct `task_ref` values serially with `tasks_get_status(task_ref=..., response_mode=compact)`. Consume only task `status=completed`, `result.status=complete`, and `result.meta.complete=true`; do not rerun page 1 merely to continue. Stop otherwise.

`freshness_kind=age_only` is not mutation coverage. Do not decide on `verification_pending`, `data_not_fresh`, unknown launch date, or incomplete data.

## Verification And Output

After confirm, follow `next_action` to `overview_get_live_configs`; `config_verified_live` proves configuration. `after_mutation_ref=mutation_ref` covers post-write metrics and does not verify delivery configuration. Recover with `operations_get_context`; never repeat writes.

Keep Meta and MMP distinct. Poll exports with `tasks_get_status(..., response_mode=compact)` to terminal. Read `result.artifact`; HTTP GET `download_url` byte-for-byte. Never redact, rebuild, decode, truncate, or substitute it. `artifact_status=expired` or an absent URL requires a new explicit export. Return the link, never raw CSV. Output concise Markdown.
