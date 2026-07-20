---
name: meta-copy
description: Use when the user asks AdsAgent to copy, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

## Route

- One source Ad: `copy_ad_quick_copy` single mode.
- Several distinct source Ads in one destination tree: grouped mode.
- Campaign or AdSet: `copy_ad_clone_structure`.
- Repeat prior creation: `campaigns_recreate_from_task` with `task_ref`.
- New template launch: `campaigns_quick_create`.

Ask deep versus fresh. Deep reuses posts/engagement; fresh uploads materials. Partnership/boosted sources require `copy_mode="deep"`; stop on `partnership_fresh_copy_unsupported`.

Show `source_creative_type`/`post_linkage`; do not auto-retry. Grouped approval returns one `cgb_confirm_*` token.

## Creation Contract V3

Re-list tools. Read `adsagent://guide/creation-contract`, `adsagent://guide/name-contract`, and for delivery, `adsagent://guide/metadata-contract`. Set `creation_contract_version=3`; emit role-specific names.

Single-copy tool arguments:

```json
{"request":{"creation_contract_version":3,"request_mode":"single","source_ad_id":"<ad>","source_ad_account_id":"<source>","target_ad_account_id":"<target>","campaign_count":1,"adset_count":1,"ads_per_adset":1,"copy_mode":"deep","target_campaign_name":"<optional>"}}
```

Grouped-copy tool arguments:

```json
{"request":{"creation_contract_version":3,"request_mode":"grouped","grouped_plan":{"source_ad_account_id":"<source>","target_ad_account_id":"<target>","copy_mode":"deep","campaigns":[{"campaign_name":"<campaign>","adsets":[{"adset_name":"<optional adset>","ads":[{"source_ad_id":"<ad>","ad_name":"<optional target ad>"}]}]}],"campaign_status":"PAUSED","adset_status":"PAUSED","ad_status":"PAUSED"}}}
```

Use role-specific fields. `template_name` selects/creates; `new_template_name` renames. `folder_name` and `interest_pack_name` identify resources. Bare `name` is legacy-only: never emit or move it. Reject conflicts.

QuickCreate uses typed `execution`, `destination`, and one `creative_source`. Web uses `destination.web_url`; app uses `app_id`, `store_url`, or `deep_link`. Never substitute Meta raw `application_id`, `object_store_url`, or `app_link`.

## Grouped Copy

Finish bounded pages serially; preserve every `ad_id` and deduplicate only exact Ad names. `ad_num` duplicates one source Ad; multiple distinct source Ads use `grouped_plan` for 1-1-N, 1-N-1, or custom layouts. Do not fall back to a client-built multi-stage copy.

Order sources deliberately: the first Ad of the first AdSet seeds Campaign settings; the first Ad of each AdSet seeds that AdSet. Show one paused-by-default approval summary and verify every `settings_source_ad_id`, account, count, budget, bid, status, and geography. Compare returned `geo_targeting_override`. After approval, pass the `cgb_confirm_*` token unchanged to `copy_ad_quick_copy_confirm`. Use `countries_override`, or `worldwide_override=true` plus `excluded_countries_override`.

If the user references settings but omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Recovery And Approval

On `adsagent_request_incomplete`, correct advertised `invalid_fields` and rerun the same prepare once; it creates no Meta object. Never reuse a confirm token. On repeat, redaction, or `operator_review_required`, stop with the exact `support_ref`. Never send raw payloads, logs, or tokens.

Show `approval_request.summary`/warnings. Confirm once after explicit approval, then poll `tasks_get_status(task_ref=..., response_mode=compact)` to `terminal=true`. Never auto-retry writes. On `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never change permissions.

On `mcp_meta_quota_deferred`, recover only with `request_sent=false`, `safe_to_retry=true`, and `operator_review_required=false`: honor `retry_after_seconds`, preserve prior receipts, and re-prepare the same entity/value with fresh approval. Never reuse confirm. Sent or uncertain writes use recovery.

At terminal create/copy, report `result.failures.items` using public `ad_name`, `code`, `message`, and `next_action`; never expose a raw Meta error or retry the unchanged write. Corrected work requires fresh approval. On `failures.unclassified_count>0` or `operator_review_required=true`, report known items, stop, and preserve the task/support reference.

Status mutations use `target_configured_status=ACTIVE|PAUSED`; optional CAS uses `current_configured_status`. Never pass `effective_status` or lifecycle states. Legacy aliases are compatibility-only.

For post-write configuration, follow `next_action` to `overview_get_live_configs` with `mutation_ref`. Insights freshness proves metrics, not delivery configuration. Recover task writes through `operations_get_context`; never replay them.
