---
name: meta-copy
description: Use when preparing a Meta Ads creation, copy, budget, status, targeting, delivery change, or direct Meta template-object lifecycle operation; not for template analysis.
---

# Meta Copy And Comparison

Use this only when the Meta template is the direct lifecycle object. Analysis
that groups, filters, or describes templates belongs to `meta-insights`.

1. Inspect `capabilities.delivery_mutations` and the exact object level.
   Template state instead requires advertised `mcp.templates.write`.
2. Resolve explicit source, destination, parent, naming, and creative inputs.
   Never invent campaign, AdSet, template, budget, pixel/app, or compliance.
3. For known writes, skip Insights preflight: prepare reads live configuration
   without mutation. Show its summary and await fresh approval. Templates use
   the snapshot contract.
4. Confirm once. Never replay or switch levels, routes, modes, or permissions.
5. Poll task writes and reconcile results through the matching recovery path.

Read [creation-and-copy-contract.md](creation-and-copy-contract.md) for
QuickCreate, append, copy, delivery mutation, reconciliation, or recovery.
For a strict pre-send quota defer, also
read [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md).

Read [template-persistence-contract.md](template-persistence-contract.md) for
template lifecycle or QuickCreate from an uncertain template.
