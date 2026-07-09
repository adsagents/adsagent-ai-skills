---
name: meta-copy
description: Copy, compare, diff, inspect, duplicate, recreate, or prepare Meta ad launches through AdsAgent with explicit confirmation and semi-black-box safety. Use when the user asks to copy winning ads, duplicate ads to another ad account, compare current Meta state to creation history, compare old vs live ads, inspect targeting differences, find budget/country/start-time/copy-mode differences, review campaign/adset/ad settings, prepare a launch, or handle operator-review on a copy/create workflow.
argument-hint: "<source ad, target account, copy goal>"
version: 0.6.1
---

# Meta Copy And Comparison

Use this skill when the user asks AdsAgent to copy Meta ads, compare historical creation records, or inspect differences between a prior task and the live Meta state.

User-facing outputs must be Markdown. For comparisons, use a compact diff table. For copy/launch preparation, use an approval summary table.


## Copy/recreate routing (ask at every fork, never guess)

Route by what the user wants to reproduce:

- **A single AD** → `copy_ad_quick_copy` (fan-out of one winning ad).
- **A CAMPAIGN or AD SET** → `copy_ad_clone_structure` — 1:1 tree clone
  where EVERY ad keeps ITS OWN creative (materials 12345 stay 12345,
  never flattened to one).
- **"Create that again" (repeat a past creation)** →
  `campaigns_recreate_from_task` with the task_ref from
  `tasks_list_create_history` — replays the ORIGINAL payload, every
  material re-uploaded fresh.

For BOTH copy paths, then ask **deep vs fresh**:

- deep — each new ad reuses its source ad's original page post;
  engagement (likes/comments) carries over; ads with dead posts are
  listed in the approval summary and SKIPPED, never substituted.
- fresh — every distinct material is re-uploaded once into a new
  creative (shared materials stay shared); nothing is skipped;
  engagement does NOT carry over.

Present the options with these differences and let the user choose
before preparing anything.

## Operating Model

AdsAgent is the operator surface. The agent should describe the user's goal, resolve public handles, prepare the request, and ask for confirmation before any write.

The public MCP response is intentionally sanitized. Do not reconstruct hidden payloads or internal validation logic.

## Safe Copy Flow

1. Identify the source ad, source account, and target account.
2. Confirm the desired structure, budget, countries, start time, and copy mode in plain language.
3. Resolve public library items by name where applicable.
4. Prepare the copy request through AdsAgent.
5. Show the sanitized approval summary.
6. Ask for explicit user confirmation before creation.
7. Poll task status after creation until the task is terminal.

## Comparison Flow

When the user asks what changed between an old launch and today's platform state:

1. Find candidate creation history through AdsAgent's public history surface.
2. Read the sanitized creation snapshot.
3. If the user asks about live manual edits, request the current platform snapshot through AdsAgent.
4. Diff creation-time intent against live state.
5. Report concrete differences in targeting, budget, status, campaign/adset/ad naming, and other user-visible fields.

Do not assume the AdsAgent task history equals today's Meta backend state. A human may have edited the campaign directly in Meta after creation.

Recommended Markdown shape:

```markdown
## Answer
The main difference is country targeting changed from PH to MX.

## Compared
- Creation task:
- Live state:
- Source ad/adset:

## Differences
| Field | Creation snapshot | Live Meta state | Impact |
| --- | --- | --- | --- |

## Notes
- Data source:
- Missing fields:
- Next safe action:
```

## Operator-Review Stop Rule

If AdsAgent returns an operator-review or intentionally redacted rejection:

- Stop immediately.
- Do not retry with guessed field names.
- Do not try smaller variations just to probe the schema.
- Give the user a clean handoff containing public IDs, requested structure, timestamp, and the exact public error.
- Ask the AdsAgent operator to inspect internal diagnostics.

## User Confirmation

Any ad creation, copy, budget change, pause, enable, or targeting change requires explicit confirmation. A reasonable confirmation message includes:

- Source ad or campaign
- Target ad account
- Structure
- Budget
- Countries
- Start time
- Expected side effects

Do not create ads from an ambiguous request.

Do not paste raw task logs, platform payloads, or hidden validation details into the approval summary. The summary is for the operator, not for reverse engineering AdsAgent internals.
