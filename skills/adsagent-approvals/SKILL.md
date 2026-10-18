---
name: adsagent-approvals
description: Use when an AdsAgent change goes through prepare then confirm, or a prepare or confirm call returns needs_input, a rejection, an amount-guard refusal, or an unknown result.
---

# AdsAgent Approvals

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Shared by Meta, Google Ads, and TikTok write skills.

1. For same-kind changes to several entities in one account, prefer one advertised batch prepare. Show accepted and excluded rows, obtain one explicit agreement, and confirm once with the returned `confirm_tool`. Legacy results may name that tool in `next_action`.
2. `needs_input` is an expected answer: ask the user for the named fields and prepare again. It is not a failure.
3. A rejected prepare or an amount-guard refusal is final for that row. Explain it without retrying unchanged or routing around it. Other accepted rows in the same batch remain available for approval.
4. Never replay a write whose result is unknown; read it back.

Read [approval-contract.md](approval-contract.md) for outcome classes, multi-operation approvals, and recovery.
