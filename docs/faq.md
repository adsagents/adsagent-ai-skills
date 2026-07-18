# FAQ

## Does this repo include the AdsAgent MCP server config?

No. The authoritative MCP setup prompt is generated inside the AdsAgent dashboard under:

```text
Settings -> MCP Access -> Copy install prompt
```

That prompt stays current as server URLs, guide versions, and onboarding behavior evolve.

## Why not publish the full tool list?

AdsAgent is a semi-black-box product. This repo teaches safe usage patterns without exposing every tool, schema, payload shape, validation rule, or internal diagnostic.

Authenticated agents can read the live AdsAgent MCP guide after connecting to Meta, Google Ads, or TikTok hosted MCP.

## Why does the skill tell agents to stop on operator-review?

Operator-review means the public MCP response is intentionally redacted. Retrying with guessed fields teaches the agent the wrong behavior and can create silent-failure loops.

The correct action is to hand the request to the AdsAgent operator with the public error and its exact `support_ref` when returned. The ref is an opaque lookup handle, not authorization; do not send bearer tokens, raw request bodies, task logs, or hidden diagnostics.

For `adsagent_request_incomplete` with public `invalid_fields`, the agent may first correct those advertised fields and rerun the prepare tool once. Prepare does not write to Meta. A second failure, an unknown redacted rule, or `operator_review_required` is handed off with the exact `support_ref`; confirm/write is never retried automatically.

## Can the agent create ads?

Only after explicit user confirmation. The agent should show a sanitized approval summary first and wait for the user's approval.

QuickCreate confirm tokens are single-use and expire after 15 minutes. The agent checks `expires_at`; on `confirm_token_invalid`, it prepares again, shows the fresh summary, and asks for approval again. It polls the returned `task_ref` with `response_mode=compact`. If the task returns `no_create_permission`, the user must open `/dashboard/assets/fb-users` and enable Create on an active eligible connection. Never enable or modify customer permissions automatically.

When a terminal create/copy task contains `result.failures.items`, the agent reports those bounded public reasons and next actions instead of a generic failure. It never exposes raw Meta errors or retries the unchanged write. Unknown items remain operator-review only.

## Does one install cover Google Ads and TikTok?

Yes. v0.7.9 is an AdsAgent tri-channel skill pack. It includes Meta skills, `google-ads-insights`, `tiktok-insights`, and the platform-neutral `agent-scheduled-tasks` guidance. New Meta connections default to `/mcp/v2` with `/mcp` as the legacy fallback. Google Ads and TikTok use their own hosted MCP URLs, discovery tools, account semantics, and capability-gated profile adapters.

## Can the skill create a scheduled task?

It can teach an Agent to use the scheduler that its client or workflow platform provides. It classifies reminder-only and executable jobs, chooses a bounded cadence, creates or updates once, reads the saved state back, runs the same entrypoint once when supported, and reports the available execution evidence. AdsAgent does not host cron, and a saved reminder is never reported as proof that the task executed.

## Will the skill pack update itself?

No. `client_skill_pack` is notify-only policy. The local helper compares strict semantic versions and suppresses the same reminder for 24 hours; it never receives raw setup data and never executes an update. The agent shows one fixed instruction for Claude Code, a Codex Git checkout, or a manual install, then requires a fresh session after an update.

## Should agents use the same overview tool for every platform?

When `setup_get_status.capabilities.agent_method_profile.profile_id=adsagent_agent_methods_v1`, all three platforms prefer `insights_query_consistent` with exactly one `scope` or one ordered `scopes` batch. Without that profile, Meta and TikTok fall back to `insights_query_overview` / `insights_query_batch_overview`; Google Ads falls back to `google_ads_insights_overview_query` / `google_ads_insights_overview_batch`.

## Does fresh mean the same thing on every platform?

No. Agents must inspect `setup_get_status.capabilities`. Meta can advertise source-watermark and mutation-aware reads. Google Ads currently reports read-only ledger `as_of` and cached consistency only. TikTok may advertise refresh tasks, since-launch reads, and mutation receipts independently. A shared profile or immediate write success is not proof of unsupported freshness or delivery verification.

## What should agent answers look like?

Markdown. The default shape is: answer, scope, compact results table, notes, and next safe action. The agent should not dump raw JSON, raw CSV, raw task logs, or hidden diagnostics into chat.

## Can the agent compare old task state with live Meta state?

Yes, if AdsAgent exposes both the sanitized creation snapshot and the current live platform snapshot through the authenticated MCP session. The agent should not assume task history equals current platform state because humans may edit campaigns directly in the ad platform.

## What if the AI client reports a temporary MCP connection failure?

The client should respect AdsAgent's recovery contract:

- discard stale sessions and re-initialize when told to,
- respect `Retry-After`,
- parse backoff from the header, top-level `data`, or JSON-RPC `error.data`,
- add jitter,
- keep concurrency below server caps,
- switch to the server-side batch overview tool when AdsAgent returns `mcp_fanout_detected`,
- cache setup/discovery instead of repeating it per call.
- trust totals only when the response is complete and treat missing scopes as unknown.

If the retry budget is exhausted, narrow the query or retry later.
