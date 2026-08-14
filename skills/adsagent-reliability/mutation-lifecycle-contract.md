# AdsAgent Mutation Lifecycle Contract

Version: `0.3` (pairs with smartads #131 Phase 5 complete + Phase 6 — guide `2026-08-14.13+`)

The hosted MCP service owns canonical payloads, immutable plans, approval
state, dispatch reservations, and recovery. The Skill Pack is a thin policy
client: route, negotiate capabilities, present summaries, preserve safe opaque
handles, and fail closed.

## Handle Discipline

| Handle | Client action | Forbidden use |
| --- | --- | --- |
| `validation_ref` + `base_payload_hash` | Apply one server-advertised bounded patch | Confirm or execute |
| `approval_ref` + `plan_digest` | Resolve exact summary; confirm with `expected_plan_digest` | Regenerate payload or auto-select another approval |
| `mutation_ref` / `upload_ref` | Read execution and receipt state via `operations_get` | Re-dispatch an uncertain mutation |
| `task_ref` | Poll the exact asynchronous job | Use as a second idempotency key |
| `support_ref` | Report sanitized diagnostics | Patch, approve, confirm, retry, or resume |
| legacy `confirm_token` | Compatibility-only single-use confirm | Primary recovery mechanism |

## Hosted Capability (`capabilities.mutation_lifecycle`)

Read `setup_get_status.capabilities.mutation_lifecycle` before advanced writes.
When advertised, prefer ref-first confirm and recovery:

| Intent | Tool | Required inputs |
| --- | --- | --- |
| Resolve approval | `operations_get_approval` | `approval_ref` |
| Confirm | `operations_confirm_approval` | `approval_ref`, `expected_plan_digest` |
| Deny | `operations_deny_approval` | `approval_ref`, `expected_plan_digest` |
| Recover write/upload | `operations_get` | `mutation_ref` or `upload_ref` |
| Recover task context | `operations_get_context` | `task_ref` |

Legacy confirm tools remain callable (`launch_confirm`, `launch_deny`,
`overview_update_confirm`, `overview_update_deny`,
`notifications_integration_confirm`, `notifications_integration_deny`) through
the documented compatibility window. Use them only when the client cannot select
the preferred tools; never treat them as durable recovery.

## Direct-Write Receipt Families (Phase 5 complete)

These idempotent writes return `mutation_ref` (or `upload_ref` for creative
uploads) without a separate approval step. Async refresh, pull, and export
jobs return `task_ref`; `support_report_error` returns `support_ref`.

| Domain | Example tools | Receipt |
| --- | --- | --- |
| Creative library | creative library mutations and uploads | `mutation_ref` / `upload_ref` |
| Templates | `templates_create`, `templates_update`, `templates_delete` | `mutation_ref` |
| Interests | `interests_save_fetched_pack`, `interests_archive` | `mutation_ref` |
| Products | `products_save_funnel_events`, `products_save_timezone_offset`, `products_link_mmp_app` | `mutation_ref` |
| Permissions | `fb_users_update_permissions`, `assets_update_account_permissions` | `mutation_ref` |
| MMP | `mmp_connect`, `mmp_delete_connection`, `mmp_refresh_connection`, `mmp_save_cohort_config`, `mmp_fetch_cohorts` | `mutation_ref` |
| Setup / connect | `connections_create_intent`, `setup_analyze_products`, `setup_ensure_baseline_templates`, `setup_begin_facebook_connect` | `mutation_ref` |
| Notifications | `notifications_ack`, `notifications_resolve` | `mutation_ref` |
| Tasks | `tasks_cancel` | `mutation_ref` |

On any lost or ambiguous response, call `operations_get` with the exact ref
before retrying. Never replay from chat memory or infer success from a later
read.

Persist when advertised: `tool_name`, `schema_version`, `approval_ref`,
`plan_digest`, `mutation_ref`, `upload_ref`, `task_ref`, `expiry`. Handles are
not interchangeable across tools or tenants.

## Dual-Stack Rules

1. Read `setup_get_status.capabilities` before advanced writes. Capability
   truth overrides prose assumptions.
2. When `mutation_lifecycle` is **not** advertised, keep the bounded
   prepare/token flow documented in [recovery-contract.md](recovery-contract.md).
3. When **advertised**, prefer ref-first recovery and never reconstruct
   canonical JSON from chat history after prepare.
4. A template fetch is selection evidence, not restoration of a prepared plan.
5. Multiple pending approvals are never resolved by choosing the newest item.

## Field Placement (QuickCreate vs Quick Copy)

| Field | QuickCreate | Quick Copy |
| --- | --- | --- |
| `append_mode`, `target_*` | root `request.*` | not accepted |
| `campaign_count`, `adset_count` | `request.execution.*` | root `request.*` |
| `ads_per_adset` | not accepted | root `request.*` |
| `status_option` | not accepted | clone only |

On `adsagent_request_incomplete` with public `invalid_fields`, correct only
the advertised paths (including any `expected_path`) and rerun prepare once.
