---
name: google-ads-manage
description: Use when changing an existing Google Ads campaign, budget, bidding, status, schedule, ad text, assets, conversions, experiment, or recommendation through AdsAgent.
---

# Google Ads Manage

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Connection blockers: `adsagent-setup`. Prepare, approval, and error rules: `adsagent-approvals`. New campaigns: `google-ads-create`.

1. Read the current state first with an insights read; name the exact customer and entity.
2. Pick the matching prepare tool from the contract. One prepare is one change; never fan out.
3. Show the before/after summary, wait for explicit approval, then confirm once with the tool named in `next_action`.
4. Location and language stay required whenever targeting is created or replaced.
5. Real writes belong only to test accounts in a test flow: see the contract.

Read [manage-contract.md](manage-contract.md) for tools, limits, and recovery.
