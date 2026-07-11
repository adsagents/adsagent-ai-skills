---
name: google-ads-insights
description: Use when the user asks AdsAgent Google Ads MCP questions about Google Ads accounts, MCC, customer IDs, Search, PMax, spend, conversions, CPA, ROAS, campaigns, ad groups, ads, keywords, assets, or multi-account Google performance summaries.
argument-hint: "<Google Ads customer/account, date range, grouping>"
version: 0.6.2
---

# Google Ads Insights Through AdsAgent

Use this skill for Google Ads performance reads through the AdsAgent Google Ads hosted MCP. Do not reuse Meta product fields, Meta tool names, or TikTok advertiser fields.

## First Steps

1. Run `setup_get_status` before analysis.
2. Discover accessible Google Ads accounts with `google_ads_accounts_list`.
3. Choose an `enabled`, `non-manager` account for normal reads. Do not analyze an MCC manager account as if it were a spend account.
4. If the user names a customer ID, verify it is one of the discovered accounts before querying.
5. Keep the date range, customer, and grouping visible in the final answer.

## Query Pattern

- Single scope: use `google_ads_insights_overview_query`.
- Multiple accounts or multiple scopes: use `google_ads_insights_overview_batch`.
- Do not create client-side fan-out by sending one overview request per customer or date slice.
- If the server returns `mcp_fanout_detected`, stop the single-scope loop and rerun current plus pending customers through `google_ads_insights_overview_batch`, chunked by the server hint when present.
- Use the server returned `summary/total` fields. Do not manually sum visible rows and present that as the total.
- Trust a scope only when the response marks it complete. Treat missing scopes as unknown, never zero.
- If the server returns pagination or a capped visible row list, explain rows shown separately from totals.

## Retry And Backoff

If Google Ads MCP returns `429` with `mcp_concurrency_limited`:

1. Honor `Retry-After + jitter`.
2. Retry serially within a small budget.
3. Prefer the server-side batch tool for multi-scope reads instead of parallel calls.
4. Do not use token rotation or multiple sessions to bypass limits.

Parse backoff from the HTTP header, top-level `data`, or JSON-RPC `error.data`; never regex human message text.

Treat `503` as dependency unavailable, not as a concurrency cap. Follow `/adsagent-reliability` for retry boundaries.

If Google Ads MCP returns `429` with `mcp_fanout_detected`, do not backoff-retry the same call. Switch to the batch overview tool.

## User-Facing Output

Use Markdown tables and concise scope notes:

```markdown
## Answer
Customer X spent $123 yesterday.

## Scope
- Platform: Google Ads
- Customer:
- Date:
- Grouping:

## Results
| Name | Spend | CPA | ROAS | Conversions |
| --- | ---: | ---: | ---: | ---: |

## Notes
- Data freshness:
- Rows shown vs total:
- Next safe action:
```

Do not dump raw JSON, hidden diagnostics, tool schemas, or every returned field.

For explicit full-table/export requests, poll the returned task handle to terminal and return the artifact link instead of raw rows.
