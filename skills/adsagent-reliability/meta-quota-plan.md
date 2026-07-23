# Meta Quota Plan Circuit Breaker

On the first qualifying pre-send quota defer:

1. Stop confirm and mutation calls immediately. Do not probe later items in the blocked window.
2. Freeze successful receipts under `completed_mutations`; never prepare or confirm them again.
3. Put only the current item in `not_sent_mutations` and untouched later items in `remaining_mutations`.
4. Honor the largest observed `retry_after_seconds` plus jitter. Do not rotate accounts, FB users, or tokens.
5. After the window, re-prepare only the exact unchanged `not_sent_mutations + remaining_mutations`.
6. Show one fresh consolidated approval summary before resuming serial confirms.
7. Never reuse an old confirm token. Any sent, uncertain, or operator-review result fails closed into operation recovery.

`scripts/meta_quota_plan_guard.py` is the normative pure state machine. It stores no token or platform identifier and emits no audit or log output.
