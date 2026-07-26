---
name: google-ads-insights
description: Use when reading or analyzing Google Ads accounts, Search, PMax, spend, conversions, campaigns, keywords, or assets through AdsAgent.
---

# Google Ads Insights Through AdsAgent

1. Run `setup_get_status` and inspect the advertised Google capability profile.
2. Discover accounts, then select one enabled non-manager customer or one
   ordered batch of explicit customers. Never analyze an MCC as spend scope.
3. Use one advertised cached aggregate query. Never fan out by customer, date,
   or page.
4. Preserve the login-customer route, source snapshot, opaque continuation,
   and completeness contract.
5. Report concise Markdown with `as_of`; unavailable or incomplete data is
   unknown, never zero.

Read [query-contract.md](query-contract.md) only for account routing,
pagination, retries, fallback tools, exports, or freshness boundaries.
