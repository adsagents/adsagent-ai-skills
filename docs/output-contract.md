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
- For a queued Meta consistency read, poll `tasks_get_status(response_mode=compact)`. Consume the terminal `result` directly only when task `status=completed`, `result.status=complete`, and `result.meta.complete=true`; never rerun page 1.
- For later pages keep all filters unchanged and increment only `page`. Set `min_as_of` to the task `result.meta.source_observed_at`, or for an immediate complete response use `result.query_contract.coverage.source_observed_at`; with multiple scopes use the earliest first-page anchor.
- Meta structured `filters` are allowlisted and combined with AND. Use text operators for hierarchy IDs/names, numeric comparisons for metrics/budgets/bids, and enum equality/membership for statuses, objectives, and events. Never probe hidden fields.
- Preserve full hierarchy IDs on Ad reads. Exact Ad-name deduplication, language classification, and business grouping are client responsibilities; do not use `dedupe_by` in new workflows.
- Interpret `configured_status` as configured `ACTIVE`/`PAUSED`, `effective_status` as Meta's actual delivery/review outcome such as `DISAPPROVED` or `PENDING_REVIEW`, and legacy `status` as an alias of `effective_status`.
- Without the profile, use `insights_query_overview` / `insights_query_batch_overview` for Meta or TikTok and `google_ads_insights_overview_query` / `google_ads_insights_overview_batch` for Google Ads.
- Do not read raw rows for normal business questions.
- If forensic raw inspection is required, hand it to the AdsAgent operator instead of turning raw rows into a chat answer.
- Do not query every account, product, and day unless the user explicitly asks for a broad export.
- Expand one dimension at a time.
- For multi-scope requests, prefer one profile `scopes` request; otherwise use the platform native server-side batch tool.
- Use server `summary/total` fields and distinguish them from visible rows.
- Use export or async workflows for large tables.
- For a large exhaustive Meta result, call grouped `insights_export_csv` with the same filters and consume the artifact.
- Poll queued work to terminal, then summarize the artifact in Markdown; do not paste full CSV into chat.

## Freshness And Verification

Report the server's exact evidence kind:

| Field | Meaning |
| --- | --- |
| `freshness_kind=age_only` | Pull age only; not mutation coverage. |
| `source_watermark` | Requested account/date windows were covered by a qualifying pull. |
| `metrics_observed_after_mutation` | Metrics source is later than the accepted `mutation_ref`. |
| `config_verified_live` | Delivery configuration was read live from the platform. |

For Meta decisions, use `insights_query_consistent(consistency=require_fresh)` only when `setup_get_status.capabilities` advertises it. Stop on `verification_pending`, `data_not_fresh`, unknown launch date, or `complete=false`.

After an approved Meta confirm, call the returned `next_action` exactly; expect `overview_get_live_configs` with typed entities and `mutation_ref`. Retry only that read while pending, and recover the persisted receipt through `operations_get` or `operations_get_context`. Never retry an uncertain write.

Use `insights_query_consistent(..., after_mutation_ref=mutation_ref)` only for requested post-write metrics. `metrics_observed_after_mutation` does not verify delivery configuration. Poll queued work with `tasks_get_status(task_ref=...)`.

Google Ads `as_of` is read-only ledger observation time and its current profile accepts only `consistency=cached`. TikTok may advertise `require_fresh`, task refs, since-launch reads, and mutation receipts independently; age-only freshness or immediate write success is not mutation verification. Use TikTok prepare/confirm/recovery tools only when their names and `mutation_receipts=true` are advertised.

## Meta Creation Confirmation

- QuickCreate confirm tokens are tenant-scoped, single-use, and expire after 15 minutes. Check `expires_at` before asking the server to confirm.
- Multiple distinct source Ads use one server-owned `grouped_plan` prepare. The approval must expose each `settings_source_ad_id`, geography override, budget/bid summary, and paused-by-default destination structure before one explicit confirmation.
- Meta creation clients set `creation_contract_version=3`, use explicit single/grouped mode, and read `adsagent://guide/creation-contract` plus `adsagent://guide/name-contract` for canonical examples and role-specific names. Legacy aliases are exact-path compatibility only.
- On `confirm_token_invalid`, never retry the old confirm. Prepare again, show the fresh sanitized approval summary, and obtain fresh explicit approval.
- A successful asynchronous confirm returns a public `task_ref`. Poll it with `tasks_get_status(task_ref=..., response_mode=compact)` until `terminal=true`; never discover a replacement by guessing from task history.
- Compact terminal output preserves the safe `no_create_permission` code. Direct the user to `/dashboard/assets/fb-users` to enable Create on an active eligible connection, then prepare again.
- Never enable or modify customer permissions automatically, and never replay a failed or uncertain mutation.

## Resource Rules

- Start narrow: yesterday or the user-supplied date window.
- Keep page size modest for chat answers.
- Respect `Retry-After`.
- Parse it from the HTTP header, top-level `data`, or JSON-RPC `error.data`.
- Honor `mcp_concurrency_limited` as a 429 concurrency signal.
- Honor `mcp_fanout_detected` as a batch-routing signal; do not retry the blocked single-scope overview request.
- Treat 503 dependency unavailable separately from 429 concurrency.
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

## Comparison Rules

When comparing historical creation state against live Meta state:

- Treat task history and live platform state as separate surfaces.
- Compare sanitized creation snapshots with current live snapshots when available.
- Use a Markdown diff table.
- Call out missing fields explicitly instead of guessing.
