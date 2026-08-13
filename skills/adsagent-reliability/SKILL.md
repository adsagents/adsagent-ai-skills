---
name: adsagent-reliability
description: Use when an AdsAgent MCP call fails, repeats, fans out, queues, or returns partial, uncertain, or retryable evidence.
---

# AdsAgent Reliability

1. Classify the result as read retry, queued work, known-not-sent write,
   uncertain write, or operator review.
2. Obey the returned `next_action`, `task_ref`, `Retry-After`, and capability
   gates. Never infer a retry from prose alone.
3. Retry only bounded reads or operations explicitly proven not sent. Never
   replay a confirm or parallelize recovery.
4. Consume terminal results directly. Preserve completeness, receipts,
   continuation, and `support_ref` boundaries.
5. For reconciled Meta create/copy, follow read-only
   `create_reconciliation.next_action` once; it verifies live state, not spend,
   and never authorizes replay.
6. Stop on unclassified, permission, or operator-review outcomes.
7. Legacy session recovery applies only after a negotiated legacy protocol;
   modern MCP `2026-07-28` is stateless.

Read [recovery-contract.md](recovery-contract.md) and, when advertised,
[mutation-lifecycle-contract.md](mutation-lifecycle-contract.md). Use
[retry-parser.md](retry-parser.md) for transport backoff and
[meta-quota-plan.md](meta-quota-plan.md) only for strict Meta quota defer.
