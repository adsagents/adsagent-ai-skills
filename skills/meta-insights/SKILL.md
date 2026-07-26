---
name: meta-insights
description: Use when reading or analyzing Meta Ads performance, delivery metadata, MMP, AppsFlyer, cohorts, or exports through AdsAgent.
---

# Meta Insights Through AdsAgent

1. Resolve one product/account scope and date range with public handles.
2. Inspect `setup_get_status.capabilities` and choose one advertised aggregate
   query. Use one server-side batch for multiple scopes; never fan out.
3. Require complete evidence before totals, filtering, pagination, or a
   decision. Missing scopes stay unknown.
4. Preserve opaque task and continuation contracts exactly.
5. Return concise Markdown or the server artifact; never expose raw rows,
   schemas, diagnostics, or internal errors.

Read [query-contract.md](query-contract.md) only when the request needs
filtering, hierarchy metadata, exhaustive pagination, freshness, MMP,
post-write verification, or export handling.
