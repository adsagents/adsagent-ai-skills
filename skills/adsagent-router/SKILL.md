---
name: adsagent-router
description: Use when an AdsAgent request is ambiguous, spans channels, or needs an OAuth tenant choice.
---

# AdsAgent Router

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Use this router for ambiguous workflows or OAuth tenants; otherwise load
the matching specialized skill:

- ambiguous or cross-channel request: stay here long enough to decompose it;
- connection/readiness: `adsagent-setup`;
- transport, retry, partial, or queued failure: `adsagent-reliability`;
- Meta performance/inventory read, including reports or dashboards where a
  template is a grouping, filter, or comparison dimension: `meta-insights`;
  known-entity status, budget, or bid change and a direct Meta
  create/copy/template-object lifecycle request: `meta-copy`;
- Google Ads: `google-ads-insights`; TikTok: `tiktok-insights`;
- notification integration: `adsagent-notifications`;
- agent-owned schedule or automation: `agent-scheduled-tasks`.

For ambiguity, discover enough scope to ask one clarifying
question. Execute cross-channel plans serially, preserving each channel's
native capability and evidence contract.
Unqualified template lifecycle requests require a channel choice.

Read [routing-contract.md](routing-contract.md) only when the request remains
ambiguous, spans channels, or needs a Meta read-versus-write decision.
