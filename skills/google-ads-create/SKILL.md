---
name: google-ads-create
description: Use when creating a new Google Ads campaign (Search, PMax, Display, Shopping, Demand Gen, App), ad group, responsive search ad, or keyword through AdsAgent.
---

# Google Ads Create

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Connection blockers: `adsagent-setup`. Prepare, approval, and error rules: `adsagent-approvals`.

1. Establish readiness with `setup_get_status` and account discovery, then pick one usable customer. Reuse current verified evidence on the same connection/customer when available.
2. Use `google_ads_creation_capabilities_get` evidence before planning; plan only what it allows. Refresh it when the customer, connection, permissions or advertised validity changes.
3. Location and language are required. Pass the user's country and language names; the server resolves them. Never create a worldwide campaign. For `needs_input`, ask for the missing choice, then prepare again.
4. Prepare one paused graph, show the summary, wait for explicit approval, then confirm once.
5. Real writes belong only to test accounts in a test flow: see the contract.

Read [create-contract.md](create-contract.md) for the tool per campaign type, assets, and limits.
