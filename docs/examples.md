# Example Prompts

These examples are safe natural-language prompts. They intentionally do not disclose complete MCP schemas or internal payload shapes.

## Setup

```text
Install or refresh AdsAgent MCP using the prompt I copied from Settings -> MCP Access. After reconnecting, verify setup status.
```

```text
After setup, inspect top-level client_skill_pack once. Compare it with my installed adsagent-ai-skills package-root VERSION using the packaged reminder helper. Never auto-update; show only the fixed instruction for my detected install method, then tell me to start a fresh session after any update.
```

```text
Check whether my AdsAgent account is ready to analyze Meta, Google Ads, and TikTok ads.
```

## Meta Insights

```text
Use AdsAgent to list my product cards, tell me how many products I have, show a short bounded list of product names, and ask which product's today data I want to inspect.
Answer in Markdown and do not read raw rows.
```

```text
Find the top campaigns for this product over the last 3 days. Start grouped by campaign, then ask me before expanding to adset or ad rows.
```

```text
Show campaign-level spend, revenue, CPA, and ROAS for yesterday. If the result is too large, export it instead of making many parallel calls.
```

```text
Before making a Meta budget decision, check setup_get_status.capabilities. If adsagent_agent_methods_v1 is advertised, send one query_contract_version=1 request and trust only top-level complete=true. Otherwise preserve the native flow. Stop on verification_pending, data_not_fresh, unknown launch date, or incomplete results.
```

```text
If a Meta require_fresh read queues work, poll tasks_get_status with response_mode=compact. On a complete terminal result, use that result directly and never rerun page 1. For later pages preserve every filter and pin min_as_of to the first-page source_observed_at; use the earliest source anchor for multiple scopes.
```

```text
After I approve this Meta delivery change, call the returned next_action exactly. Expect overview_get_live_configs with typed entities and mutation_ref; retry only that read while pending. Use operations_get_context if interrupted. If I also ask for post-write metrics, use after_mutation_ref separately; it does not verify delivery configuration. Do not repeat an uncertain write.
```

```text
Compare yesterday's spend and CPA for these three product_refs. Use one batch overview request, require meta.complete=true, and report missing scopes as unknown; do not run one overview request per product.
```

```text
Find every Ad whose Campaign name contains "partnership" and spend is greater than 200 in this product for the last 7 days. Use group_by=ad and one server-side AND filters plan. Return full account, Campaign, AdSet, and Ad IDs/names plus configured_status, effective_status, daily_budget, lifetime_budget, objective, optimization_goal, billing_event, conversion_event, pixel_id, and app_id. Keep page_size<=50 and paginate serially on one source anchor. Preserve every ad_id; after retrieval, deduplicate exact ad_name values and classify language in the client. If the complete table is large, use grouped insights_export_csv with the identical filters and return its artifact.
```

```text
For this product, tell me today's AppsFlyer paid count and revenue. Keep Meta ad metrics and MMP metrics separate.
Use the cleaned product-scoped MMP summary. Do not use per-ad funnel visualization for aggregate totals.
```

## Google Ads Insights

```text
Use AdsAgent Google Ads MCP. Run setup_get_status, inspect agent_method_profile, then google_ads_accounts_list. Pick an enabled non-manager customer. When the profile is advertised, use one query_contract_version=1 insights_query_consistent request with consistency=cached; otherwise use the native overview fallback.
```

```text
Compare these Google Ads customers over the last 7 days. Prefer one insights_query_consistent scopes request when adsagent_agent_methods_v1 is advertised; otherwise use google_ads_insights_overview_batch. Do not fan out one request per customer or sum visible rows.
```

```text
Report Google Ads as_of as read-only ledger observation time. Do not claim Meta-style require_fresh or mutation verification.
```

```text
For this PMax campaign, summarize asset and campaign performance only after confirming the customer ID is owned by the authenticated user.
```

## TikTok Insights

```text
Use AdsAgent TikTok MCP. Run setup_get_status, discover my TikTok advertisers, then ask which advertiser's yesterday data I want to inspect.
```

```text
For these TikTok advertisers, inspect agent_method_profile. Prefer one query_contract_version=1 insights_query_consistent scopes request when advertised; otherwise use insights_query_batch_overview. Preserve result order and report server totals and completeness.
```

```text
If TikTok returns 429 or 503, follow Retry-After and the AdsAgent reliability skill instead of retrying in parallel.
```

```text
Use TikTok require_fresh, since_launch, task_ref polling, and delivery receipts only when each capability is advertised. An age-only result or immediate write success is not mutation verification, and a TikTok receipt is not Meta config_verified_live evidence.
```

```text
If TikTok advertises mutation_receipts=true plus delivery prepare, confirm, and operation-get tools, prepare first, confirm once after approval, and recover uncertain outcomes with operation-get. Never replay the write.
```

## Meta Copy And Comparison

```text
Compare the ad created on May 16 with the live version today. Tell me what targeting changed.
Return a Markdown diff table. Do not expose raw task logs.
```

```text
Prepare a copy of this winning ad into the target account with 5 adsets and a $50 daily campaign budget. Show me the approval summary before creating anything.
```

```text
After the bounded Ad read is complete, preserve each source ad_id and ad_account_id, deduplicate exact Ad names, and group the remaining Ads by my explicit language rules. For multiple distinct source Ads, use one copy_ad_quick_copy grouped_plan prepare. Show the paused-by-default structure, every settings_source_ad_id, budget, bid, and geo_targeting_override. Do not confirm until I explicitly approve; then use the returned token once and poll its task_ref to terminal.
```

```text
For QuickCreate, check expires_at and confirm the single-use token within 15 minutes only after I approve the displayed summary. If confirm_token_invalid is returned, prepare again, show the fresh summary, and ask me again. Poll the returned task_ref with response_mode=compact. On no_create_permission, send me to /dashboard/assets/fb-users; never enable or modify customer permissions automatically.
```

```text
Find the latest successful copy task for this ad, then compare the creation snapshot with current Meta state.
```

## Output Discipline

```text
When using AdsAgent, first decide the smallest data scope needed: date, entity, grouping, and row budget. Use aggregated/cleaned reads first. Return Markdown only.
```

## Agent Scheduled Tasks

```text
Create a daily 09:30 reminder in Asia/Kuala_Lumpur in this existing thread. Treat it as reminder-only, read the saved schedule back, and do not claim it executed until the scheduler exposes a run record.
```

```text
Create a daily AdsAgent monitoring task for this product_ref. Use a versioned rule, server-side batch, complete coverage, bounded retry, and an append-only run log. Read the schedule back and run the same entrypoint once now. Do not change delivery unless the hosted MCP advertises every required prepare, confirm, receipt, and read-back capability.
```

## Failure Handling

```text
If AdsAgent returns a concurrency limit, wait according to Retry-After and retry with backoff instead of surfacing the first error to me.
```

```text
If AdsAgent returns operator-review, stop and give me a handoff for the AdsAgent operator. Do not retry with guessed payload changes.
```
