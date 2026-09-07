# Meta Insights Query Contract

Use bounded aggregates and public handles. Never expose rows, schemas, or diagnostics.

## Scope And Routing

Missing scope: run `setup_get_status`, then `products_list`; ask for scope and dates.

- One scope: `insights_query_overview`; multiple scopes: one `insights_query_batch_overview`. Native reads pass `metadata_contract_version=1`.
- With `agent_method_profile.profile_id=adsagent_agent_methods_v1` and its consistent query tool present in the client-local catalog, call `insights_query_consistent` once with root `query_contract_version=1`, `consistency=cached`, and one scope or up to 20 ordered scopes. Use the tenant ledger populated by `setup_get_status.auto_pull`; do not default to `require_fresh` unless the connection advertises `mcp.insights.pull` and the user explicitly needs a source refresh (for example post-mutation metrics verification). When that refresh path applies, call `insights_query_consistent(consistency=require_fresh)` once instead of cached.
- If that advertised read tool is missing only from the client-local catalog, use the profile's `native_single_fallback` or `native_batch_fallback` when present, otherwise the documented native overview/batch tool above. Do not report a server registration failure or stop a read solely because of a local selector miss.
- On `mcp_fanout_detected`, stop, batch current plus pending scopes, and do not retry the blocked call.

## Filtering And Metadata

For `insights_query_consistent`, use `page_size<=50` and allowlisted `filters`. All conditions are AND.

- Batch cap: with `query_contract_version=1`, total rows requested may be up to `20 scopes × 50 page_size`. If the response exceeds the public 48 KiB budget, reduce `page_size`, use `response_mode=compact`, or request fewer fields (`response_budget_exceeded`).
- OAuth Safe Mode accepts `date_range_mode=since_launch` without explicit `date_from`/`date_to` when product scope is anchored.
- Product-scoped results may include `query_contract.spend_reconciliation` comparing `products_list` last-7d spend to the Insights summary for overlapping query windows. Treat `state=mismatch` as non-authoritative spend evidence.

- Text `contains`/`prefix`/`eq`: hierarchy IDs/names, `pixel_id`, `app_id`.
- Number `gt`/`gte`/`lt`/`lte`/`eq`: metrics, `daily_budget`, `lifetime_budget`, `bid_amount`.
- Enum `eq`/`in`: statuses, `objective`, `optimization_goal`, `billing_event`, `conversion_event`, budget/bid/product/currency fields.

Read `adsagent://guide/metadata-contract` once per guide version. `configured_status` is `ACTIVE`/`PAUSED`; `effective_status` includes `DISAPPROVED`, `PENDING_REVIEW`, and parent-paused. Legacy `status` aliases `effective_status`.

Read `delivery_status` and `delivery_issue_codes` independently from both
native status fields. Account and parent blockers may make an otherwise
`ACTIVE` child unable to deliver. Never rewrite child status from an inherited
blocker, and preserve simultaneous account, parent, review, and rejection
issues.

Money uses returned account currency and `money_unit=major`. Cached Insights
`daily_budget` values include `budget_config_source=inventory_snapshot` and
optional `budget_observed_at`; compare live budgets through
`overview_get_live_configs` before mutating. `budget_level` is `campaign|adset`;
`bid_strategy` and `optimization_goal` are canonical lower-case. `objective`
and `billing_event` are Meta-native uppercase; `conversion_event` is separate
lower-case metadata.

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

## Known Entity Configuration

Insights answers performance and bounded candidate-selection questions; it is
not a live-configuration preflight for one known Campaign, Ad Set, or Ad. When
the user asks to change a known entity's status, budget, or bid, route to
`meta-copy` and call the matching prepare tool directly. Prepare reads the live
current value and does not mutate Meta.

If the user explicitly requests read-only configuration proof, call
`overview_get_live_configs` with exactly one typed entity and no
`mutation_ref`. Never use `management=true` or product/date Insights as live
configuration evidence.

For a bounded rule or decision over explicit candidates, pass up to 50 exact
candidate entities in one `overview_get_live_configs` request. Match every
live row by `entity_type` and `entity_id`, require complete one-to-one coverage,
and use `configured_status` to exclude non-active candidates. If any exact
candidate is missing or incomplete, live status coverage is incomplete. Never
infer child state from parent status, and never apply a reported manual change
outside the candidate ID set to the current candidates without an exact ID
match.

On `read_query_too_large` with `operator_review_required=false`,
`automatic_retry_allowed=false`, and `query_change_required=true`, do not send
the user to an operator and do not repeat the unchanged request. Narrow the
scope/date/filter/page shape, use `overview_get_live_configs` for one known
entity, or use `insights_export_csv` only for an explicitly requested large
table.

## Completeness And Freshness

Report server totals; never sum pages. Native totals require `meta.complete=true`; profile totals require top-level `complete=true` and `metrics_evidence.authoritative=true`. When `metrics_evidence.authoritative=false`, follow `next_action` to the profile's native read fallback instead of treating the ledger as decision-ready. Missing scopes are unknown. In a common result, claim exact zero only when `metrics_evidence.zero_proven=true`; otherwise report no observed metrics and say the exact amount is unproven.

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

## Product Export And Delivery Gate

Before calling `insights_export_csv` or delivering a terminal export artifact
for a product-scoped daily report (email, webhook, workbook ingest, or object
storage):

1. Preflight the identical scope, date window, timezone, grouping, and filters
   with `insights_query_consistent` (`query_contract_version=1`,
   `consistency=cached`, and `require_complete_range=true` when paginating).
2. Require top-level `complete=true`, `result.status=complete`, and
   `metrics_evidence.authoritative=true` for the same scope and calendar
   day(s).
3. When a same-batch account scope for the product's bound ad account shows
   same-day non-zero activity while the product scope returns zero rows, treat
   product aggregation as incomplete—not a proven zero day. Do not export,
   send, or ingest downstream.
4. On `status=incomplete_coverage` or `metrics_evidence.authoritative=false`,
   stop before export. Follow `next_action`; use the profile's native read
   fallback once when advertised. Preserve `support_ref`.
5. A terminal export with `row_count=0` is delivery-ready only when preflight
   proved authoritative complete coverage and `metrics_evidence.zero_proven=true`.
   Otherwise treat `artifact_status=ready` as non-authoritative even when the
   CSV schema and hash validate.
6. When export terminal metadata exposes `coverage`, `source_watermark`,
   `metrics_evidence.authoritative`, or `zero_proven`, enforce the same gates
   before delivery.

`freshness_kind=age_only` is not mutation coverage. Do not decide on `verification_pending`, `data_not_fresh`, unknown launch date, or incomplete data.

When `freshness.entity_activity_after_watermark=true` or warning
`entity_activity_after_watermark` is present, treat metrics as stale relative to
inventory: entities were created after the metrics watermark. Do not use those
rows for spend totals, optimization, or pause decisions without
`require_fresh` or live verification.

## Verification And Output

After a delivery confirm, consume top-level `verification` and
`verification_result` first. An inline `config_verified_live` result proves
configuration. Follow `next_action` to `overview_get_live_configs` only while
verification remains pending. If the client cannot select that read after
`mutation_applied=true`, preserve `mutation_ref` and report applied-but-pending;
do not reauthorize, replace the bearer, or repeat the write.
`after_mutation_ref=mutation_ref` covers post-write metrics and does not verify delivery configuration. `mutation_coverage` is applicable only when that request field was supplied; it never proves current configured or delivery state.
Recover task-backed uncertainty with
`operations_get_context`; never repeat writes.

Keep Meta and MMP distinct. Poll exports with `tasks_get_status(..., response_mode=compact)` to terminal. Read `result.artifact`; HTTP GET `download_url` byte-for-byte. Never redact, rebuild, decode, truncate, or substitute it. `artifact_status=expired` or an absent URL requires a new explicit export. Return the link, never raw CSV. Output concise Markdown.
