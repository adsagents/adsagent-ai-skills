---
name: adsagent-reliability
description: Use when an AdsAgent MCP call fails, retries, fans out, queues, or returns disputed data.
---

# AdsAgent Reliability

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

1. Classify as read retry, queued work, known-not-sent write,
   uncertain write, or operator review.
2. Obey `next_action`, `task_ref`, `Retry-After`, and capability
   gates. Wait for `poll_after_ms` before each task poll and stop at terminal;
   retain task refs at deadlines; never resubmit.
   Never infer a retry from prose alone.
3. Retry only bounded reads or operations explicitly proven not sent. Never
   replay a confirm or parallelize recovery.
4. Use terminal results. Preserve completeness, receipts,
   continuation, and `support_ref` boundaries.
5. For reconciled Meta create/copy, follow read-only
   `create_reconciliation.next_action` once; never replay.
6. After two failures or disputed data, follow
   [support-reporting.md](support-reporting.md) with the latest `support_ref`.
7. Stop on unclassified, permission, or operator-review outcomes.
   `needs_input` and amount refusals are not failures: `adsagent-approvals`.
8. Legacy recovery requires a negotiated legacy protocol;
   MCP `2026-07-28` is stateless.

Read [recovery-contract.md](recovery-contract.md); when advertised,
[mutation-lifecycle-contract.md](mutation-lifecycle-contract.md) and
[plan-reconciliation-contract.md](plan-reconciliation-contract.md). Use
[retry-parser.md](retry-parser.md) for backoff and
[meta-quota-plan.md](meta-quota-plan.md) for Meta quota defer.
