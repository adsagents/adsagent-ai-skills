# Meta Creation And Copy Contract

## Route

- One Ad: `copy_ad_quick_copy`.
- Multiple distinct source Ads: grouped `copy_ad_quick_copy`.
- Campaign/AdSet: `copy_ad_clone_structure`.
- Prior task: `campaigns_recreate_from_task`.
- New campaign from a saved template: `campaigns_quick_create`.
- Fixed existing-Ad campaign scope check (read-only): `campaigns_reconcile_campaign_plan`.

When the user wants a **fresh** QuickCreate after a partial failure — not task continuation — set `creation_intent=fresh` on `campaigns_quick_create`. Do not silently choose `campaigns_recreate_from_task`. Use `name_collision_policy=abort` when exact campaign names must not collide; prepare returns `creation_context.name_collisions` and may block with `status=blocked`.

Partnership/boosted sources require `copy_mode="deep"`. Stop on `partnership_fresh_copy_unsupported`; show `source_creative_type` and `post_linkage`; do not auto-retry.

## Fresh Copy Page Selection

Fresh copy (`engagement_mode=new_creatives` / `copy_mode="fresh"`) rebuilds media as a new post. The Page that publishes that post must be explicit on cross-account copies.

1. When prepare returns `fresh_copy_page_selection_required`, call `accounts_list_eligible_pages` for the **target** ad account.
2. Show the user every returned `page_id` with its display name. **Never auto-pick** a Page — wait for an explicit user choice.
3. Prepare again with `page_id=<chosen>` on the same request (single copy on the request root; grouped copy on `grouped_plan.page_id`).
4. Do **not** confirm while the warning is present and `page_id` is still missing.

`page_id` is only valid with fresh copy. To keep the authorized post and its engagement, use `engagement_mode=preserve_post` instead — no `page_id`.

For template-based append with a known Page and creative library, `campaigns_quick_create` + `append_mode=append-adset` + `overrides.page_id` remains valid.

## Append To Existing Ad Sets

Grouped copy **always creates a new destination tree**. It cannot append into existing Campaigns or Ad Sets.

| Goal | Tool | Shape |
| --- | --- | --- |
| Add ads to one existing Ad Set, keep source post | `copy_ad_quick_copy` | `request_mode=single`, `mode=new_ads`, `target_adset_id` on request root, `engagement_mode=preserve_post` — one prepare/confirm per Ad Set |
| Add ads via saved template + explicit Page | `campaigns_quick_create` | `append_mode=append-adset`, `target_adset_id`, `overrides.page_id` |
| Multiple new campaigns/ad sets from distinct sources | `copy_ad_quick_copy` | `request_mode=grouped`, `grouped_plan` tree — **not** append |

If prepare returns `grouped_copy_append_not_supported`, fix the payload — do not retry grouped with `target_adset_id`.

## Creation Contract V3

Read `adsagent://guide/creation-contract`, `adsagent://guide/name-contract`, and `adsagent://guide/metadata-contract`. Set `creation_contract_version=3`.

For `creation_contract_version=3`, every object level that the selected mode creates must carry an explicit status before prepare succeeds:

- `clone_all`: `campaign_status`, `adset_status`, and `ad_status`
- `new_adsets`: `adset_status` and `ad_status`
- `new_ads`: `ad_status` only
- grouped copy: `campaign_status`, `adset_status`, and `ad_status` on the outer request

Omitted required statuses fail closed at prepare with a validation error. Never infer `ACTIVE` for v3.

Legacy/unversioned requests remain compatible: the server may apply paused-by-default or legacy ACTIVE defaults, but the approval summary must expose each level's `requested_status`, `resolved_status`, `default_applied`, and `compatibility_rule`, plus an activation-risk warning when any resolved status is `ACTIVE`.

```json
{"request":{"creation_contract_version":3,"request_mode":"single","source_ad_id":"<ad>","source_ad_account_id":"<source>","target_ad_account_id":"<target>","campaign_count":1,"adset_count":1,"ads_per_adset":1,"copy_mode":"deep","target_campaign_name":"<optional>"}}
```

To add Ad Sets to an existing Campaign with `copy_ad_quick_copy`, use
`mode="new_adsets"` plus `target_campaign_id`. Statuses use only
`campaign_status`, `adset_status`, and `ad_status`, each `ACTIVE|PAUSED`;
`status_option` belongs only to `copy_ad_clone_structure` and must never be
sent to Quick Copy. `append_mode` belongs only to `campaigns_quick_create`.

```json
{"request":{"creation_contract_version":3,"request_mode":"single","source_ad_id":"<ad>","source_ad_account_id":"<source>","target_ad_account_id":"<target>","mode":"new_adsets","campaign_count":1,"adset_count":2,"ads_per_adset":1,"copy_mode":"fresh","target_campaign_id":"<campaign>","adset_status":"ACTIVE","ad_status":"ACTIVE"}}
```

```json
{"request":{"creation_contract_version":3,"request_mode":"grouped","grouped_plan":{"source_ad_account_id":"<source>","target_ad_account_id":"<target>","copy_mode":"deep","campaigns":[{"campaign_name":"<campaign>","adsets":[{"adset_name":"<optional>","ads":[{"source_ad_id":"<ad>","ad_name":"<optional>"}]}]}]}}}
```

Use explicit `campaign_name`, `adset_name`, `ad_name`, `template_name`, `new_template_name`, `folder_name`, and `interest_pack_name`; bare `name` is legacy-only. QuickCreate sends typed `execution`, one `creative_source`, and `destination.type=web|app`: web requires `web_url`; app requires `app_id`, `store_url`, or `deep_link` and forbids `web_url`. Never substitute Meta raw adapter fields.

Discover one upload window with `creatives_list(created_from=<inclusive>, created_to=<exclusive>)`; bounds are timezone-aware ISO 8601.

## Append

- `append_mode=append-campaign` plus `target_campaign_id`.
- `append_mode=append-adset` plus `target_adset_id`, `execution.campaign_count=1`, and `execution.adset_count=1`; it creates zero Campaigns and zero AdSets, creates the requested Ads only, and inherits the existing parent budget.
- Never send `append_mode=existing`, `existing_campaign_id`, `existing_adset_id`, or `product_ref`.
- Never place QuickCreate counts at the request root (`campaign_count`, `adset_count`) or Copy-only fields (`ads_per_adset`) under `execution`.

| Misplaced path | Use instead |
| --- | --- |
| `request.campaign_count` | `request.execution.campaign_count` |
| `request.adset_count` | `request.execution.adset_count` |
| `request.execution.append_mode` | `request.append_mode` |
| `request.execution.ads_per_adset` | remove; belongs to `copy_ad_quick_copy` only |

On bounded `invalid_fields` (including `expected_path` when present), rerun prepare once, show the new summary, and obtain fresh explicit approval. Never auto-confirm, change permissions, or replay a confirm token. Never reuse confirmation material.

## Grouped Copy

Finish pages serially; preserve every `ad_id` and deduplicate only exact Ad names. `ad_num` duplicates one source Ad; multiple distinct source Ads use `grouped_plan` for 1-1-N or 1-N-1. Do not fall back to a client-built multi-stage copy.

First Ad seeds Campaign settings; each AdSet's first seeds its settings. Show one paused-by-default approval summary with every `settings_source_ad_id`. Pass `cgb_confirm_*` unchanged to `copy_ad_quick_copy_confirm`. Compare `countries_override`, `worldwide_override=true`, `excluded_countries_override`, and `geo_targeting_override`.

If the user omits its Campaign, AdSet, or template reference, stop before preparing. Ask for one concrete reference; never invent objective, budget, bid, app/pixel, placements, compliance, or naming settings.

## Delivery And Recovery

Inspect `setup_get_status.capabilities.delivery_mutations`. If denied, follow `permission_action`: `/dashboard/settings#mcp-access` or OAuth `mcp.optimize.write`. Never change permissions automatically; reconnect and re-list tools.

For one known Campaign, Ad Set, or Ad, do not scan historical or product-level
Insights to discover its current status, budget, or bid. Call the matching
prepare tool directly; prepare reads the live current value and does not mutate
Meta. If an explicit read-only preflight is needed, call
`overview_get_live_configs` with exactly one typed entity and no
`mutation_ref`. `management=true` or product/date Insights is not live
configuration evidence.

Use only this advertised object-field matrix:

## Product-family pause

For pausing every live ACTIVE Campaign under one or more saved products:

1. `products_list` to resolve `product_ref` values.
2. `products_delivery_pause_prepare(product_refs=[...], expected_scope=all_live_active_campaigns)`.
3. Show grouped live campaigns, exclusions (`mapping_required`, `no_routable_token`, `already_paused`, budget drift), and `mutation_count`.
4. After explicit approval, `products_delivery_pause_confirm(confirm_token=pd_confirm_*)` once; `products_delivery_pause_deny` discards.

Never fan out per-campaign `overview_update_campaign_status` prepares when the product pause tool is available. Confirm mutates only the immutable prepared set.

## Singular delivery writes

- Campaign status: `overview_update_campaign_status`, then
  `overview_update_confirm`.
- Campaign budget: `overview_update_campaign_budget`, then
  `overview_update_campaign_budget_confirm`.
- Ad Set status: `overview_update_adset_status`, then
  `overview_update_confirm`.
- Ad Set budget: `overview_update_adset_budget`, then
  `overview_update_confirm`.
- Ad Set bid: `overview_update_adset_bid`, then `overview_update_confirm`.
- Ad status: `overview_update_ad_status`, then `overview_update_confirm`.

Campaign bid is unsupported. Ad budget and Ad bid are unsupported. Stop instead
of substituting another object level or inventing a tool. ABO uses the Ad Set
budget path; CBO uses the Campaign budget path. Stop with `support_ref` when an
advertised tool is absent.

Correct `adsagent_request_incomplete` `invalid_fields` on prepare once. On repeat or `operator_review_required`, stop. On `no_create_permission`, use `/dashboard/assets/fb-users`.

On `mcp_meta_quota_deferred` with `request_sent=false`, `safe_to_retry=true`, `operator_review_required=false`, STOP and follow [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md). Sent/uncertain writes use `operations_get_context`.

Poll `tasks_get_status(task_ref=..., response_mode=compact)`. At terminal, require `result.create_reconciliation.reconciled=true`. Map `creative_results` `ad_name` plus `selection_key`/`selection_keys` to `ad_id`. When `create_reconciliation.next_action` is present, call that exact bounded read once, require `retry_write=false`, and use its live configured/effective/delivery fields for current delivery state. It never authorizes replaying the write and does not prove spend. `approved_task_payload` with `live_verified=false` is not live Meta state.

Claim an exact zero only when the common Insights result has
`metrics_evidence.zero_proven=true`. Otherwise say no metrics were observed and
the exact amount is unproven. `mutation_coverage` is relevant only when the
metrics request supplied `after_mutation_ref`; it never proves live delivery.

Report `result.failures.items` `code`, `message`, and `next_action`; never expose a raw Meta error or retry the unchanged write. `recovered_by_url_fallback` is compensated and never permits retry or a new task. Only `manual_new_task_allowed=true` permits a new task with fresh approval. Stop on `failures.unclassified_count>0`.

Server chunking is not a fixed Meta limit; preserve every acknowledged object and receipt.
Status writes use `target_configured_status=ACTIVE|PAUSED` and
`current_configured_status`. Never pass `effective_status`. After a delivery
confirm, consume inline
`verification` and `verification_result` first. Follow `next_action` to
`overview_get_live_configs` only while pending. A local selector miss after
`mutation_applied=true` is client snapshot drift; preserve `mutation_ref` and
never reauthorize, replace the bearer, or replay the write. Post-write metrics
do not verify delivery configuration.
