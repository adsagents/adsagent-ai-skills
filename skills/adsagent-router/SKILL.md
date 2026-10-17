---
name: adsagent-router
description: Use when an AdsAgent request is ambiguous, spans channels, or needs an OAuth tenant choice.
---

# AdsAgent Router

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Use this router for ambiguous workflows or OAuth tenants; otherwise load
the matching skill:

- ambiguous or cross-channel request: stay here long enough to decompose it;
- connection/readiness: `adsagent-setup`;
- transport, retry, partial, or queued failure: `adsagent-reliability`;
- Meta performance/inventory read, including reports or dashboards where a
  template is a grouping, filter, or comparison dimension: `meta-insights`;
  known-entity status, budget, or bid change and a direct Meta
  create/copy/template-object lifecycle request: `meta-copy`;
- Google Ads: `google-ads-insights` (read), `google-ads-create`, `google-ads-manage`;
  TikTok: `tiktok-insights`;
- any prepare/confirm write, `needs_input`, or amount refusal: `adsagent-approvals`;
- deep diagnosis / audit / account health check: `adsagent-diagnosis`;
- notification integration: `adsagent-notifications`;
- agent-owned schedule or automation: `agent-scheduled-tasks`.

For ambiguity, discover enough to ask one clarifying
question. Execute cross-channel plans serially, preserving each channel's
capability and evidence contract.
Unqualified template lifecycle requests require a channel choice.

Read [routing-contract.md](routing-contract.md) only when ambiguous,
cross-channel, or a Meta read-versus-write decision.
