# AdsAgent Agent Output Contract

This contract is for AI agents using AdsAgent Meta, Google Ads, and TikTok hosted MCP in B2B operator workflows.

## Default Answer Format

Use Markdown for every user-facing AdsAgent answer.

```markdown
## Answer
One concise answer.

## Scope
- Date:
- Entity:
- Grouping:
- Attribution / channel:
- Platform:

## Results
| Name | Spend | CPA | ROAS | Conversions |
| --- | ---: | ---: | ---: | ---: |

## Notes
- Data freshness:
- Rows shown:
- Limitations:
- Next safe action:
```

## Data Access Rules

- Fetch only the data needed to answer the question.
- Fetch enough to answer the requested metrics; do not return placeholder counts when metric rows are available.
- Prefer cleaned and aggregated AdsAgent reads.
- Report server-computed totals from the response. Do not sum currently visible rows; row pages can be capped or paginated.
- Trust totals only when `meta.complete=true`; follow `meta.has_more` and treat missing scopes as unknown, never zero.
- For one Meta or TikTok product/account/advertiser scope, use `insights_query_overview`; for several explicit Meta or TikTok scopes, call `insights_query_batch_overview` once.
- For one Google Ads customer scope, use `google_ads_insights_overview_query`; for several explicit Google Ads scopes, call `google_ads_insights_overview_batch` once.
- Do not read raw rows for normal business questions.
- If forensic raw inspection is required, hand it to the AdsAgent operator instead of turning raw rows into a chat answer.
- Do not query every account, product, and day unless the user explicitly asks for a broad export.
- Expand one dimension at a time.
- For multi-scope overview requests, prefer server-side batch tools: Meta/TikTok `insights_query_batch_overview`, Google `google_ads_insights_overview_batch`.
- Use server `summary/total` fields and distinguish them from visible rows.
- Use export or async workflows for large tables.
- Poll queued work to terminal, then summarize the artifact in Markdown; do not paste full CSV into chat.

## Resource Rules

- Start narrow: yesterday or the user-supplied date window.
- Keep page size modest for chat answers.
- Respect `Retry-After`.
- Parse it from the HTTP header, top-level `data`, or JSON-RPC `error.data`.
- Honor `mcp_concurrency_limited` as a 429 concurrency signal.
- Honor `mcp_fanout_detected` as a batch-routing signal; do not retry the blocked single-scope overview request.
- Treat 503 dependency unavailable separately from 429 concurrency.
- Retry serially after concurrency limits.
- Do not use token rotation to bypass customer caps.
- Cache setup and tool discovery.

## Semi-Black-Box Rules

- Do not list the complete internal tool catalog.
- Do not expose payload schemas.
- Do not infer hidden fields from redacted errors.
- Do not print raw task logs or internal diagnostics.
- Stop on operator-review and hand off to the AdsAgent operator.

## Comparison Rules

When comparing historical creation state against live Meta state:

- Treat task history and live platform state as separate surfaces.
- Compare sanitized creation snapshots with current live snapshots when available.
- Use a Markdown diff table.
- Call out missing fields explicitly instead of guessing.
