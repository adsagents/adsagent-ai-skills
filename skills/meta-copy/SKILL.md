---
name: meta-copy
description: Use when preparing a Meta Ads creation, copy, template write, budget, status, targeting, or delivery change; not template analysis.
---

# Meta Copy And Comparison

1. Inspect `capabilities.delivery_mutations` and the exact object level.
   Template state instead requires
   `capabilities.template_mutations.allowed=true` with
   `required_capability=mcp.templates.write`. Without Resources, use its
   `inline_contract`.
2. Resolve exact source, destination, parent, names, and creatives.
   Quick Copy uses `*_status`, never `status_option`/`append_mode`.
   Never invent campaign, AdSet, template, budget, pixel/app, or compliance.
3. For known writes, skip Insights preflight: prepare reads live configuration
   without mutation. Show its summary and await fresh approval. Templates use
   the snapshot contract.
4. Confirm once. Consume inline `verification_result` first; follow read-only
   `next_action` only while pending. Never replay or switch level, route, mode,
   or permissions.
5. Reconcile tasks through the matching recovery path. Follow a reconciled
   create/copy `next_action` once; it proves live state, not spend or replay.

Read [creation-and-copy-contract.md](creation-and-copy-contract.md) for
QuickCreate, append, copy, delivery mutation, reconciliation, or recovery.
For a strict pre-send quota defer, also
read [meta-quota-plan.md](../adsagent-reliability/meta-quota-plan.md).

Read [template-persistence-contract.md](template-persistence-contract.md) for
template lifecycle or QuickCreate from an uncertain template.
