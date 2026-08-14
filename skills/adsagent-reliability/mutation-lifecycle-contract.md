# AdsAgent Mutation Lifecycle Contract

Version: `0.2` (pairs with smartads #131 Phase 6 — guide `2026-08-14.9+`)

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

Direct-write families (creative library, uploads) return `mutation_ref` or
`upload_ref` without a separate approval step. On a lost response, recover with
`operations_get` using the exact ref before any retry.

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
