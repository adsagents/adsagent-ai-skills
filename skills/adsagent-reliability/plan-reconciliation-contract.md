# Campaign Plan Reconciliation Contract

Guide `2026-08-14.15+`. Tracks SP #65 and SP #71 plan-reconciliation gaps.

## When to use

Before prepare/confirm when a plan names **fixed existing Ad IDs/creatives inside one target campaign** and forbids copies, new IDs, or cross-campaign assets.

For fresh QuickCreate after partial failures, use `campaigns_quick_create` with explicit:

- `creation_intent=fresh|recover`
- `existing_partial_policy=abort|reuse_exact_parents|keep|pause`
- `name_collision_policy=abort|allow_with_warning|suffix`

Never silently route an explicit fresh rebuild to `campaigns_recreate_from_task`.

## Read-only reconcile tool

Call `campaigns_reconcile_campaign_plan` with:

- `ad_account_id`
- `target_campaign_id`
- `requested_items[]` (`requested_identifier`, optional `label`)
- `scope_policy=strict|partial`

The response embeds `plan_reconciliation` with per-item `match_status`, budget completeness, and `launch_readiness`.

## `match_status` values

| Value | Meaning |
|-------|---------|
| `found_in_scope` | Requested item resolves in the target campaign |
| `absent_in_scope` | Not in target campaign |
| `found_outside_scope` | Found elsewhere — never auto-used |
| `ambiguous` | Multiple candidates |
| `inaccessible` | Token/sync gap — fail closed |

## Strict vs partial

- **strict** — any blocker → prepare must fail closed; reconciliation object still returned.
- **partial** — only proceed with explicit omitted items and budget in the approval manifest.

## QuickCreate prepare evidence

When `name_collision_policy=abort`, exact campaign-name collisions block draft creation and return `status=blocked` with `creation_context.name_collisions`.

When `allow_with_warning`, collisions appear in `creation_context` and prepare warnings before approval.

## Delivery truth on paused ads

For “has this ad passed review?” on intentionally paused ads, use `overview_get_live_configs` and read:

- `review_semantics.state`
- `inventory_issue_labels`

Do not infer approval from `effective_status=PAUSED` alone or from absent `DISAPPROVED` / `PENDING_REVIEW` alone.
