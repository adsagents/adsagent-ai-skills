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

The correct action is to hand the request to the AdsAgent operator with public IDs, requested structure, timestamp, and the public error.

## Can the agent create ads?

Only after explicit user confirmation. The agent should show a sanitized approval summary first and wait for the user's approval.

## Does one install cover Google Ads and TikTok?

Yes. v0.6.1 is an AdsAgent tri-channel skill pack. It includes Meta skills plus `google-ads-insights` and `tiktok-insights`. Google Ads and TikTok use their own hosted MCP URLs, discovery tools, account semantics, and overview tools.

## Should agents use the same overview tool for every platform?

No. Meta and TikTok use `insights_query_overview` for one scope and `insights_query_batch_overview` for multiple scopes. Google Ads uses `google_ads_insights_overview_query` for one scope and `google_ads_insights_overview_batch` for multiple scopes.

## What should agent answers look like?

Markdown. The default shape is: answer, scope, compact results table, notes, and next safe action. The agent should not dump raw JSON, raw CSV, raw task logs, or hidden diagnostics into chat.

## Can the agent compare old task state with live Meta state?

Yes, if AdsAgent exposes both the sanitized creation snapshot and the current live platform snapshot through the authenticated MCP session. The agent should not assume task history equals current platform state because humans may edit campaigns directly in the ad platform.

## What if the AI client reports a temporary MCP connection failure?

The client should respect AdsAgent's recovery contract:

- discard stale sessions and re-initialize when told to,
- respect `Retry-After`,
- add jitter,
- keep concurrency below server caps,
- cache setup/discovery instead of repeating it per call.

If the retry budget is exhausted, narrow the query or retry later.
