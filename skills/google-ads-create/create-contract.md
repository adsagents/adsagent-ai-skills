# Google Ads Create Contract

Use Google Ads fields and tools only. Never substitute Meta or TikTok tools.

## Before Planning

1. `setup_get_status`, then `google_ads_accounts_list`. Choose one customer whose account list entry is usable and is not a manager.
2. `google_ads_creation_capabilities_get(customer_id)` states which campaign types, writer access, and route this customer can create. Switches, writer access, a create route, and the budget ceiling are checked separately from provider eligibility; an unavailable type is a stop, not something to work around.

These are readiness requirements, not mandatory repeated calls. Reuse current
verified evidence for the same connection and customer; refresh it if the scope,
permissions or advertised validity changes, or a response requests a refresh.

## Location And Language Are Required

Search and Performance Max creation both require an explicit location and language choice. Without them the server answers `needs_input`; it never builds a worldwide campaign, and neither should you.

1. Ask the user which countries or regions and which languages they want.
2. Pass the user's country and language names to the creation tool; the server resolves and validates them. Never choose a location or language on the user's behalf and never default to "all". Use all languages only when the user explicitly requests it.
3. When a place is ambiguous, show the returned names and levels and ask the user to choose. `google_ads_geo_targets_suggest` can help explore places; do not turn its results into a separate code-conversion task.
4. Show the approval summary, including locations, exclusions and languages, and confirm only after explicit approval.

For keyword creation, ask for a missing match type. Pass the user's exact, phrase or broad match choice by name; do not silently select broad match.

## Choosing The Tool

| Request | Prepare tool |
| --- | --- |
| Search, Display, Shopping, Demand Gen, or App campaign graph | `google_ads_quick_create_prepare` |
| Performance Max (standard or retail) | `google_ads_pmax_create_prepare` |
| Campaign and budget only | `google_ads_campaign_create_prepare` |
| Ad group | `google_ads_ad_group_create_prepare` |
| Responsive search ad | `google_ads_responsive_search_ad_create_prepare` |
| Keywords | `google_ads_keyword_create_prepare` |

Confirm with the confirmation tool named in the prepare result's `next_action`; the summary is the approval record, and a draft expires, is single-use, and is never reconfirmed.

Quick-create graphs are paused and use existing media references only; they do not upload. Upload or link assets first through the asset prepare tools (`google_ads_asset_upload_prepare`, `google_ads_youtube_asset_prepare`) and check requirements with `google_ads_asset_requirements_get`. For research before planning use `google_ads_keyword_ideas_generate`, `google_ads_keyword_themes`, or `google_ads_keyword_historical_metrics`.

## Not Available

Video campaigns are read-only. Smart campaigns are retired. Hotel and Performance Max Travel are not offered. App engagement and pre-registration stay blocked until the service can verify qualification. A YouTube upload is not Video campaign creation, and a two-resource shell is not a complete campaign graph. Say so and stop; do not emulate these with another tool.

## Test Accounts And Real Writes

Google test accounts are marked `test_account` in `google_ads_accounts_list`; they can read CLOSED, accept normal calls, and never serve ads or spend money.

- In a test, demo, or verification run, confirm a write only on a customer marked `test_account`. For any other customer, stop after the prepare summary, say nothing was confirmed, and leave the draft to expire.
- Never mark an account as a test account yourself, and never choose a test account to avoid an approval step: approval is still required.
- Customer work on real accounts follows the ordinary approval flow in `adsagent-approvals`; this rule limits test flows, not production use.

## After Confirm

Follow the confirm result. If the outcome is uncertain, use only the read-back tools in `adsagent-approvals`; never replay.

## Creative Files

`creatives_list`, `creatives_get` and `creatives_list_folders` read the account's read-only Google Drive cloud folders; Google has no uploaded library here. Pass a file's `selection_key` as `base64_data` to `google_ads_asset_upload_prepare` or as `source_url` to `google_ads_video_upload_prepare`; the original is fetched from Drive then. Images over 5 MiB carry `cloud_file_too_large`. `creatives_cloud_status` is read-only. `creatives_cloud_refresh` queues a refresh of connected cloud folders.
