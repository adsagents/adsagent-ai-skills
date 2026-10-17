---
name: adsagent-approvals
description: Use when an AdsAgent change goes through prepare then confirm, or a prepare or confirm call returns needs_input, a rejection, an amount-guard refusal, or an unknown result.
---

# AdsAgent Approvals

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Shared by Meta, Google Ads, and TikTok write skills.

1. Prepare one change, show the summary, wait for explicit approval, then confirm once with the tool named in the prepare result's `next_action`.
2. `needs_input` is an expected answer: ask the user for the named fields and prepare again. It is not a failure.
3. A rejected prepare or an amount-guard refusal is final for that request: explain it, never retry unchanged or route around it.
4. Never replay a write whose result is unknown; read it back.

Read [approval-contract.md](approval-contract.md) for outcome classes, multi-operation approvals, and recovery.
