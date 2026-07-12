# Safety And Semi-Black-Box Design

AdsAgent is intentionally operated as a semi-black-box MCP product across Meta, Google Ads, and TikTok.

The agent-facing contract should help users succeed without exposing the internal implementation details that make the system easy to clone, probe, or misuse.

## Safe To Publish Later

The skill pack may describe:

- What AdsAgent can help users do.
- Recommended user prompts.
- Safe setup behavior.
- Platform-specific routing across Meta, Google Ads, and TikTok hosted MCP.
- Retry, backoff, and concurrency expectations.
- Confirmation requirements before write actions.
- Operator-review stop rules.
- High-level troubleshooting language.

## Keep Private

The skill pack should not disclose:

- Complete MCP tool catalogs.
- Complete request or response schemas.
- Backend routes.
- Database tables.
- Internal validation categories.
- Raw task logs.
- Platform payload construction logic.
- Hidden copy/create business rules.
- Infrastructure topology beyond user-visible hosted HTTP MCP.

## Why This Matters

Agents are useful, but they can also:

- Make too many calls in parallel.
- Retry immediately after recoverable limits.
- Guess payload fields after a sanitized error.
- Treat stale sessions as auth failure.
- Confuse historical task state with live platform state.
- Reuse Meta tool names or payload fields on Google Ads or TikTok.
- Fan out one overview call per Google customer or TikTok advertiser instead of using server-side batch.
- Treat age-only freshness or an immediate write response as mutation verification.
- Copy Meta consistency/recovery tool names onto Google Ads or TikTok before those servers advertise them.
- Pull raw rows when a cleaned aggregate would answer the question.
- Paste JSON or CSV into chat instead of producing an operator-readable summary.

## B2B Data Discipline

For B2B operators, the correct behavior is not "fetch everything and reason later." The correct behavior is:

1. Identify the business question.
2. Select the narrowest date, entity, and grouping.
3. Read cleaned or aggregated AdsAgent outputs.
4. Expand only when the first answer proves more detail is needed.
5. Return Markdown with scope, metrics, caveats, and next action.

Agents must inspect `setup_get_status.capabilities` before optional consistency or recovery paths. Missing capability means use the existing platform-native workflow and label its evidence truthfully; it does not authorize guessing parity.

Raw-row reads are not a user-facing agent workflow. Forensic/debug cases should become an operator handoff, not a chat dump.

This repo gives agents behavior guardrails while the AdsAgent server enforces hard limits.

## Reliability Boundary

The skill pack is a soft guardrail. It reduces bad behavior from cooperative agents.

The server must still enforce:

- Authentication.
- Per-token and per-customer concurrency limits.
- Queueing or short waits for startup bursts.
- Retryable structured errors.
- Timeouts.
- Async handling for heavy reads.
- Sanitized public errors.
- Bounded date windows and row caps.
- Dedicated read-heavy lanes for insights.

Never rely on docs alone to protect the backend.
