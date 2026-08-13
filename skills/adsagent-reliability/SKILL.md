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
5. For reconciled Meta create/copy tasks, follow the returned read-only
   `create_reconciliation.next_action` once. It verifies live delivery state,
   never spend, and never authorizes replaying the write.
6. Stop on unclassified, permission, or operator-review outcomes.
7. Apply session recovery only after a legacy protocol was negotiated. Modern
   MCP `2026-07-28` is stateless; do not invent a session ID or re-register.

Read [recovery-contract.md](recovery-contract.md) for the query plan, recovery
matrix, task and artifact handling, and cross-channel boundaries. Read
[mutation-lifecycle-contract.md](mutation-lifecycle-contract.md) for durable
handle discipline and ref-first recovery when the hosted service advertises it.
Read [retry-parser.md](retry-parser.md) only when parsing transport backoff. Read
[meta-quota-plan.md](meta-quota-plan.md) only for a strict Meta quota defer.
