---
name: adsagent-setup
description: Use when connecting, authorizing, or checking AdsAgent MCP readiness in Claude, ChatGPT, or another client.
---

# AdsAgent Setup

1. Keep the user's task. Reuse existing connections; connect only the
   requested channel.
2. Distinguish client MCP OAuth, platform authorization, account scope,
   history sync, and launch readiness.
3. For missing tools, follow [setup-contract.md](setup-contract.md). Otherwise
   read the selected server's `setup_get_status` when readiness is unknown or
   blocked. Inspect capabilities and return one actionable next step.
4. Use the advertised begin/check flow on its owning server. Share the returned
   link, wait for the human, then check the same connection once. Never poll
   OAuth automatically or copy credentials between servers.
5. Recheck readiness and resume the original task. For setup-only requests,
   report status and stop. Never change customer permissions.

[Data boundary](data-boundary.md) applies.
