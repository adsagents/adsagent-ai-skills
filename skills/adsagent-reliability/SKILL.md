---
name: adsagent-reliability
description: Use when an AdsAgent MCP call fails, retries, fans out, queues, or returns disputed data.
---

# AdsAgent Reliability

1. Classify as read retry, queued work, known-not-sent write,
   uncertain write, or operator review.
2. Obey `next_action`, `task_ref`, `Retry-After`, and capability
   gates. Wait for `poll_after_ms` before each task poll and stop at terminal;
   retain the task reference at a deadline; never resubmit.
   Never infer a retry from prose alone.
3. Retry only bounded reads or operations explicitly proven not sent. Never
   replay a confirm or parallelize recovery.
4. Use terminal results. Preserve completeness, receipts,
   continuation, and `support_ref` boundaries.
5. For reconciled Meta create/copy, follow read-only
   `create_reconciliation.next_action` once; it verifies live state, not spend,
   and never authorizes replay.
6. After two failures or disputed data, follow
   [support-reporting.md](support-reporting.md) with the latest `support_ref`.
7. Stop on unclassified, permission, or operator-review outcomes.
8. Legacy session recovery applies only after a negotiated legacy protocol;
   modern MCP `2026-07-28` is stateless.

Read [recovery-contract.md](recovery-contract.md); when advertised,
[mutation-lifecycle-contract.md](mutation-lifecycle-contract.md) and
[plan-reconciliation-contract.md](plan-reconciliation-contract.md). Use
[retry-parser.md](retry-parser.md) for backoff and
[meta-quota-plan.md](meta-quota-plan.md) for strict Meta quota defer.

[Data boundary](data-boundary.md) applies.
