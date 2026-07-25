---
name: meta-copy
description: Use when the user asks AdsAgent to copy, compare, or prepare Meta ads, campaigns, budgets, targeting, or delivery changes.
---

# Meta Copy And Comparison

## Route

- One Ad: `copy_ad_quick_copy`; distinct Ads: grouped mode.
- Campaign/AdSet: `copy_ad_clone_structure`; prior task: `campaigns_recreate_from_task`.
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

`template_name` selects; `new_template_name` renames. `folder_name` and `interest_pack_name` identify resources. Bare `name` is legacy-only. QuickCreate uses typed `execution`, `destination`, and one `creative_source`. Never substitute Meta raw adapter fields.

### QuickCreate Append

- Use `append_mode=append-campaign` plus `target_campaign_id`.
- Use `append_mode=append-adset` plus `target_adset_id`, `campaign_count=1`, and `adset_count=1`. It creates zero Campaigns and zero AdSets, creates the requested Ads only, and inherits the existing parent budget.
- Never send `append_mode=existing`, `existing_campaign_id`, `existing_adset_id`, or `product_ref`, or replace a target after prepare.

On bounded `invalid_fields`, rerun prepare once, show the new summary, and obtain fresh explicit approval. Never auto-confirm, rotate accounts, change permissions, or replay a confirm token.

## Grouped Copy

Finish pages serially; preserve every `ad_id` and deduplicate only exact Ad names. `ad_num` duplicates one source Ad; multiple distinct source Ads use `grouped_plan` for 1-1-N or 1-N-1. Do not fall back to a client-built multi-stage copy.

First Ad seeds Campaign settings; each AdSet's first seeds its settings. Show one paused-by-default approval summary with every `settings_source_ad_id`. Pass `cgb_confirm_*` unchanged to `copy_ad_quick_copy_confirm`. Use `countries_override`, or `worldwide_override=true` plus `excluded_countries_override`; compare `geo_targeting_override`.

If the user omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Delivery Permission And Budget Level

Before status, budget, or bid changes, inspect `setup_get_status.capabilities.delivery_mutations`. If denied, follow `permission_action`: dashboard tokens use `/dashboard/settings#mcp-access`; OAuth reconnects with `mcp.optimize.write`. Never change permissions automatically. Then reconnect, re-list tools, and rerun setup.

ABO uses `overview_update_adset_budget` then `overview_update_confirm`; CBO uses `overview_update_campaign_budget` then `overview_update_campaign_budget_confirm`. Show the summary and get approval. Never substitute budget levels. If `allowed=true` but its tool remains absent, stop with `support_ref`.

## Recovery

On `adsagent_request_incomplete`, correct `invalid_fields` on prepare once. On repeat or `operator_review_required`, stop with `support_ref`. Confirm only after explicit approval, then poll `tasks_get_status(task_ref=..., response_mode=compact)`. On `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never change permissions.

On strict `mcp_meta_quota_deferred` (`request_sent=false`, `safe_to_retry=true`, `operator_review_required=false`), STOP before later confirms and follow [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md). Never reuse confirmation material or replay sent/uncertain writes; use `operations_get_context`.

Report terminal `result.failures.items` and follow its retry flags. Never expose a raw Meta error or retry the unchanged write. Only `manual_new_task_allowed=true` permits a new task with fresh approval. Stop on `failures.unclassified_count>0`.

Server chunking is not a fixed Meta limit. Preserve every acknowledged object and receipt.

Status writes use `target_configured_status=ACTIVE|PAUSED`; CAS uses `current_configured_status`. Never pass `effective_status`. Follow `next_action` to `overview_get_live_configs` with `mutation_ref`; `after_mutation_ref` is for post-write metrics and does not verify delivery configuration.
