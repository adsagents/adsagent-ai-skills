---
name: tiktok-insights
description: Use when the user asks AdsAgent TikTok MCP questions about TikTok advertisers, tenants, TT accounts, campaign/ad group/ad performance, spend, conversions, CPA, ROAS, impressions, clicks, or multi-advertiser TikTok summaries.
---

# TikTok Insights Through AdsAgent

Use this skill for TikTok Ads performance reads through the AdsAgent TikTok hosted MCP. Do not map Meta product fields or Google Ads customer fields onto TikTok requests.

## First Steps

1. Run `setup_get_status` before analysis.
2. Use TikTok MCP's own tenant and advertiser discovery tools. Do not assume Meta product names, Facebook pages, or Google customer IDs exist on TikTok.
3. Choose the specific TikTok advertiser or tenant scope returned by the server.
4. If the user names an advertiser, verify it against the discovered TikTok scopes before querying.
5. Keep the advertiser, date range, and grouping visible in the final answer.

## Freshness And Write Boundary

TikTok stored-data freshness is age-only. It does not advertise require_fresh or Meta-style mutation receipts. An immediate write success is not mutation verification. Keep native task IDs until TikTok capabilities advertise direct `task_ref` polling.

## Query Pattern

- Single scope: use `insights_query_overview`.
- Multiple scopes: use `insights_query_batch_overview`.
- Do not run one request per advertiser, one account at a time, as client-side fan-out.
- If the server returns `mcp_fanout_detected`, stop the advertiser loop and rerun current plus pending scopes through `insights_query_batch_overview`, chunked by the server hint when present.
- Use the server summary/total values. Do not manually sum visible rows and call that complete.
- Trust a scope only when the response marks it complete. Treat missing scopes as unknown, never zero.
- If a scope has many campaigns, ad groups, or ads, preserve the scope payload and report server totals separately from visible rows.

## Retry And Backoff

- For `429` with `mcp_concurrency_limited`, read and honor `Retry-After`, add jitter, then retry serially within a small budget.
- For `429` with `mcp_fanout_detected`, do not retry the same single-scope request; switch to `insights_query_batch_overview`.
- For `503`, treat it as dependency unavailable and follow `/adsagent-reliability`.
- Prefer `insights_query_batch_overview` before parallel reads when the user asks for multiple TikTok advertisers or scopes.
- Parse backoff from the HTTP header, top-level `data`, or JSON-RPC `error.data`; never regex human message text.

## User-Facing Output

Use Markdown tables and concise scope notes:

```markdown
## Answer
Advertiser X spent $123 yesterday.

## Scope
- Platform: TikTok
- Advertiser:
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

Do not dump raw JSON, hidden diagnostics, complete tool catalogs, or platform payload schemas.

For explicit full-table/export requests, poll the returned task handle to terminal and return the artifact link instead of raw rows.
