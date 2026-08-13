# AdsAgent Mutation Lifecycle Contract

Version: `0.1` (client scaffold — pairs with smartads #131)

The hosted MCP service owns canonical payloads, immutable plans, approval
state, dispatch reservations, and recovery. The Skill Pack is a thin policy
client: route, negotiate capabilities, present summaries, preserve safe opaque
handles, and fail closed.

## Handle Discipline

| Handle | Client action | Forbidden use |
| --- | --- | --- |
| `validation_ref` + `base_payload_hash` | Apply one server-advertised bounded patch | Confirm or execute |
| `approval_ref` + `plan_digest` | Resolve exact summary; fresh explicit approval | Regenerate payload or auto-select another approval |
| `mutation_ref` / `operation_ref` | Read execution and receipt state | Re-dispatch an uncertain mutation |
| `task_ref` | Poll the exact asynchronous job | Use as a second idempotency key |
| `support_ref` | Report sanitized diagnostics | Patch, approve, confirm, retry, or resume |
| legacy `confirm_token` | Compatibility-only single-use confirm | Primary recovery mechanism |

## Dual-Stack Rules

1. Read `setup_get_status.capabilities` before advanced writes. Capability
   truth overrides prose assumptions.
2. When durable handles are **not** advertised, keep the current bounded
   prepare/token flow documented in [recovery-contract.md](recovery-contract.md).
3. When durable handles **are** advertised, prefer ref-first recovery and
   never reconstruct canonical JSON from chat history after prepare.
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
