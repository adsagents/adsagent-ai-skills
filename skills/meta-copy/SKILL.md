---
name: meta-copy
description: Use when the user asks AdsAgent to copy, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

Use sanitized public summaries; never reconstruct hidden payloads.

## Route

- One source Ad -> `copy_ad_quick_copy`.
- Campaign or AdSet -> `copy_ad_clone_structure`.
- Repeat creation -> `campaigns_recreate_from_task` with a history `task_ref`.

Ask deep versus fresh. Deep reuses posts/engagement; fresh uploads materials. Partnership/boosted sources require `copy_mode="deep"`. On `partnership_fresh_copy_unsupported`, stop before approval. Show `source_creative_type`, `post_linkage`, and warnings; do not auto-retry or switch modes silently.

## Group Several Source Ads

1. Finish bounded Insights pages serially. Preserve every `ad_id`; deduplicate only exact Ad names after completion.
2. Preserve each source `ad_account_id`; apply only explicit language/geography rules.
3. `ad_num` duplicates one source Ad. For multiple distinct source Ads, call `copy_ad_quick_copy` once with `grouped_plan`; use its live schema for a 1-1-N, 1-N-1, or custom tree. Never emulate it client-side.
4. Order sources deliberately: the first Ad of the first AdSet seeds Campaign settings, and the first Ad of each AdSet seeds that AdSet. Verify every returned `settings_source_ad_id` before approval.
5. Show one paused-by-default approval summary covering source/target accounts, counts, budget, bid, geography, and settings sources. After approval, pass returned `cgb_confirm_*` token unchanged to `copy_ad_quick_copy_confirm` exactly once.
6. If live schema lacks `grouped_plan`, reconnect, re-list tools, and read `adsagent://guide/brief`. Do not fall back to a client-built multi-stage copy.

Use `countries_override` for explicit includes. Use `worldwide_override=true` with `excluded_countries_override` for worldwide-minus-country targeting. Compare returned `geo_targeting_override` with the request before approval.

If the user references settings but omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Safe Flow

1. Resolve source level/account and target account.
2. Confirm structure, budget, geography, start, and copy mode.
3. Prepare and inspect `expires_at`. Confirm tokens, including grouped-copy tokens, are single-use and expire after 15 minutes.
4. Show only `approval_request.summary` and warnings.
5. Confirm only after explicit approval. Preserve the exact token.
6. On `confirm_token_invalid`, prepare again, show the new summary, and obtain new approval.
7. Poll successful asynchronous work with `tasks_get_status(task_ref=..., response_mode=compact)` until `terminal=true`.

For delivery changes, follow `next_action` to `overview_get_live_configs` with `mutation_ref`. `insights_query_consistent(require_fresh, after_mutation_ref=mutation_ref)` proves metrics freshness, not configuration. Recover with `operations_get`; never repeat uncertain writes.

Never auto-retry confirm, creation, budget, status, bid, or targeting writes. On terminal `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never enable or modify customer permissions automatically.

## QuickCreate And Comparison

Choose normal creatives, `partnership_rows`, or carousel groups. A carousel is one Ad with 2-10 ordered images; never mix IDs and names or use video in v1.

Task history is intent, not live proof. Compare its sanitized snapshot with current AdsAgent state in a Markdown table covering targeting, budget, status, naming, structure, and creative mode.

On `operator_review_required`, stop. Hand off public IDs, requested structure, timestamp, exact public error, and any `support_ref`. Never paste raw logs, payloads, tokens, or hidden diagnostics.
