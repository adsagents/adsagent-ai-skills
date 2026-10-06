---
name: adsagent-setup
description: Use when connecting AdsAgent in Claude or another MCP client, authorizing an advertising channel, or resolving missing accounts and setup blockers.
---

# AdsAgent Setup

1. Keep the user's task and channel. Reuse an existing
   connection; do not require all three channels or reinstall a working plugin.
2. Distinguish client MCP OAuth, platform authorization, account discovery,
   data sync, and launch readiness. If tools are unavailable, give the matching
   client connection step from [setup-contract.md](setup-contract.md).
3. Run the selected server's `setup_get_status` when readiness is unknown or
   blocked. Inspect capabilities and return one actionable next step.
4. Use the advertised begin/check flow on its owning server. Share the returned
   browser link; wait for the human, then check the same connection once.
   Never poll OAuth automatically or copy credentials between servers.
5. Recheck readiness after that step and resume the original task. For a
   connection-only request, report the result and stop. Report sync and launch
   blockers separately; never change customer permissions.

Read [setup-contract.md](setup-contract.md) when installing, reconnecting,
authorizing a channel, resolving missing accounts, or evaluating an update notice.

[Data boundary](data-boundary.md) applies.
