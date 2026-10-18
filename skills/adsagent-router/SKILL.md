---
name: adsagent-router
description: Use when an AdsAgent request is ambiguous, spans channels, or needs an OAuth tenant choice.
---

# AdsAgent Router

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Use this router for ambiguous workflows or OAuth tenants; otherwise load
the matching skill:

- connection/readiness: `adsagent-setup`;
- transport, retry, partial, or queued failure: `adsagent-reliability`;
- Meta performance or inventory: `meta-insights`; known-entity status/budget/bid
  and create/copy/template lifecycle: `meta-copy`. Templates are creation
  objects, not insights breakdowns;
- Google Ads: `google-ads-insights` (read), `google-ads-create`, `google-ads-manage`;
  TikTok: `tiktok-insights`;
- any prepare/confirm write, `needs_input`, or amount refusal: `adsagent-approvals`;
- deep diagnosis / audit / account health check: `adsagent-diagnosis`;
- notification integration: `adsagent-notifications`;
- agent-owned schedule or automation: `agent-scheduled-tasks`.

Ask one question to resolve ambiguity. Execute cross-channel plans serially,
preserving each channel's capability and evidence contract.
Unqualified template lifecycle requests require a channel choice.

Read [routing-contract.md](routing-contract.md) only when ambiguous,
cross-channel, or a Meta read-versus-write decision.
