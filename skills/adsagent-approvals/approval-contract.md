# AdsAgent Approval And Protection Contract

Applies to every write on Meta, Google Ads, and TikTok. Channel skills add which tools to call; this contract decides what to do with the answers.

## Prepare, Approve, Confirm

1. Prepare exactly one change. Prepare reads live state and saves a draft; it never changes delivery.
2. Show the sanitized before/after summary, including currency for money and the exact entities.
3. Wait for the user's explicit approval of that summary. Silence, an earlier approval, or approval of a different draft is not approval.
4. Confirm once, using the confirmation tool named in the prepare result's `next_action`. Do not choose a confirmation tool from memory or from a tool list.
5. Drafts expire and are single-use. A used, expired, or failed draft is never reconfirmed; prepare again and obtain fresh approval.

## Dry Run At Prepare (validate_only)

For creates and updates the service asks the platform for a dry run (`validate_only`) before it saves a draft. If the platform would reject the change, prepare returns the platform's reason and creates no draft.

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

When the user wants several operations approved together and the channel offers it (`approval_plan_prepare` on Google and TikTok), prepare the plan, read it with `approval_plan_get`, show every operation, and confirm once (`approval_plan_confirm`) after explicit approval; `approval_plan_deny` discards it. Meta groups same-level updates inside `entities_prepare_update` and the grouped create flow instead. Never fan out single prepares to simulate one approval.

## Results You Cannot Trust Yet

A confirm that returns no clear result, an error after the request left, a timeout, or `verification_pending` is unknown.

1. Do not call confirm again and do not re-prepare the same change.
2. Read it back: Meta and TikTok `operations_get` with the exact reference; Google `google_ads_mutation_receipt_get`, then `google_ads_mutation_reconcile` only for an exact read-back through the original route. Read-back never resubmits.
3. If read-back is unsupported or ambiguous, stop for operator review with the latest `support_ref`.
4. Report to the user what is known and what is not; never claim success from a later read that could have a different cause.

## Expected Outcomes Are Not Failures

Two failed tool calls or disputed data may be reported to support under the channel's consent rules (see `adsagent-reliability`). A `needs_input`, an amount-guard refusal, and a dry-run rejection are expected answers to a request the service understood; do not count them as failures and do not report them.
