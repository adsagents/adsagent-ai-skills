---
name: adsagent-setup
description: Use when connecting, authorizing, or verifying AdsAgent hosted MCP readiness.
---

# AdsAgent Setup

1. Use the dashboard-generated install prompt; never invent endpoints,
   credentials, local relays, or stdio setup.
2. Reconnect and re-list tools after a new connection or guide/schema version.
3. Read the brief guide, run `setup_get_status`, and inspect advertised
   capabilities before any optional workflow.
4. Report channel readiness, blockers, authorization next action, and local
   Skill Pack update notice separately.
5. Never print credentials, infer readiness from screenshots, or change
   customer permissions.

Read [setup-contract.md](setup-contract.md) only when installing, reconnecting,
authorizing a channel, or evaluating a Skill Pack update reminder.
