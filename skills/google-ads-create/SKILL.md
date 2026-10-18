---
name: google-ads-create
description: Use when creating a Google Ads campaign (Search, PMax, Display, Shopping, Demand Gen, App), ad group, responsive search ad, or keyword.
---

# Google Ads Create

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Connection blockers: `adsagent-setup`. Prepare, approval, and error rules: `adsagent-approvals`.

1. Pick a usable customer with `setup_get_status` and account discovery; reuse current verified evidence for the same connection/customer.
2. Plan within `google_ads_creation_capabilities_get`. Refresh its evidence when the customer, connection, permissions or advertised validity changes.
3. Location and language are required. Pass the user's country and language names; the server resolves them. Never create a worldwide campaign. For `needs_input`, ask for the missing choice, then prepare again.
4. Prepare one paused graph, show the summary, wait for explicit approval, then confirm once.
5. Real writes belong only to test accounts in a test flow: see the contract.

See [create-contract.md](create-contract.md) for tools, assets, and limits.
