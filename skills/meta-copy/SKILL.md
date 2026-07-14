---
name: meta-copy
description: Use when the user asks AdsAgent to copy, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

Use public handles and sanitized summaries. Never reconstruct hidden payloads.

## Route Before Preparing

Ask at every fork; never guess:

- One source ad -> `copy_ad_quick_copy`.
- Campaign or ad set -> `copy_ad_clone_structure`; preserve its 1:1 tree and creatives.
- Repeat a past creation -> `campaigns_recreate_from_task` with `task_ref` from `tasks_list_create_history`.

Ask deep versus fresh:

- Deep reuses source page posts and engagement. Disclose and skip dead posts; never substitute.
- Fresh uploads distinct materials. Nothing is skipped; engagement does not carry.

Partnership/boosted sources require `copy_mode="deep"`. On `partnership_fresh_copy_unsupported`, stop before approval; never switch silently. Show `source_creative_type`, `post_linkage`, and warnings. Meta validates cross-account eligibility; rejection is terminal, so do not auto-retry or probe accounts.

## Safe Flow

1. Resolve source level/account and target account.
2. Confirm structure, budget, countries, start, copy mode, and library selections.
3. Prepare through AdsAgent and inspect `expires_at`. QuickCreate confirm tokens are single-use and expire after 15 minutes.
4. Show only `approval_request.summary`, including warnings and live current -> requested values.
5. Call confirm only after explicit user approval and before `expires_at`. Preserve the exact token; never retype it.
6. On `confirm_token_invalid`, do not retry confirm. Prepare again, show the fresh summary, and obtain fresh explicit approval; never inherit approval from the expired draft.
7. A successful asynchronous confirm returns `task_ref`. Poll with `tasks_get_status(task_ref=..., response_mode=compact)` until `terminal=true`; do not search task history for a replacement handle.

For status/budget/bid changes, follow `next_action` to `overview_get_live_configs` with typed entities and `mutation_ref`; retry only that read while pending. Use `insights_query_consistent(require_fresh, after_mutation_ref=mutation_ref)` only for post-write metrics; it does not verify delivery configuration. Recover interruptions with `operations_get` or `operations_get_context`; never repeat uncertain writes.

Never automatically retry confirm, creation, budget, status, bid, or targeting writes.

On terminal `no_create_permission`, tell the user to open `/dashboard/assets/fb-users`, enable Create on an active eligible connection, and then prepare again. Never enable or modify customer permissions automatically, and never replay the failed task.

## QuickCreate Sources

Choose exactly one:

- Normal creative ads: `creative_names` or creative source mode.
- Partnership ads: `partnership_rows`.
- Carousel ads: `creative_source.mode="carousel"` with `carousel_groups`.

Each group becomes one ad. Use its `ad_name`/`name`, provide 2-10 ordered images, never mix IDs and names, and exclude video in carousel v1.

## Comparison

Task history is creation intent, not current Meta proof. Compare its sanitized snapshot with a current AdsAgent snapshot.

Return Markdown:

| Field | Creation snapshot | Live Meta state | Impact |
| --- | --- | --- | --- |

Cover targeting, budget, status, naming, structure, and user-visible creative mode. State missing fields and data sources.

## Stop Rule

On `operator_review_required` or another redacted business-rule rejection, stop. Do not probe alternate fields. Hand off public IDs, requested structure, timestamp, and exact public error to the AdsAgent operator.

Do not paste raw task logs, Meta payloads, tokens, or hidden diagnostics.
