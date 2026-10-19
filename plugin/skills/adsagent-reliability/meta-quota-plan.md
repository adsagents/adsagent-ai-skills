# Meta Quota Plan Circuit Breaker

Choose recovery from the live contract. A quota defer alone does not advertise batch continuation.

## Advertised Batch Continuation

Use this path only when the live contract explicitly advertises continuation of the existing batch approval. Stop later writes during the quota wait and honor its returned retry time. Resume only unchanged, proven-unsent rows with the same digest and complete reviewed change list before the original expiry. The original agreement still applies; no new agreement is needed. Do not re-prepare or replace the approval merely because of the quota defer.

Successful and queued rows are never resent; queued work is not verified success. Keep uncertain rows frozen and use operation recovery. A host safety denial or an operator-review requirement stops continuation. The legacy fresh-approval and new-token rules below do not apply to this advertised path. See `adsagent-approvals` for the shared batch contract and the live schema for exact fields.

## Legacy Quota Plans

For a legacy plan without advertised batch continuation, on the first qualifying pre-send quota defer:

1. Stop confirm and mutation calls immediately. Do not probe later items in the blocked window.
2. Freeze successful receipts under `completed_mutations`; never prepare or confirm them again.
3. Put only the current item in `not_sent_mutations` and untouched later items in `remaining_mutations`. Retain `safe_resume_from` and `support_refs` for this legacy recovery.
4. Honor the largest observed `retry_after_seconds` plus jitter. Do not rotate accounts, FB users, or tokens.
5. After the window, re-prepare only the exact unchanged `not_sent_mutations + remaining_mutations`.
6. Show one fresh consolidated approval summary, obtain fresh approval and a new confirm token before resuming serial confirms.
7. Never reuse an old confirm token. Any sent, uncertain, or operator-review result fails closed into operation recovery.

`scripts/meta_quota_plan_guard.py` is the normative pure state machine for legacy quota plans only. It stores no token or platform identifier and emits no audit or log output.
