---
name: adsagent-notifications
description: Use when viewing or configuring AdsAgent email, Feishu, Telegram, or Meta Ads Webhooks integrations, including sending a test notification.
---

# AdsAgent Notifications

Use only advertised operator-scoped Meta MCP tools. OAuth Safe Mode hides
credential-taking tools. If absent, do not solicit credentials in chat; direct
the user to dashboard/operator setup. Never expose internal IDs.

## Inspect

Call `notifications_integrations_list` first. Optional `app_ref` and
`ad_account_id` filters are bounded. Use only masked destinations, public refs,
and status.

Read `monitoring_capabilities` before describing coverage. Runtime truth
overrides this guide.

## What AdsAgent Monitors

Meta Ads Webhooks are event-driven and per ad account:

- `effective_status` -> `meta_effective_status` after a live entity read
- `ad_recommendations` -> `meta_ad_recommendation`
- `with_issues_ad_objects` -> `meta_ad_object_issue`
- `creative_fatigue` -> `meta_creative_fatigue`
- `in_process_ad_objects` -> `meta_ad_object_processed`
- `subscriptions` -> `meta_ads_subscription`

Defaults are `effective_status`, `ad_recommendations`, and
`with_issues_ad_objects`. App registration is not account subscription; each
account needs observed subscription state.

Cached asset-health monitoring runs after asset refresh or
`notifications_scan`; it does not call Meta directly:

- `ad_account_status`
- `ad_account_recharge`
- `page_unpublished`
- `page_ads_restricted`
- `page_no_advertise_access`
- `fb_user_abnormal`
- `fb_user_disabled`
- `fb_user_token_expiring`

Defaults: remaining spend cap <= 50 major units or <= 10 percent; USER-token
expiry <= 7 days; 3600-second cooldown. Product ownership is included when
mapped.

Email, Feishu, and Telegram accept all or one exact `notification_type`, with
minimum `info`, `warning`, or `critical` severity.

Keep these boundaries explicit:

- Webhooks do not replace Insights pulls.
- Webhooks do not continuously stream spend or balance metrics.
- Balance, Page, and FB User health come from cached asset-health monitoring.
- `effective_status` webhook events are live-read before AdsAgent emits the
  verified notification.
- Monitoring never changes customer permissions.

## Configure

1. Call `notifications_integration_prepare` with exactly one action.
2. Show its sanitized summary and warnings. Never repeat credentials,
   destinations, recipients, tokens, or secrets.
3. Wait for explicit user approval.
4. Call `notifications_integration_confirm` once with the returned `confirm_token`.
5. If a task is returned, poll `tasks_get_status(task_ref)` to terminal state.

Supported actions are `configure_channel`, `remove_channel`, `test_channel`, `create_meta_app`, `register_meta_app`, `subscribe_meta_account`, and `unsubscribe_meta_account`.

`test_channel` sends one real external message after confirmation. Prepare is
not delivery evidence.

## Recovery

- Confirmation tokens expire after 15 minutes and are single-use.
- Never replay a confirm after success, timeout, transport failure, or uncertain Meta outcome.
- For uncertain Meta results, re-list with the same filter; do not replay.
- Correct `invalid_fields` once by preparing again, then obtain fresh approval.
- Preserve any `support_ref` for operator review.
- Never create, enable, disable, or modify customer FB User permissions.
- Use only the exact eligible route accepted during prepare.
- Do not treat provider acceptance as destination delivery proof without
  observed state.
