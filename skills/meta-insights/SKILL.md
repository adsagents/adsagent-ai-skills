---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
---

# Meta Insights Through AdsAgent

Use bounded aggregate reads and public handles. Do not expose raw rows, internal IDs, schemas, or diagnostics.

## Scope First

1. Run `setup_get_status`; inspect `setup_get_status.capabilities`, then run `products_list` when no product/account is selected.
2. Report a bounded product count; ask for one product/account plus `date_from` and `date_to`.
3. Read `adsagent://guide/brief`; use one catalog topic only when needed.

Do not silently select all accounts or a default date range.

## Totals And Completeness

Report server totals verbatim: `summary` from `insights_query_overview` and `totals` from `insights_read_breakdowns`. Never sum visible rows; rows may be paginated and same-name campaigns are common. Reference campaigns by ID.

Trust results only when `meta.complete=true`. Follow `meta.has_more`; do not infer completion from item count. In batch results, missing scopes are unknown, never zero.

Report effective Meta statuses verbatim, including `DISAPPROVED`, `PENDING_REVIEW`, and `IN_PROCESS`.

## Query Routing

- Ordinary report, one explicit scope -> `insights_query_overview`.
- Ordinary report, multiple scopes -> one `insights_query_batch_overview` call.
- Profile decision read -> only for `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with root `query_contract_version=1`, `consistency=require_fresh`, and one scope or at most 20 ordered scopes.
- Product ranking -> `products_list`, already sorted by recent spend.
- `mcp_fanout_detected` -> stop the single-scope loop and batch current plus pending scopes; do not retry the blocked call.

In profile mode trust totals only when top-level `complete=true`. Poll distinct `task_ref` values serially with `tasks_get_status(response_mode=compact)`; rerun the identical query only after `completed`, and stop on `partial_completed`, `failed`, or `cancelled`. Without the profile, preserve native single/batch output and trust only `meta.complete=true`.

`freshness_kind=age_only` means pull age and is not mutation coverage. `source_watermark`, `metrics_observed_after_mutation`, and `config_verified_live` are separate proofs. Do not make a decision on `verification_pending`, `data_not_fresh`, unknown launch date, or `complete=false`.

## Write Verification And Recovery

After approved confirm, call returned `next_action`: expect `overview_get_live_configs` with typed entities and `mutation_ref`. Retry only that read while pending; `config_verified_live` proves configuration. Use `insights_query_consistent(..., after_mutation_ref=mutation_ref)` only for post-write metrics; `metrics_observed_after_mutation` does not verify delivery configuration. Never repeat the write.

Recover one receipt with `operations_get`, or an interrupted workflow with `operations_get_context(product_ref=...)`.

## MMP

Keep Meta and MMP metrics distinct. Pass `channel_pid`. Use `all` only for a requested cross-channel view. If `status=partial` or `complete=false`, report failed channels; the smaller total is incomplete. Long supported windows are split server-side.

## Export

Use export only when explicitly requested. If queued, poll with `tasks_get_status(task_ref=...)` until `terminal=true`; return artifact metadata/link, never raw CSV.

## Output

```markdown
## Answer
Direct answer with server total.

## Scope
- Product/account:
- Date/grouping/channel:
- Complete/fresh:

## Results
| Name | Spend | CPA | ROAS | Conversions | Status |
| --- | ---: | ---: | ---: | ---: | --- |

## Notes
- Missing scopes/channels or artifact link:
```

Do not return only item counts when metrics exist. Do not volunteer optimization advice unless requested.
