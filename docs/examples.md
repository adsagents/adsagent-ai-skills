# Example Prompts

These examples are safe natural-language prompts. They intentionally do not disclose complete MCP schemas or internal payload shapes.

## Setup

```text
Install or refresh AdsAgent MCP using the prompt I copied from Settings -> MCP Access. After reconnecting, verify setup status.
```

```text
Check whether adsagent-ai-skills is installed at v0.6.2 or newer. If it is older, update the user-scope plugin; if it is duplicated in local and user scope, keep user scope and remove local scope. Then tell me to start a fresh Claude Code session.
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
Compare yesterday's spend and CPA for these three product_refs. Use one batch overview request and report the server summaries; do not run one overview request per product.
```

```text
For this product, tell me today's AppsFlyer paid count and revenue. Keep Meta ad metrics and MMP metrics separate.
Use the cleaned product-scoped MMP summary. Do not use per-ad funnel visualization for aggregate totals.
```

## Google Ads Insights

```text
Use AdsAgent Google Ads MCP. Run setup_get_status, then google_ads_accounts_list. Pick an enabled non-manager customer and show yesterday's campaign spend, conversions, CPA, and ROAS.
```

```text
Compare these Google Ads customers over the last 7 days using google_ads_insights_overview_batch. Do not fan out one request per customer. Use server summary/total instead of summing visible rows.
```

```text
For this PMax campaign, summarize asset and campaign performance only after confirming the customer ID is owned by the authenticated user.
```

## TikTok Insights

```text
Use AdsAgent TikTok MCP. Run setup_get_status, discover my TikTok advertisers, then ask which advertiser's yesterday data I want to inspect.
```

```text
For these TikTok advertisers, use insights_query_batch_overview. Do not run one request per advertiser. Report spend, conversions, CPA, ROAS, rows shown, and server total.
```

```text
If TikTok returns 429 or 503, follow Retry-After and the AdsAgent reliability skill instead of retrying in parallel.
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
Find the latest successful copy task for this ad, then compare the creation snapshot with current Meta state.
```

## Output Discipline

```text
When using AdsAgent, first decide the smallest data scope needed: date, entity, grouping, and row budget. Use aggregated/cleaned reads first. Return Markdown only.
```

## Failure Handling

```text
If AdsAgent returns a concurrency limit, wait according to Retry-After and retry with backoff instead of surfacing the first error to me.
```

```text
If AdsAgent returns operator-review, stop and give me a handoff for the AdsAgent operator. Do not retry with guessed payload changes.
```
