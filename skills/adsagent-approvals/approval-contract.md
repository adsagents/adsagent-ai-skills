# AdsAgent Approval And Protection Contract

Applies to approval-backed writes on Meta, Google Ads, and TikTok. Use the confirmation tool named in the prepare result; the live schema defines the exact fields. Direct operations that the channel skill says follow their own contract (for example TikTok `creatives_abandon_upload` and `support_report_error`) are not covered; do not invent a prepare or confirm step for them. Channel skills add which tools to call; this contract decides what to do with the answers.

## Prepare, Approve, Confirm

1. Prefer one advertised batch prepare for same-kind changes to several entities in one account. Prepare reads live state and saves an approval; it never changes delivery.
2. Show the sanitized before/after summary, including currency for money and the exact entities.
3. Wait for the user's explicit approval of that summary. Silence, an earlier approval, or approval of a different draft is not approval.
4. Confirm once with the confirmation tool named in the prepare result. Do not choose a confirmation tool from memory or from a tool list.
5. Legacy single-use drafts retain their existing expiry and recovery contract. The batch recovery rules below apply only when the live tool advertises them.

## Partial Validation, One Agreement

The batch summary includes every requested row. Show accepted and excluded rows with their reasons. Preserve the complete reviewed change list, including accepted and excluded rows, when confirming; use the live schema for exact fields. An excluded row is never sent. Suggestions are display-only. Accepting a different value requires a new approval and fresh agreement.

One agreement covers one confirmation of all accepted rows. Do not split the batch into per-entity confirmations when one row is excluded. If every row is excluded, nothing is prepared.

An uncertain row stays frozen and is never resent. A proven-unsent row may resume only when the live batch contract permits it, with the same digest and complete reviewed change list before the original expiry. The original agreement still covers those unchanged, unsent rows; no new agreement is needed. Success and queued work are not resent. Queued work is not a verified platform change. A quota wait retains the original expiry and its returned retry time; it does not require a new prepare or agreement for this advertised continuation. The legacy Meta quota-plan re-prepare, fresh-approval, and new-token rules in `adsagent-reliability` apply only outside this advertised batch continuation.

A host safety denial is not permission to repeat a confirmation, change tools, or prepare the same write through another route. The server's unsent-row recovery does not override that denial.

## Dry Run At Prepare (validate_only)

For creates and updates the service may ask the platform for a dry run (`validate_only`) before saving an approval. A rejected single-use prepare returns the reason without a draft. A batch keeps the rejected row visible as excluded while other validated rows remain accepted.

- Show the reason, change only the field it names, and prepare once more with the user's approval of the change.
- If it is rejected again, stop and keep the `support_ref`. Do not loop, vary values at random, or probe the platform with repeated attempts.
- A passing dry run is not approval and does not prove the live change will succeed.

## Outcome Classes

| Outcome | Meaning | Action |
| --- | --- | --- |
| `needs_input` | The request is incomplete or in an unsupported shape; no draft exists | Ask the user for the named fields, then prepare again. Do not guess, do not report it to support, do not escalate to an operator. |
| Invalid fields | A named field is wrong | Correct only the named fields and prepare once. |
| Amount-guard refusal | The money change is refused (for example `money_change_exceeds_guard` on Meta or `over_cap` on Google) | Final for that request. See below. |
| Not sent, safe to retry | The response says nothing was sent and gives a retry step | Follow `next_action` once. |
| Unknown result | The write may or may not have happened | Read it back. Never replay. |
| Permission or connection | Access is missing | Tell the user the dashboard or reconnect step; never change permissions yourself. |
| Operator review | The response says so | Stop and preserve `support_ref`. |

## Amount Guard

The service refuses a budget, bid, or cap change when it is unreasonably large or small for the account, below a platform minimum, or when it has no reference rate for the currency. Rules, limits, and numbers are enforced server-side; never state a threshold, guess one, or try to find it by probing.

- Retrying the same request will never succeed; a refusal is a parameter error, not a transient failure.
- Report the refusal reason in plain language with the amount and currency the user asked for.
- Ask the user for a different amount, or to contact the account owner or support if they believe the amount is right.
- Never split one change into several smaller steps, move it to another level or account, switch currency, or use another tool to reach the same result.

## Several Operations, One Approval

Creation revise changes one unconfirmed creation draft; a batch combines changes to existing entities. Use revise only where the channel advertises it. Supported name, schedule, activation and selection edits replace the displayed summary; show it again and obtain approval of the new digest, because the old digest is invalid. The original expiry does not extend. A change to budget or targeting requires a new prepare. One creation tree remains one approval, including its groups; do not compose separate drafts merely to create that tree.

Same-kind changes use the channel's advertised batch preparation. Different kinds of already validated drafts can use `approval_plan_prepare` when advertised on Meta, Google or TikTok. `approval_plan_get` reads that plan, `approval_plan_confirm` confirms it once, and `approval_plan_deny` discards it. Mixed plans retain their failure-stop contract. Atomic creates, clones, shared budgets and portfolio changes retain one atomic approval; they are not split into batch rows. Never fan out single prepares to simulate one approval.

## Results You Cannot Trust Yet

A confirm that returns no clear result, an error after the request left, a timeout, or `verification_pending` is unknown.

1. Never resend the uncertain row and do not re-prepare it. Legacy drafts are not reconfirmed. A batch's separate, proven-unsent tail follows the bounded recovery rule above.
2. Read it back: Meta and TikTok `operations_get` with the exact reference; Google `google_ads_mutation_receipt_get`, then `google_ads_mutation_reconcile` only for an exact read-back through the original route. Read-back never resubmits.
3. If read-back is unsupported or ambiguous, stop for operator review with the latest `support_ref`.
4. Report to the user what is known and what is not; never claim success from a later read that could have a different cause.

## Expected Outcomes Are Not Failures

Two failed tool calls or disputed data may be reported to support under the channel's consent rules (see `adsagent-reliability`). A `needs_input`, an amount-guard refusal, and a dry-run rejection are expected answers to a request the service understood; do not count them as failures and do not report them.
