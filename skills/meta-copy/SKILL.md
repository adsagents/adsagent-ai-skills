---
name: meta-copy
description: Use when preparing Meta Ads creation, copy, template write, budget, status, targeting, or delivery change; not analysis.
---

# Meta Copy And Comparison

1. Inspect `capabilities.delivery_mutations` and exact object level. Template
   state requires `capabilities.template_mutations.allowed=true` with
   `required_capability=mcp.templates.write`. Without Resources, use
   `inline_contract`.
2. Resolve source, destination, parent, names, and creatives. Quick Copy uses
   `*_status`, never `status_option`/`append_mode`. Never invent campaign,
   AdSet, template, budget, pixel/app, or compliance. Cross-account copy: call
   the eligible-pages listing action, let the user pick `page_id`, then prepare
   again — never auto-select Page.
3. For known writes, skip Insights preflight: prepare reads live configuration
   without mutation. Show summary and await fresh approval. Templates use
   snapshot contract.
4. Confirm once. Consume inline `verification_result` first; follow read-only
   `next_action` while pending. Never replay or switch level, route, mode, or
   permissions.
5. Reconcile tasks through the matching recovery path. Follow reconciled
   create/copy `next_action` once; proves live state, not spend or replay.

Read [creation-and-copy-contract.md](creation-and-copy-contract.md) for
QuickCreate, append, copy, delivery mutation, reconciliation, or recovery.

Read [template-persistence-contract.md](template-persistence-contract.md) for
template lifecycle or QuickCreate from uncertain template.
