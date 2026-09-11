---
name: tiktok-insights
description: Use when reading or changing TikTok Ads, creatives, delivery, optimization, MMP, or support through AdsAgent.
---

# TikTok Through AdsAgent

1. Run `setup_get_status`, then inspect the exact advertised TikTok capability
   names before choosing a read, creative, write, optimization, MMP, or support
   workflow.
2. For reads, use one aggregate query or server batch and preserve completeness,
   source snapshot, route, and continuation.
3. For approval-backed ad changes, use the advertised prepare/confirm/recovery
   tools, sanitized review, fresh explicit approval, one confirm, and exact-route
   recovery. For direct operations such as `support_report_error` or
   `creatives_abandon_upload`, follow the exact advertised tool contract and
   user authorization; do not invent a prepare/confirm pair.
4. Never translate Meta object names or semantics into TikTok.
5. Return compact evidence and the next safe action, never raw JSON.

Read [channel-contract.md](channel-contract.md) only for pagination, creative
readiness, QuickCreate/append, receipts, optimization, MMP, or support.
