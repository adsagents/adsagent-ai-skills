---
name: adsagent-approvals
description: Use when an AdsAgent change goes through prepare then confirm, or a prepare or confirm call returns needs_input, a rejection, an amount-guard refusal, or an unknown result.
---

# AdsAgent Approvals

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

1. Prefer one advertised batch for same-kind changes in one account. Show accepted and excluded rows, obtain explicit approval, then confirm once with the returned tool.
2. For `needs_input`, ask for the named fields and prepare again. This is not a failure.
3. Explain rejected rows without retrying unchanged or bypassing guards. Accepted rows remain available for approval.
4. Never replay a write whose result is unknown; read it back.

Read [approval-contract.md](approval-contract.md) for outcome classes, multi-operation approvals, and recovery.
