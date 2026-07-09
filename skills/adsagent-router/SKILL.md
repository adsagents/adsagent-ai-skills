---
name: adsagent-router
description: "Route AdsAgent requests to the right AdsAgent skill. Use when the user mentions AdsAgent, Meta/Facebook, Google Ads, TikTok, hosted MCP setup, product spend, campaign/adset/ad performance, CPA, ROAS, AppsFlyer, copy ad, duplicate ad, targeting diff, Retry-After, 429, 503, stale sessions, or operator-review."
argument-hint: "<AdsAgent request>"
version: 0.6.2
---

# AdsAgent Router

Use this skill as the first AdsAgent routing layer. Do not do heavy analysis here. Pick the correct AdsAgent skill and continue with the narrowest safe workflow for the named ad platform.

## Route Map

- Meta / Facebook / FB / Page / pixel / campaign copy: use the `meta-insights` skill for reads or the `meta-copy` skill for copy, launch, compare, recreate, and mutation preparation.
- Google Ads / MCC / customer / search / PMax: use the `google-ads-insights` skill for performance reads and account-scoped overview.
- TikTok / advertiser / TT: use the `tiktok-insights` skill for advertiser-scoped performance reads.
- 429 / 503 / Retry-After / concurrency / stale session: use the `adsagent-reliability` skill before retrying.
- setup / connect / OAuth / MCP token: use the `adsagent-setup` skill.
- "Create that again" / clone a campaign or ad set / repeat a previous creation: use the `meta-copy` skill — it routes by source level (ad → quick_copy, campaign/adset → clone_structure, repeat → recreate_from_task) and requires ASKING deep-vs-fresh, never guessing.

## Platform Guardrail

Do not carry Meta tool names or Meta payload fields into Google Ads or TikTok. Each hosted MCP has its own account discovery and insights tool names.

## Default First Product Flow

When the user has just connected AdsAgent or asks for a first test without naming a platform, do not use a hardcoded example account or product name.

Use this flow:

1. Read AdsAgent setup status.
2. Identify the intended platform from the user's words or available connection state.
3. Use that platform's discovery tool: Meta product cards, Google Ads accounts, or TikTok advertiser/tenant discovery.
4. Tell the user how many usable scopes are available and show a short bounded list of names.
5. Ask which scope's today's data they want to inspect.
6. After the user chooses, route to the platform skill and request a cleaned aggregated overview for today.

## General Rules

- Hosted HTTP MCP remains the source of truth.
- Use Markdown for user-facing output.
- Do not read raw rows for normal business questions.
- Do not expose hidden diagnostics, task internals, or payload schemas.
- Do not fan out across all accounts, products, advertisers, customers, and days.
- For multi-scope reads, prefer the platform's server-side batch overview tool.
- For explicit multi-scope Meta comparisons, route to `meta-insights` and call `insights_query_batch_overview` once.
- If the next step is a write or ad creation, route to the `meta-copy` skill and require explicit confirmation.
