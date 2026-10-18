# Google Ads Manage Contract

Use Google Ads fields and tools only. No generic mutate or raw GAQL write exists. Use the confirmation tool named in the prepare result.

For same-kind budget, status or bid changes in one customer, prefer an advertised batch prepare. Show accepted and excluded rows together and confirm the batch once. Existing shared-budget and portfolio operations remain atomic; do not split them into campaign rows. Only advertised tools and schemas are available.

## Tools By Change

| Change | Prepare tool |
| --- | --- |
| Pause / enable campaign, ad group, or ad | `google_ads_status_pause_prepare`, `google_ads_status_enable_prepare`, `google_ads_ad_status_update_prepare` |
| Budget | `google_ads_budget_update_prepare`, `google_ads_shared_budget_update_prepare` |
| Bidding | `google_ads_bidding_update_prepare`, `google_ads_portfolio_target_update_prepare` |
| Dates and ad schedule | `google_ads_campaign_dates_update_prepare`, `google_ads_schedule_replace_prepare` |
| Ad text | `google_ads_ad_text_update_prepare` |
| Keywords and negatives | `google_ads_keyword_create_prepare`, `google_ads_negative_keyword_add_prepare`, `google_ads_negative_location_add_prepare` |
| Assets and groups | `google_ads_asset_link_prepare`, `google_ads_asset_unlink_prepare`, `google_ads_asset_group_update_prepare`, `google_ads_asset_group_link_prepare`, `google_ads_asset_group_unlink_prepare`, `google_ads_extension_asset_create_prepare`, `google_ads_retail_tree_replace_prepare` |
| Conversion actions | `google_ads_conversion_action_create_prepare`, `google_ads_conversion_action_update_prepare`, `google_ads_conversion_action_remove_prepare` |
| Experiments | `google_ads_experiment_create_prepare`, `google_ads_experiment_schedule_prepare`, `google_ads_experiment_initiate_prepare`, `google_ads_experiment_halt_prepare`, `google_ads_experiment_promote_prepare`; read with `google_ads_experiment_state` |
| Recommendations | `google_ads_recommendation_apply_prepare`, `google_ads_recommendation_dismiss_prepare`; read with `google_ads_recommendations_list` |
| Copy an ad | `google_ads_copy_ad_prepare` |
| Other entity rename, status, remove | `google_ads_entity_update_prepare`, `google_ads_entity_remove_prepare`, `google_ads_management_prepare` |

Use the specific tool when one exists; the generic entity and management tools are for changes no specific tool covers. Read the live schema for the fields each tool accepts and do not invent fields. Output-only status, serving, and policy fields are diagnostics, never write payload.

## Rules

- Name the customer, the entity, and the exact before/after in the approval summary. Money values carry their currency; never compare amounts across currencies.
- A budget or bidding change rejected by the amount guard is a stop, not a retry: see `adsagent-approvals`.
- Legacy drafts are tenant-bound, payload-bound, and single-use. Batch recovery can resume proven-unsent rows under the unchanged digest and expiry, as described in `adsagent-approvals`; uncertain and completed rows never replay.
- Removal and conversion-action removal are destructive: ask for an explicit, separate confirmation of the removal itself.
- Stored asset inventory is read with `google_ads_asset_inventory_list`; `asset_inventory_not_synced` means unknown, never zero.

## Test Accounts And Real Writes

Test accounts are marked `test_account` in `google_ads_accounts_list`; they never serve ads or spend money.

- In a test, demo, or verification run, confirm a write only on a customer marked `test_account`. On any other customer stop after the prepare summary, state that nothing was confirmed, and let the draft expire.
- A test account never replaces approval, and you never label an account as a test account yourself.
- Ordinary customer work follows the approval flow in `adsagent-approvals`.

## Recovery

After an uncertain confirm, read the receipt (`google_ads_mutation_receipt_get`) and, only for an exact read-back through the original route, `google_ads_mutation_reconcile`. Reconciliation never resubmits. Unsupported or ambiguous read-back goes to operator review with the latest `support_ref`.
