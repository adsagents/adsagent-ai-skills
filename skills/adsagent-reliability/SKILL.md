---
name: adsagent-reliability
description: Use AdsAgent MCP without overloading the server. Applies when making repeated Meta, Google Ads, or TikTok AdsAgent MCP calls, handling 404 stale sessions, 429 concurrency limits, 503 dependency errors, retries, large reads, exports, or parallel agent work.
argument-hint: "<retry, backoff, concurrency, MCP stability>"
version: 0.6.0
---

# AdsAgent Reliability

Use this skill for every non-trivial AdsAgent MCP session.

The goal is to keep the user experience stable while protecting AdsAgent from client-side fanout, immediate retry loops, and stale-session cascades.

## Platform Batch Tools

Use the platform's server-side batch overview when the user asks for multiple scopes. Do not launch one overview request per account, product, advertiser, or customer from the client.

| Platform | Single-scope overview | Multi-scope overview |
| --- | --- | --- |
| Meta | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok | `insights_query_overview` | `insights_query_batch_overview` |
| Google Ads | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

## Data Budget Before Calls

Before making read-heavy calls, decide the smallest useful query:

- Entity scope: product, account, campaign, adset, or ad.
- Date scope: yesterday, today, last 3 days, or the explicit user window.
- Grouping scope: one grouping at a time.
- Row/page budget: enough to answer, not enough to explore blindly.
- Output shape: Markdown summary, not raw JSON.

If the user did not provide enough scope, ask one clarifying question or use the safest narrow default: yesterday, grouped summary, first page.

Do not under-fetch either. If the user asks for spend, CPA, ROAS, and conversions, the answer must include those metrics when AdsAgent returns them; do not stop at counts such as "2 items found."

## Required Client Behavior

- Cache connection setup when the client supports it.
- Do not re-run initialization and tool discovery for every tool call.
- Keep per-token MCP concurrency bounded.
- Prefer 4 to 6 in-flight calls per token.
- Respect server retry signals.
- Add jitter before retrying.
- Stop after a small retry budget.
- Never parallel-retry after a 429 or 503. Retry serially.
- Do not use multiple tokens to bypass a customer-level cap.

## Stale Session Recovery

If a request returns a recoverable session-not-found response:

1. Discard the cached MCP session id.
2. Re-initialize the MCP connection without sending the stale session id.
3. Retry the original operation once.

Do not treat this as an auth failure. Do not rotate tokens. Do not loop with the old session id.

## Concurrency And Dependency Recovery

If AdsAgent returns HTTP 429 with `error="mcp_concurrency_limited"` or `data.subcode="mcp_concurrency_limited"`:

1. Read the `Retry-After` header when available.
2. Sleep for at least that duration.
3. Add small random jitter.
4. Retry with bounded backoff.
5. Do not fan out overview calls while waiting.
6. Do not show the first concurrency-limit response as a final user-facing failure.
7. Use `data.scope` when present: `token` means reduce this token's parallelism; `customer` means rotating tokens will not help; `insights_token` / `insights_customer` means only insights tools are saturated.

If the retry budget is exhausted, tell the user the request is queued or rate-limited and ask whether to retry later or narrow the query.

If AdsAgent returns HTTP 503 with `error="dependency_unavailable"`, treat `503 dependency unavailable` separately from `429 concurrency`: follow the same `Retry-After + jitter` retry discipline, retry serially within a small budget, but do not discard the MCP session id and do not rotate the bearer token. If it persists, report dependency unavailability rather than describing it as a concurrency cap.

## Large Reads

For broad insights, long date ranges, or product/account fanout:

- Prefer cleaned, aggregated reads first.
- Ask for narrower date, product, account, or grouping when the request is ambiguous.
- For multiple Meta product/account scopes, use `insights_query_batch_overview` once instead of client-side fanout.
- Use export or async workflows when available.
- Avoid launching many independent insight calls at once.
- For multi-scope read-heavy requests, use server-side batch first.
- Do not read raw rows to answer normal business questions.
- Expand one dimension at a time after the summary proves the expansion is needed.
- For CSV/export workflows, return a Markdown summary of what was exported and only include preview rows when the user asked for a table.

## Sister MCP Batch Names

When the user is operating another AdsAgent MCP server, read that server's live guide first and use its native batch tool name:

| Server | One scope | Multiple scopes |
| --- | --- | --- |
| Meta AdsAgent | `insights_query_overview` | `insights_query_batch_overview` |
| TikTok AdsAgent | `insights_query_overview` | `insights_query_batch_overview` |
| Google AdsAgent | `google_ads_insights_overview_query` | `google_ads_insights_overview_batch` |

Do not carry Meta-specific payload fields into TikTok or Google. The shared rule is only: one scope uses the normal overview tool; multiple scopes use the server-side batch overview; retries honor `Retry-After`.

## User-Facing Output

Always convert AdsAgent results into Markdown:

- One-line answer first.
- Scope block with date/entity/grouping/attribution.
- A compact table for metrics.
- Data freshness or limitation notes.
- Next safe action.

Do not paste raw JSON, raw CSV, raw task logs, stack traces, or internal diagnostics into the user conversation.

## Operator-Review Boundary

When AdsAgent returns an operator-review or intentionally redacted rejection:

- Stop.
- Do not guess alternate payload fields.
- Do not probe with similar payloads.
- Ask the AdsAgent operator to inspect internal diagnostics.
- Preserve the user goal, public IDs, account names, date range, and timestamp for handoff.
