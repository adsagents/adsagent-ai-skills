---
name: adsagent-router
description: Use when an AdsAgent request is ambiguous or spans channels and needs one specialized workflow selected.
---

# AdsAgent Router

Do not use this router when one channel and one workflow are already clear.
Load only the matching specialized skill:

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

For an ambiguous request, discover only enough scope to ask one clarifying
question. For a cross-channel request, execute one channel plan at a time and
preserve each channel's native capability and evidence contract.
An unqualified list/view/delete/rename-template request is ambiguous until the
user names the channel.

Read [routing-contract.md](routing-contract.md) only when the request remains
ambiguous, spans channels, or needs a Meta read-versus-write decision.
