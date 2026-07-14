---
name: meta-copy
description: Use when the user asks AdsAgent to copy, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

Use public handles and sanitized summaries. Never reconstruct hidden payloads.

## Route

- One source Ad -> `copy_ad_quick_copy`.
- Campaign or AdSet -> `copy_ad_clone_structure`.
- Repeat a past creation -> `campaigns_recreate_from_task` with a `task_ref` from `tasks_list_create_history`.

Ask deep versus fresh. Deep reuses posts and engagement; disclose dead posts. Fresh uploads distinct materials. Partnership/boosted sources require `copy_mode="deep"`. On `partnership_fresh_copy_unsupported`, stop before approval. Show `source_creative_type`, `post_linkage`, and warnings; do not auto-retry. Never switch modes or probe accounts silently.

## Group Several Source Ads

1. Finish the bounded Insights read. Preserve every `ad_id`, paginate serially, and deduplicate only exact Ad names after all requested pages are complete.
2. Show the language/geography grouping and apply only explicit rules.
3. Remember: `ad_num` duplicates one source Ad; it never combines source IDs.
4. For each target Campaign/geography, prepare one seed with `mode="clone_all"`. Freeze settings in its approval.
5. After the approved seed is terminal, obtain its target AdSet ID and prepare remaining distinct Ads with `mode="new_ads"`. Do not pass geography to `new_ads`; the target AdSet owns targeting.
6. Show remaining summaries as one bounded second approval set. Confirm exact approved drafts and poll `task_ref` values serially.

Use `countries_override` for explicit includes. Use `worldwide_override=true` with `excluded_countries_override` for worldwide-minus-country targeting. Compare returned `geo_targeting_override` with the request before approval.

If the user references settings but omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Safe Flow

1. Resolve source level/account and target account.
2. Confirm structure, budget, geography, start, and copy mode.
3. Prepare and inspect `expires_at`. Confirm tokens are single-use and expire after 15 minutes.
4. Show only `approval_request.summary` and warnings.
5. Confirm only after explicit approval. Preserve the exact token.
6. On `confirm_token_invalid`, prepare again, show the new summary, and obtain new approval.
7. Poll successful asynchronous work with `tasks_get_status(task_ref=..., response_mode=compact)` until `terminal=true`.

For delivery changes, follow `next_action` to `overview_get_live_configs` with `mutation_ref`. `insights_query_consistent(require_fresh, after_mutation_ref=mutation_ref)` proves metrics freshness, not configuration. Recover with `operations_get`; never repeat uncertain writes.

Never auto-retry confirm, creation, budget, status, bid, or targeting writes. On terminal `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never enable or modify customer permissions automatically.

## QuickCreate And Comparison

Choose one source: normal creatives, `partnership_rows`, or carousel groups. A carousel is one Ad with 2-10 ordered images; never mix IDs and names or use video in v1.

Task history is creation intent, not live Meta proof. Compare its sanitized snapshot with current AdsAgent state in a Markdown table covering targeting, budget, status, naming, structure, and creative mode.

On `operator_review_required`, stop. Hand off public IDs, requested structure, timestamp, exact public error, and any `support_ref`. Never paste raw logs, payloads, tokens, or hidden diagnostics.
