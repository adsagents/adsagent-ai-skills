# Meta Template Persistence Contract

## Snapshot Semantics

Read `adsagent://guide/catalog/templates` before a template workflow. For a
reverse-engineered template, this pack chooses snapshot semantics: source
account/ad set IDs, names, and tags are provenance only. They are not evidence
that Campaign, AdSet, or Ad configuration was saved.

This fail-closed contract applies to a reverse-engineered preview and to a
saved template whose persistence is legacy-projected, false, or unknown. It
does not replace the live guide's normal QuickCreate contract for a template
whose current server-owned persistence and launch semantics are already
authoritative.

`templates_reverse_engineer` returns an unsaved preview. A Hosted version is
launch-safe only when it atomically persists the normalized effective snapshot,
accounts for normalization and every rejected or dropped path, and makes
`templates_get` return a server-owned snapshot identity, immutable content
revision/digest, explicitly complete rejected-path report, and
machine-verifiable launch-readiness evidence. Source fields remain provenance.

For affected templates, this pack defines no positive launch-safe inference
from currently observed fields. Treat readiness evidence as present only when
the live guide explicitly names the authoritative response fields and their
semantics. Never assemble it from maps, timestamps, provenance, or an
absent/null rejected-path report.

Never guess the withheld request schema, invent Meta adapter fields, or fill
defaults. Never copy opaque preview maps wholesale into a write. Never send
source references alone unless the guide explicitly defines a server-owned
snapshot import with the same readiness evidence.

## Write And Read-Back

Before writing a reverse-engineered preview, require the live guide to
advertise all of the following: snapshot-import semantics, the bounded public
write schema, normalization and rejected-path behavior, immutable read-back
identity, and machine-verifiable launch-readiness fields. Advertising
`mcp.templates.write` or a tool name alone is insufficient. If any part is
absent, stop before `templates_create` or `templates_update` and report that
Hosted has not exposed a verifiable template-save contract.

When that contract is present, use `templates_create` or `templates_update`
only when it is advertised under `mcp.templates.write` and the user explicitly
requested that exact write. A payload containing only provenance or metadata
(including source references, names, tags, and `overwrite`) is never a
snapshot write.
For `templates_create`, only when its live guide advertises `overwrite`, use
`overwrite=false` by default; `overwrite=true` is reserved for an
operator-approved replacement, never recovery. Never add it to
`templates_update` unless that exact tool guide exposes it.

The following labels are agent-local, not Hosted response fields. After every
accepted create or update, enter client state
`write_accepted_unverified`. The verification transitions are:

- create: `unsaved_preview -> write_accepted_unverified`;
- update: any prior saved-state label -> `write_accepted_unverified`;
- exact-name get finds the intended object:
  `write_accepted_unverified -> saved_unverified`; and
- authoritative persistence evidence:
  `saved_unverified -> snapshot_persisted_unbound`; and
- fresh-read, prepare-revision, and confirmation-token binding:
  `snapshot_persisted_unbound -> snapshot_verified`.

After one write, call `templates_get` by exact `template_name`. The read-back is
verified only when the server-advertised snapshot evidence:

- binds the accepted write outcome and normalized snapshot to an immutable
  server-owned content revision/digest, while retaining source provenance;
- accounts for effective `campaign_params`, `adset_params`, and `ad_params`;
- contains an explicitly complete report with no unhandled rejected or dropped
  launch-critical paths; and
- covers targeting; promoted object/Pixel/app and conversion event;
  placements, optimization and billing; creative identity/media/copy, CTA and
  destination URL; plus budget and bid unless explicitly runtime-required.

Empty configuration maps, `migration_state.persisted=false`,
`legacy_projection`, or a default-only `effective_creation_defaults`
projection are blockers unless authoritative complete coverage marks the level
not applicable or every omission runtime-required. Non-empty maps,
`migration_state.persisted=true`, `updated_at`, labels, source references, or a
write-success response are still not sufficient without the server's
machine-verifiable snapshot evidence.

If exact-name read-back is missing or identifies another object/revision,
report **write accepted; persistence unverified**. If the intended object
exists but its snapshot readiness is missing, stale, or mismatched, report
**saved but not launch-safe**. Do not auto-update, delete, recreate, overwrite,
or silently substitute defaults or the current live source.

## Template Lifecycle Routing

For an explicit Meta request, use `templates_list` to list saved templates and
`templates_get` to view one exact template. Both are reads under `mcp.read`.
Use `templates_delete` only under `mcp.templates.write` when the user explicitly
requests deletion of the exact named template; never infer deletion from a
cleanup request. Rename is one `templates_update` direct state write using only
the exact public fields advertised by the live guide, followed by exact-name
read-back. Never implement rename as delete-and-recreate.

If the user says only list/view/delete/rename "template" without naming Meta,
Facebook, Google Ads, or TikTok, return to `adsagent-router` for one channel
clarification. Explicit Google Ads or TikTok requests stay with their native
specialist and capability profile; never call Meta template tools for them.

## Validation And QuickCreate

`templates_create` and `templates_update` are direct AdsAgent-state writes, not
prepare calls. On `code=adsagent_request_incomplete` (including
`category=template_request_incomplete`) without non-empty public
`invalid_fields` or `required_fields`, stop and hand off. Preserve any returned
`support_ref`; when it is absent, report that none was returned. Do not probe
the hidden schema by deleting fields or replaying the write.

Public template diagnostics are summaries, never raw mappings, arguments,
payloads, or credentials. Preserve only bounded scalar/string
`invalid_fields`, `required_fields`, and a safe scalar `support_ref`; deduplicate
items and honor `invalid_fields_complete`, `required_fields_complete`,
`support_ref_complete`, and aggregate `diagnostics_complete`. A false
completeness flag means the public diagnostic was truncated or sanitized and
must not be treated as the complete hidden schema.

Even when bounded complete public fields are returned, show the proposed
correction. Any later create or update is a new explicit user request, not an
automatic retry, and it requires another exact-name read-back.

An indeterminate create/update result enters agent-local
`write_outcome_unknown`. Never replay it. Perform at most one exact-name
read-back when advertised, but keep the outcome unknown unless authoritative
write-bound revision/digest evidence identifies that exact write; then hand
off and preserve any returned `support_ref`.

Immediately before `campaigns_quick_create` from a reverse-engineered,
legacy-projected, or persistence-unknown template, get and verify the exact
template again. Use only the exact public binding input and response explicitly
advertised by the live guide. Require the prepare response and its confirmation
token to prove binding to the same immutable snapshot revision/digest, and show
that identity, configuration coverage, and runtime-required inputs in the
approval summary. A client re-read or client-added summary echo is not token
binding. Missing or changed evidence blocks both prepare and confirm.
Persistence verification without all three binding checks is agent-local state
`snapshot_persisted_unbound`, never `snapshot_verified`, and remains
non-launchable.

This Skill guardrail cannot repair or attest persistence. Hosted must reject a
partial snapshot instead of returning success, return bounded actionable
validation evidence, and reject QuickCreate from an unverified or stale
template server-side.
