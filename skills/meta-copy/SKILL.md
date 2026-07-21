---
name: meta-copy
description: Use when the user asks AdsAgent to copy, clone, recreate, compare, or prepare Meta ads, campaigns, ad sets, partnership ads, carousels, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

## Route

- One source Ad: `copy_ad_quick_copy`; multiple distinct source Ads: grouped mode.
- Campaign or AdSet: `copy_ad_clone_structure`; prior task: `campaigns_recreate_from_task` with `task_ref`.
- New template launch: `campaigns_quick_create`.

Partnership/boosted sources require `copy_mode="deep"`; stop on `partnership_fresh_copy_unsupported`. Show `source_creative_type` and `post_linkage`; do not auto-retry.

## Creation Contract V3

Read `adsagent://guide/creation-contract`, `adsagent://guide/name-contract`, and `adsagent://guide/metadata-contract`. Set `creation_contract_version=3`.

```json
{"request":{"creation_contract_version":3,"request_mode":"single","source_ad_id":"<ad>","source_ad_account_id":"<source>","target_ad_account_id":"<target>","campaign_count":1,"adset_count":1,"ads_per_adset":1,"copy_mode":"deep","target_campaign_name":"<optional>"}}
```

```json
{"request":{"creation_contract_version":3,"request_mode":"grouped","grouped_plan":{"source_ad_account_id":"<source>","target_ad_account_id":"<target>","copy_mode":"deep","campaigns":[{"campaign_name":"<campaign>","adsets":[{"adset_name":"<optional adset>","ads":[{"source_ad_id":"<ad>","ad_name":"<optional target ad>"}]}]}],"campaign_status":"PAUSED","adset_status":"PAUSED","ad_status":"PAUSED"}}}
```

`template_name` selects; `new_template_name` renames. `folder_name` and `interest_pack_name` identify resources. Bare `name` is legacy-only. QuickCreate uses typed `execution`, `destination`, and one `creative_source`. Never substitute Meta raw `application_id`, `object_store_url`, or `app_link`.

### QuickCreate Append

- Use `append_mode=append-campaign` plus `target_campaign_id`.
- Use `append_mode=append-adset` plus `target_adset_id`, `campaign_count=1`, and `adset_count=1`. It creates zero Campaigns and zero AdSets, creates the requested Ads only, and inherits the existing parent budget.
- Never send `append_mode=existing`, `existing_campaign_id`, `existing_adset_id`, or `product_ref`, or replace a target after prepare.

On bounded `invalid_fields`, rerun prepare once, show the new summary, and obtain fresh explicit approval. Never auto-confirm, rotate accounts, change permissions, or replay a confirm token.

## Grouped Copy

Finish pages serially; preserve every `ad_id` and deduplicate only exact Ad names. `ad_num` duplicates one source Ad; multiple distinct source Ads use `grouped_plan` for 1-1-N, 1-N-1, or custom layouts. Do not fall back to a client-built multi-stage copy.

Order sources: first Ad seeds Campaign settings; each AdSet's first seeds its settings. Show one paused-by-default approval summary with every `settings_source_ad_id`, account, count, budget, bid, status, and geography. Compare `geo_targeting_override`; after approval pass `cgb_confirm_*` unchanged to `copy_ad_quick_copy_confirm`. Use `countries_override`, or `worldwide_override=true` plus `excluded_countries_override`.

If the user omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Recovery

On `adsagent_request_incomplete`, correct `invalid_fields` on prepare once. On repeat or `operator_review_required`, stop with `support_ref`. Confirm only after explicit approval, then poll `tasks_get_status(task_ref=..., response_mode=compact)`. On `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never change permissions.

For `mcp_meta_quota_deferred`, recover only with `request_sent=false`, `safe_to_retry=true`, and `operator_review_required=false`; wait, then re-prepare with fresh approval. Never reuse confirm. Sent or uncertain writes use `operations_get_context`; never replay.

Report terminal `result.failures.items` fields `ad_name`, `code`, `message`, `automatic_retry_allowed`, `manual_new_task_allowed`, `operator_review_required`, and `next_action`. Never expose a raw Meta error, retry the unchanged write, or reuse its confirm token. Only `manual_new_task_allowed=true` permits a newly prepared task containing failed items with fresh approval; pending or ambiguous writes stay in `operations_get_context` recovery. Stop on `failures.unclassified_count>0`.

AdsAgent may split bulk Ad writes into configurable sequential chunks. Treat that as a server-owned defensive reliability policy, not evidence of a fixed Meta limit. Preserve every acknowledged object and receipt; never recreate successful items when a later chunk fails.

Status writes use `target_configured_status=ACTIVE|PAUSED`; CAS uses `current_configured_status`. Never pass `effective_status`. Follow `next_action` to `overview_get_live_configs` with `mutation_ref`; `after_mutation_ref` is for post-write metrics and does not verify delivery configuration.
