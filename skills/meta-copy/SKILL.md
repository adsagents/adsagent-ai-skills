---
name: meta-copy
description: Use when preparing a Meta Ads creation, copy, budget, status, targeting, or delivery-configuration change through AdsAgent.
---

# Meta Copy And Comparison

1. Inspect `setup_get_status.capabilities.delivery_mutations` and the exact
   object level before preparing anything.
2. Resolve explicit source, destination, parent, naming, and creative inputs.
   Never invent missing campaign, AdSet, template, budget, pixel/app, or
   compliance settings.
3. Call the advertised prepare tool once, show its sanitized summary, and wait
   for fresh explicit approval.
4. Confirm once. Never replay confirmation material or silently switch object
   levels, routes, copy modes, or permissions.
5. Poll the returned task and reconcile created objects and failures before
   reporting completion. Uncertain writes use operation recovery, not retry.

Read [creation-and-copy-contract.md](creation-and-copy-contract.md) only for
QuickCreate, append, grouped/deep copy, budget or status mutation, task
reconciliation, or failure recovery. For a strict pre-send quota defer, also
read [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md).
