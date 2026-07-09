---
name: meta-insights
description: Analyze Meta Ads performance through AdsAgent for B2B operators while keeping queries bounded, aggregated, Markdown-first, and resource-aware. Use when the user asks about AdsAgent, adsagent.md, Meta ads through AdsAgent, product cards, product count, product spend, campaign spend, adset/ad performance, today's spend, yesterday's spend, date ranges, cost, CPA, ROAS, conversions, registrations, impressions, clicks, CTR, CPC, CPM, MMP, AppsFlyer, cohort, country, placement, breakdowns, CSV export, or comparing Meta performance across products/accounts/campaigns/adsets/ads/dates.
argument-hint: "<product, campaign, date range, grouping>"
version: 0.6.1
---

# Meta Insights Through AdsAgent

Use this skill when the user asks performance questions about Meta ads connected to AdsAgent.

This skill is intentionally semi-black-box. It describes safe workflows, not the full MCP tool catalog or backend schema.


## Totals discipline (report, never compute)

Every aggregate read returns a SERVER-computed total — `summary` on
`insights_query_overview`, `totals` on `insights_read_breakdowns` — and it
is the FIRST line of the text preview. Report it verbatim. NEVER sum rows
yourself: rows may be truncated at the read limit, and accounts commonly
carry multiple campaigns with IDENTICAL names (a real account had 5 —
name-keyed manual sums under-count). Reference campaigns by campaign_id,
never by name.

## First Steps

1. Verify AdsAgent setup status before analysis.
2. If the user has not named a product/campaign/account, list product cards first, tell the user how many products exist, show a short bounded list, and ask which product's data they want.
3. Clarify the product, ad account, campaign name, and date range when missing.
4. Prefer today for "current spend", yesterday for completed daily performance, or a short date window when the user asks an open-ended question.
5. Choose grouped summaries for management questions and daily rows for trend analysis.
6. Read the AdsAgent brief guide resource (`adsagent://guide/brief`) for behavior rules; consult the full tool guide (`adsagent://guide/tools`) on demand only — never end-to-end.

## Data-Minimizing Query Pattern

- Start with a compact aggregated overview.
- Fetch exactly one grouping first: account, campaign, adset, or ad.
- Use small page sizes unless the user explicitly asks for a table.
- If the user asks for more detail, expand by one dimension at a time.
- For large tables, use export or async results instead of many paginated reads.
- Keep the selected date range visible in the answer.
- State whether the result is grouped, daily, or exported.
- Do not use raw-row reads for normal operator questions.
- Do not request all accounts, all products, and all days at once.

## Multi-Scope Batch Rule

Use one MCP request for one user question.

- One product or ad account scope: use `insights_query_overview` with the explicit `product_ref` / `product_name` or `ad_account_id`, plus `date_from` and `date_to`.
- Several product or ad account scopes: call `insights_query_batch_overview` once with explicit scopes. Do not launch one `insights_query_overview` call per scope, even if the client can parallelize.
- Ranking product cards by recent spend: use `products_list`; it is already sorted for recent-spend triage. Do not re-rank by fanning out overview calls.
- Report each batch result by its returned scope. If `partial=true`, show the successful scopes and name the failed scopes; do not hide partial failure.
- The server `summary` is the total source of truth. Visible rows may be paginated or capped, so never compute totals from currently visible rows.

## Clean Then Aggregate

AdsAgent already exposes cleaned rollups and product-scoped summaries. Prefer those over raw rows.

Required order:

1. Resolve the narrow business object.
2. Read cleaned or aggregated AdsAgent output.
3. Aggregate or sort only the returned bounded result.
4. Answer in Markdown.

Avoid:

- raw row scans,
- JSON dumps,
- unbounded history,
- joining Meta and MMP data manually unless the tool response already provides the clean relationship.

## MMP And Product Reads

- Resolve the saved product before asking MMP-specific questions.
- Keep Meta metrics and MMP metrics separate in the explanation.
- For today's MMP event totals, use the AdsAgent-provided MMP summary path rather than a per-ad funnel visualization path.
- Use `channel_pid='all'` only when the user asks for cross-channel totals. For a question specifically about Meta, use the Meta channel slug exposed by the live guide.
- Add `breakdown` only when the user explicitly asks for that dimension.
- If cohort freshness is reported, tell the user whether the selected range is fresh, syncing, stale, or missing.

## Markdown Output Contract

Every user-facing answer should be Markdown:

```markdown
## Answer
Campaign X spent $123 yesterday.

## Scope
- Date: 2026-05-21
- Entity: product/campaign/account requested by user
- Grouping: campaign
- Attribution/channel: value / facebook_int / all

## Results
| Campaign | Spend | CPA | ROAS | Conversions |
| --- | ---: | ---: | ---: | ---: |

## Notes
- Data freshness:
- Rows shown:
- Next safe action:
```

Do not output raw JSON. Do not say "2 items" without names and metrics when the response contains usable rows.

## Stability Rules

- Do not fan out across many accounts, products, and days at once.
- Use `insights_query_batch_overview` for explicit multi-product or multi-account comparisons.
- Respect retry and concurrency behavior from the AdsAgent reliability skill.
- If a client only shows a short text preview, explain that the full structured rows may be available in the MCP response.
- If the response is incomplete, ask for a narrower grouping or export instead of guessing.
- Treat `insights_*` concurrency scopes as read-heavy saturation and retry serially.
- Prefer export for operator-requested tables; prefer summarized Markdown for chat answers.

## What Not To Expose

- Do not print raw internal task logs.
- Do not disclose hidden diagnostics.
- Do not infer database structure.
- Do not list every available MCP tool.
- Do not claim a platform-side change happened unless AdsAgent returns the relevant state or live comparison.
- Do not expose raw rows as the answer. If raw detail is explicitly needed for debugging, summarize the finding and hand the raw inspection need to the AdsAgent operator.
