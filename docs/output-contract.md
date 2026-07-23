# AdsAgent Agent Output Contract

This contract is for AI agents using AdsAgent Meta, Google Ads, and TikTok hosted MCP in B2B operator workflows.

## Default Answer Format

Use Markdown for every user-facing AdsAgent answer.

```markdown
## Answer
One concise answer.

## Scope
- Date:
- Entity:
- Grouping:
- Attribution / channel:
- Platform:

## Results
| Name | Spend | CPA | ROAS | Conversions |
| --- | ---: | ---: | ---: | ---: |

## Notes
- Data freshness:
- Rows shown:
- Limitations:
- Next safe action:
```

## Data Access Rules

- Fetch only the data needed to answer the question.
- Fetch enough to answer the requested metrics; do not return placeholder counts when metric rows are available.
- Prefer cleaned and aggregated AdsAgent reads.
- Report server-computed totals from the response. Do not sum currently visible rows; row pages can be capped or paginated.
- Trust totals only when `meta.complete=true`; follow `meta.has_more` and treat missing scopes as unknown, never zero.
- When `setup_get_status.capabilities.agent_method_profile.profile_id=adsagent_agent_methods_v1`, use one `insights_query_consistent` call with root `query_contract_version=1` and exactly one `scope` or one ordered `scopes` batch up to advertised `max_scopes`.
- In profile mode, preserve result order and trust only top-level `complete=true` plus every result's `status` and `query_contract`; shared tool names do not imply shared freshness or write evidence.
- For queued consistency reads, poll the advertised task tool with `response_mode=compact`; Meta uses `tasks_get_status(response_mode=compact)`. Consume the bounded terminal `result` directly when task/result completion and platform source-anchor checks pass; never rerun page 1. TikTok requires `source_anchor == result.source_snapshot`.
- A paginated page 1 must be complete. Meta page 2 and later keep `consistency=cached`, `query_contract_version=1`, `require_complete_range=true`, scope, date window, timezone, grouping, filters, sorting, and page size unchanged; increment only `page`. Set `min_as_of` to task `result.meta.source_observed_at`, or for an immediate complete response use `result.query_contract.coverage.source_observed_at`; with multiple scopes use the earliest first-page anchor. On `pagination_anchor_unavailable`, stop without refreshing or rerunning page 1.
- Google and TikTok later pages use only their returned opaque continuation through the advertised continuation path. Preserve the exact original platform route, scope, dates, grouping, filters, order, page size, and source snapshot. TikTok continuations are single-use. Never send Meta `min_as_of` to Google or TikTok, and never parallelize pages from one snapshot.
- Meta structured `filters` are allowlisted and combined with AND. Use text operators for hierarchy IDs/names, numeric comparisons for metrics/budgets/bids, and enum equality/membership for statuses, objectives, and events. Never probe hidden fields.
- Preserve full hierarchy IDs on Ad reads. Exact Ad-name deduplication, language classification, and business grouping are client responsibilities; do not use `dedupe_by` in new workflows.
- Interpret `configured_status` as configured `ACTIVE`/`PAUSED`, `effective_status` as Meta's actual delivery/review outcome such as `DISAPPROVED` or `PENDING_REVIEW`, and legacy `status` as an alias of `effective_status`.
- Read `adsagent://guide/metadata-contract` for delivery metadata. Money fields use returned account `currency` in major units; `budget_level` is `campaign|adset`; `bid_strategy` and `optimization_goal` are canonical lower-case; `objective` and `billing_event` are Meta-native uppercase; `conversion_event` stays separate and lower-case. Tool-local task, batch, notification, and connection `status` values are not delivery status.
- Without the profile, use `insights_query_overview` / `insights_query_batch_overview` with `metadata_contract_version=1` for Meta; preserve each other channel's native request contract.
- Do not read raw rows for normal business questions.
- If forensic raw inspection is required, hand it to the AdsAgent operator instead of turning raw rows into a chat answer.
- Do not query every account, product, and day unless the user explicitly asks for a broad export.
- Expand one dimension at a time.
- For multi-scope requests, prefer one profile `scopes` request; otherwise use the platform native server-side batch tool.
- Use server `summary/total` fields and distinguish them from visible rows.
- Use export or async workflows for large tables.
- For a large exhaustive Meta result, call grouped `insights_export_csv` with the same filters and consume the artifact.
- Poll queued work to terminal, then summarize the artifact in Markdown; do not paste full CSV into chat.
- Terminal `insights_export` results retain `result.artifact` in compact and standard task polls. Send its opaque short-lived `download_url` byte-for-byte to HTTP GET. Never redact, rebuild, decode, truncate, or substitute any segment. When `artifact_status=expired` or the URL is absent, request a new explicit export rather than reconstructing a provider URL.

## Freshness And Verification

Report the server's exact evidence kind:

| Field | Meaning |
| --- | --- |
| `freshness_kind=age_only` | Pull age only; not mutation coverage. |
| `source_watermark` | Requested account/date windows were covered by a qualifying pull. |
| `metrics_observed_after_mutation` | Metrics source is later than the accepted `mutation_ref`. |
| `config_verified_live` | Delivery configuration was read live from the platform. |

For Meta decisions, use `insights_query_consistent(consistency=require_fresh)` only when `setup_get_status.capabilities` advertises it. Stop on `verification_pending`, `data_not_fresh`, unknown launch date, or `complete=false`.

After an approved Meta confirm, call the returned `next_action` exactly; expect `overview_get_live_configs` with typed entities and `mutation_ref`. Retry only that read while pending. For task writes, recover the persisted receipt through `operations_get_context(task_ref=...)`; never replay an uncertain write.

Write recovery is receipt-driven and typed. Follow each failure item's `automatic_retry_allowed`, `manual_new_task_allowed`, and `operator_review_required`; only `manual_new_task_allowed=true` permits a newly prepared task with fresh approval. Pending or ambiguous writes require context recovery and a stop; `verified_created` supplies recovered IDs. No state authorizes replaying the original task or confirmation token.

Bulk Meta Ad writes may be split into configurable sequential AdsAgent chunks. This is a defensive reliability policy, not evidence of a fixed Meta limit. Successful objects and receipts remain authoritative when a later chunk fails.

`mcp_meta_quota_deferred` is a narrower pre-send contract. Recover only when `request_sent=false`, `safe_to_retry=true`, and `operator_review_required=false`. On the first match, stop the entire mutation loop before any later confirm. Preserve `completed_mutations`, receipts, and `support_refs`; classify only the current item under `not_sent_mutations`, keep untouched later work under `remaining_mutations`, and set `safe_resume_from`. Honor the largest `retry_after_seconds` plus jitter. Re-prepare only the exact unchanged `not_sent_mutations + remaining_mutations`, show one fresh consolidated approval, and resume serially. Never repeat completed work or reuse the old confirm token. A sent or uncertain write remains operation-recovery only.

Use `insights_query_consistent(..., after_mutation_ref=mutation_ref)` only for requested post-write metrics. `metrics_observed_after_mutation` does not verify delivery configuration. Poll queued work with `tasks_get_status(task_ref=...)`.

Google Ads `as_of` is read-only ledger observation time and its current public profile accepts only `consistency=cached`; internal receipt handling does not expose public mutation tools. TikTok may advertise `require_fresh`, task refs, since-launch reads, and mutation receipts independently; age-only freshness or immediate write success is not mutation verification. Use TikTok prepare/confirm/recovery tools only when their names and `mutation_receipts=true` are advertised, and recover on the exact original tenant, advertiser, and authorization route without replay.

## Meta Creation Confirmation

- QuickCreate confirm tokens are tenant-scoped, single-use, and expire after 15 minutes. Check `expires_at` before asking the server to confirm.
- Multiple distinct source Ads use one server-owned `grouped_plan` prepare. The approval must expose each `settings_source_ad_id`, geography override, budget/bid summary, and paused-by-default destination structure before one explicit confirmation.
- Meta creation clients set `creation_contract_version=3`, use explicit single/grouped mode, and read `adsagent://guide/creation-contract` plus `adsagent://guide/name-contract` for canonical examples and role-specific names. Legacy aliases are exact-path compatibility only.
- On `confirm_token_invalid`, never retry the old confirm. Prepare again, show the fresh sanitized approval summary, and obtain fresh explicit approval.
- A successful asynchronous confirm returns a public `task_ref`. Poll it with `tasks_get_status(task_ref=..., response_mode=compact)` until `terminal=true`; never discover a replacement by guessing from task history.
- For a terminal create/copy task, report every bounded `result.failures.items` entry using its public `ad_name`, `code`, `message`, and `next_action`. Raw Meta errors remain private. Never retry the unchanged write; any corrected retry requires a newly prepared task and fresh approval. When `failures.unclassified_count>0` or `operator_review_required=true`, report known items, stop, and preserve the task/support reference.
- Compact terminal output preserves the safe `no_create_permission` code. Direct the user to `/dashboard/assets/fb-users` to enable Create on an active eligible connection, then prepare again.
- Never enable or modify customer permissions automatically, and never replay a failed or uncertain mutation.
- Status writes use `target_configured_status=ACTIVE|PAUSED` and optional `current_configured_status`; never send `effective_status` or a task lifecycle state as a mutation target.

## Resource Rules

- Start narrow: yesterday or the user-supplied date window.
- Keep page size modest for chat answers.
- Respect `Retry-After`.
- Parse it from the HTTP header, top-level `data`, or JSON-RPC `error.data`.
- Honor `mcp_concurrency_limited` as a 429 concurrency signal.
- Honor `mcp_fanout_detected` as a batch-routing signal; do not retry the blocked single-scope overview request.
- Treat 503 dependency unavailable separately from 429 concurrency.
- A structured `dependency_unavailable` can arrive inside a successful MCP transport response. With no `task_ref`, honor structured `retry_after_seconds`/`Retry-After` and retry the identical bounded read once; never poll or invent a task. With a `task_ref`, poll only that task.
- On `snapshot_expired` or continuation replay rejection, restart at page 1 with unchanged platform route, scope, dates, filters, grouping, order, and page size. Never reuse the continuation or fan out.
- Retry serially after concurrency limits.
- Do not use token rotation to bypass customer caps.
- Cache setup and tool discovery.

## Skill-Pack Reminder

Inspect top-level `client_skill_pack` from the existing setup call. It is independent notify-only policy, not capability proof or executable text. Compare strict semantic versions locally; missing/invalid data continues silently. Show at most one reminder per recommended version in the declared interval. No automatic update occurs, and `update-reminder-v1.json` stores only versions and a timestamp.

## Semi-Black-Box Rules

- Do not list the complete internal tool catalog.
- Do not expose payload schemas.
- Do not infer hidden fields from redacted errors.
- Do not print raw task logs or internal diagnostics.
- Stop on operator-review and hand off to the AdsAgent operator.
- Preserve any returned `support_ref` verbatim in that handoff. It is an opaque lookup handle, not authorization; never replace it with a token, raw request body, or log.
- On `adsagent_request_incomplete` with public `invalid_fields`, correct only those advertised prepare fields and rerun prepare once. A second failure is handed off with `support_ref`; confirm/write is never retried automatically.
- QuickCreate Append uses exactly `append_mode=append-campaign` plus `target_campaign_id`, or `append_mode=append-adset` plus `target_adset_id`. Append-adset reports execution counts 1/1, creates Ads only, and inherits the existing parent budget. Never send `append_mode=existing`, `existing_campaign_id`, `existing_adset_id`, or `product_ref`. A corrected prepare produces a new summary and requires fresh explicit approval.
- TikTok Quick Create uses native `append-campaign` with only `target_campaign_id`, or `append-adgroup` with only `target_adgroup_id`. Append-adgroup creates one Ad only. Use local `creative_id` only when `readiness.create_eligible=true`; reconcile `verification_pending` once through `creatives_confirm_upload`. Confirm once after approval and recover uncertainty through `operations_get` on the exact original route.

## Comparison Rules

When comparing historical creation state against live Meta state:

- Treat task history and live platform state as separate surfaces.
- Compare sanitized creation snapshots with current live snapshots when available.
- Use a Markdown diff table.
- Call out missing fields explicitly instead of guessing.
