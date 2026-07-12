---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
argument-hint: "<product/account, date range, grouping>"
version: 0.7.0
---

# Meta Insights Through AdsAgent

Use bounded aggregate reads and public handles. Do not expose raw rows, internal IDs, schemas, or diagnostics.

## Scope First

1. Run `setup_get_status`; inspect `setup_get_status.capabilities`, then run `products_list` when no product/account is selected.
2. Tell the user how many product cards exist and ask for one product/account plus `date_from` and `date_to`.
3. Keep scope, grouping, attribution/channel, and freshness visible in the answer.
4. Read `adsagent://guide/brief`; use one bounded catalog topic only when needed.

Do not silently select all accounts or a default date range.

## Totals And Completeness

Report server totals verbatim: `summary` from `insights_query_overview` and `totals` from `insights_read_breakdowns`. Never sum visible rows; rows may be paginated and same-name campaigns are common. Reference campaigns by ID.

Trust results only when `meta.complete=true`. Follow `meta.has_more`; do not infer completion from item count. In batch results, missing scopes are unknown, never zero.

Report effective Meta statuses verbatim, including `DISAPPROVED`, `PENDING_REVIEW`, and `IN_PROCESS`.

## Query Routing

- Ordinary report, one explicit scope -> `insights_query_overview`.
- Ordinary report, multiple scopes -> one `insights_query_batch_overview` call.
- Decision-sensitive read -> `insights_query_consistent` with `consistency=require_fresh`, but only when capabilities advertise it. Otherwise use the cached overview and label `freshness_kind=age_only`.
- Product ranking -> `products_list`, already sorted by recent spend.
- `mcp_fanout_detected` -> stop the single-scope loop and batch current plus pending scopes; do not retry the blocked call.

If top-level `meta.complete=false`, show successful scopes and every `missing_scopes` entry.

`freshness_kind=age_only` means pull age and is not mutation coverage. `source_watermark`, `metrics_observed_after_mutation`, and `config_verified_live` are separate proofs. Do not make a decision on `verification_pending`, `data_not_fresh`, unknown launch date, or `complete=false`.

## Write Verification And Recovery

For a delivery write: prepare, show the sanitized summary, obtain explicit approval, then confirm. Keep the returned `mutation_ref`; call `insights_query_consistent` with `after_mutation_ref=mutation_ref`. Never retry an uncertain write automatically.

Recover one receipt with `operations_get`, or an interrupted product workflow with `operations_get_context(product_ref=...)`. Poll queued work with `tasks_get_status(task_ref=...)` until terminal.

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
