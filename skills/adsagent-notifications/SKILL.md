---
name: adsagent-notifications
description: Use when inspecting AdsAgent alerts, requesting an alert refresh, or explaining MCP Events and retired notification integrations.
---

# AdsAgent Notifications

1. For Meta alert status, use `notifications_list` or `notifications_summary`.
   Inspect returned monitoring capabilities before describing coverage.
2. Current Meta MCP no longer configures email, Feishu, Telegram, or Meta Ads
   Webhooks. Explain that boundary; never collect integration credentials or
   invent configuration tools.
3. `notifications_scan` changes alert state and may generate MCP Events. Use
   it only for a requested or already authorized alert refresh, with that
   effect clear; it is not a read-only status check and has no separate
   prepare/confirm pair.
4. MCP Events require advertised server and client support. An event carries
   references, not approval or proof of completion; read the referenced state.
5. Acknowledge or resolve an alert only when requested. Never replay an
   uncertain change or modify customer FB User permissions.

Read [monitoring-contract.md](monitoring-contract.md) only when explaining
event coverage, thresholds, retired integrations, push support, or recovery.

[Data boundary](data-boundary.md) applies.
