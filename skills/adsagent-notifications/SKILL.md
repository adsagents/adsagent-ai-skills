---
name: adsagent-notifications
description: Use when viewing or configuring AdsAgent notifications, email, Feishu, Telegram, or Meta Ads Webhooks.
---

# AdsAgent Notifications

1. For alert status, use `notifications_list`. List
   integrations and read runtime monitoring capabilities when inspecting
   configuration or describing coverage.
2. Use only masked destinations, public refs, and operator-scoped advertised
   tools. Never solicit hidden credentials in chat.
3. For integration changes or test delivery, prepare exactly one action, show
   the sanitized summary, obtain explicit approval, and confirm once.
4. `notifications_scan` updates alerts and may queue delivery to configured
   external channels. Use it only for a requested or already authorized alert
   refresh, with that effect clear; it is not a read-only status check and has
   no separate prepare/confirm pair.
5. Poll any returned task and distinguish provider acceptance from observed
   destination delivery.
6. Never replay an uncertain confirm or change customer FB User permissions.

Read [monitoring-contract.md](monitoring-contract.md) only when explaining
event coverage, thresholds, channel configuration, webhook subscription, test
delivery, or recovery.
