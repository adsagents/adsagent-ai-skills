---
name: meta-copy
description: Use when preparing a Meta Ads creation, copy, template, budget, status, targeting, or delivery-configuration change through AdsAgent.
---

# Meta Copy And Comparison

1. For delivery writes inspect `capabilities.delivery_mutations` and the exact
   object level. Template state requires an advertised `mcp.templates.write`
   tool instead.
2. Resolve explicit source, destination, parent, naming, and creative inputs.
   Never invent missing campaign, AdSet, template, budget, pixel/app, or
   compliance settings.
3. For platform writes, prepare once, show the sanitized summary, and wait for
   fresh explicit approval. Template writes follow the snapshot contract.
4. Confirm a prepared platform write once. Never replay confirmation material
   or silently switch object levels, routes, copy modes, or permissions.
5. Poll task-backed platform writes and reconcile results. Their uncertainty
   uses operation recovery; template uncertainty follows the snapshot contract.

Read [creation-and-copy-contract.md](creation-and-copy-contract.md) only for
QuickCreate, append, grouped/deep copy, budget or status mutation, task
reconciliation, or failure recovery. For a strict pre-send quota defer, also
read [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md).

Read [template-persistence-contract.md](template-persistence-contract.md) only
for template list/view, reverse-engineering, create/update/rename/delete,
read-back, or QuickCreate from a reverse-engineered, legacy-projected, or
persistence-unknown template.
