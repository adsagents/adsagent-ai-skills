---
name: meta-copy
description: Use when the user asks AdsAgent to copy, duplicate, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or live delivery changes.
argument-hint: "<source ad/campaign/adset, target account, copy goal>"
version: 0.7.0
---

# Meta Copy And Comparison

Use public handles and sanitized approval summaries. Never reconstruct hidden payloads or validation internals.

## Route Before Preparing

Ask at every fork; never guess:

- One source ad -> `copy_ad_quick_copy`.
- Campaign or ad set -> `copy_ad_clone_structure`; preserve the 1:1 tree and each ad's own creative.
- Repeat a past creation -> `campaigns_recreate_from_task` with `task_ref` from `tasks_list_create_history`.

For both copy paths, ask deep versus fresh:

- Deep reuses each source page post and preserves engagement. Dead posts are disclosed and skipped, never substituted.
- Fresh uploads each distinct material into new creatives. Nothing is skipped; engagement does not carry.

## Safe Flow

1. Resolve source level/account and target account.
2. Confirm structure, budget, countries, start time, copy mode, and public library selections.
3. Prepare through AdsAgent.
4. Show only `approval_request.summary`, including warnings and live current -> requested values.
5. Call confirm only after explicit user approval. Preserve the exact single-use confirm token; never retype it.
6. Poll queued creation with `tasks_get_status(task_ref=...)` until `terminal=true`.

For status/budget/bid delivery changes, keep the confirmed `mutation_ref` and verify it with `insights_query_consistent(require_fresh, after_mutation_ref=mutation_ref)` when capabilities advertise consistency. If interrupted, recover with `operations_get_context`; never repeat an uncertain write.

Never automatically retry confirm, creation, budget, status, bid, or targeting writes.

## QuickCreate Sources

Choose exactly one:

- Normal creative ads: `creative_names` or creative source mode.
- Partnership ads: `partnership_rows`.
- Carousel ads: `creative_source.mode="carousel"` with `carousel_groups`.

Each carousel group becomes one ad. Use its `ad_name`/`name`, provide 2-10 image creatives in intended card order, do not mix IDs and names within a group, and do not use video cards in carousel v1.

## Comparison

Task history is creation-time intent, not proof of current Meta state. For live-edit questions, compare the sanitized creation snapshot with a current AdsAgent platform snapshot.

Return Markdown:

| Field | Creation snapshot | Live Meta state | Impact |
| --- | --- | --- | --- |

Cover targeting, budget, status, naming, structure, and user-visible creative mode. State missing fields and data sources.

## Stop Rule

On `operator_review_required` or another redacted business-rule rejection, stop. Do not probe alternate fields. Hand off public IDs, requested structure, timestamp, and exact public error to the AdsAgent operator.

Do not paste raw task logs, Meta payloads, tokens, or hidden diagnostics.
