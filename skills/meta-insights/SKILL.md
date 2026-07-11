---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
argument-hint: "<product/account, date range, grouping>"
version: 0.6.2
---

# Meta Insights Through AdsAgent

Use bounded aggregate reads and public handles. Do not expose raw rows, internal IDs, schemas, or diagnostics.

## Scope First

1. Run `setup_get_status`, then `products_list` when no product/account is selected.
2. Tell the user how many product cards exist and ask for one product/account plus `date_from` and `date_to`.
3. Keep scope, grouping, attribution/channel, and freshness visible in the answer.
4. Read `adsagent://guide/brief`; use one bounded catalog topic only when needed.

Do not silently select all accounts or a default date range.

## Totals And Completeness

Report server totals verbatim: `summary` from `insights_query_overview` and `totals` from `insights_read_breakdowns`. Never sum visible rows; rows may be paginated and same-name campaigns are common. Reference campaigns by ID.

Trust results only when `meta.complete=true`. Follow `meta.has_more`; do not infer completion from item count. In batch results, missing scopes are unknown, never zero.

Report effective Meta statuses verbatim, including `DISAPPROVED`, `PENDING_REVIEW`, and `IN_PROCESS`.

## Query Routing

- One explicit product/account scope -> `insights_query_overview`.
- Multiple scopes -> one `insights_query_batch_overview` call.
- Product ranking -> `products_list`, already sorted by recent spend.
- `mcp_fanout_detected` -> stop the single-scope loop and batch current plus pending scopes; do not retry the blocked call.

If top-level `meta.complete=false`, show successful scopes and every `missing_scopes` entry.

## MMP

Keep Meta and MMP metrics distinct. Pass `channel_pid`. Use `all` only for a requested cross-channel view. If `status=partial` or `complete=false`, report failed channels; the smaller total is incomplete. Long supported windows are split server-side.

## Export

Use export only when explicitly requested. If queued, poll the returned `task_ref` until `terminal=true`; return artifact metadata/link, never raw CSV. Normal chat answers use cleaned aggregates and compact Markdown tables.

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
