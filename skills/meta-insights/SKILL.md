---
name: meta-insights
description: Use when reading or analyzing Meta Ads performance, delivery, MMP, cohorts, exports, or reports where templates are an analysis dimension.
---

# Meta Insights Through AdsAgent

1. Classify health or performance. Template-dimension reports stay here;
   direct template lifecycle uses `meta-copy`.
2. For product health, call `products_list`, select one public `product_ref`,
   then call `products_get_health`. This path does not require a date range or
   an Insights query.
3. For performance, resolve one product/account scope and date range, inspect
   `setup_get_status.capabilities`, and choose one advertised aggregate query.
   Use one server-side batch for multiple scopes; never fan out.
4. Require complete evidence before totals, filtering, pagination, or a
   decision. Missing scopes stay unknown.
5. Preserve opaque task and continuation contracts exactly.
6. Return concise Markdown or the server artifact; never expose raw rows,
   schemas, diagnostics, or internal errors.

Read [query-contract.md](query-contract.md) only when the request needs
filtering, hierarchy metadata, exhaustive pagination, freshness, MMP,
post-write verification, or export handling.

Read [product-health-contract.md](product-health-contract.md) only when the
request asks whether a product, account, Page, Pixel, or delivery path is
healthy, blocked, unavailable, or ready to spend.
