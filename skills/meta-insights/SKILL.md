---
name: meta-insights
description: Use when the user asks AdsAgent about Meta product/account/campaign/ad-set/ad spend, delivery status, CPA, ROAS, conversions, MMP, AppsFlyer, cohorts, breakdowns, comparisons, or exports.
---

# Meta Insights Through AdsAgent

Use bounded aggregate reads and public handles. Do not expose raw rows, internal IDs, schemas, or diagnostics.

## Scope First

Run `setup_get_status`, then `products_list` when scope is missing. Ask for one product/account and explicit dates; never choose all accounts or dates silently. Read `adsagent://guide/brief` and only the needed catalog topic.

## Totals And Completeness

Report server `summary`/`totals`; never sum visible pages. Trust native totals only with `meta.complete=true`, follow `meta.has_more`, and treat missing scopes as unknown. Preserve effective statuses such as `DISAPPROVED`, `PENDING_REVIEW`, and `IN_PROCESS`.

## Query Routing

- Ordinary report, one explicit scope -> `insights_query_overview`.
- Ordinary report, multiple scopes -> one `insights_query_batch_overview` call.
- Profile decision read -> only for `agent_method_profile.profile_id=adsagent_agent_methods_v1`, call `insights_query_consistent` once with root `query_contract_version=1`, `consistency=require_fresh`, and one scope or at most 20 ordered scopes.
- Product ranking -> `products_list`, already sorted by recent spend.
- `mcp_fanout_detected` -> stop the single-scope loop and batch current plus pending scopes; do not retry the blocked call.

For candidate selection keep `page_size<=50`; pass `search`, `spend_gt`, and `dedupe_by=name`. Do not enlarge the page or fetch all pages to filter client-side.

On `adsagent_query_invalid`, correct the named public field and retry once. For an unavailable scope, ask for a connected `products_list` choice; never broaden.

In profile mode trust totals only when top-level `complete=true`. Poll distinct `task_ref` values serially with `tasks_get_status(response_mode=compact)`; rerun the identical query only after `completed`, and stop on `partial_completed`, `failed`, or `cancelled`. Without the profile, preserve native single/batch output and trust only `meta.complete=true`.

`freshness_kind=age_only` means pull age and is not mutation coverage. `source_watermark`, `metrics_observed_after_mutation`, and `config_verified_live` are separate proofs. Do not make a decision on `verification_pending`, `data_not_fresh`, unknown launch date, or `complete=false`.

## Write Verification And Recovery

After approval and confirm, follow `next_action` to `overview_get_live_configs`; `config_verified_live` proves configuration. `insights_query_consistent(..., after_mutation_ref=mutation_ref)` is for post-write metrics and does not verify delivery configuration. Recover with `operations_get` or `operations_get_context`; never repeat writes.

## MMP

Keep Meta and MMP distinct. Pass `channel_pid`; report partial channels and server-split windows.

## Export

Export only when asked. Poll `tasks_get_status(task_ref=...)` to terminal; return the artifact, never raw CSV.

## Output

Return Markdown with Answer, Scope, a compact metric table, completeness/freshness, and Notes. Do not return only counts or volunteer optimization advice.
