# AdsAgent Monitoring Contract

Use only advertised Meta MCP tools. Current Meta removed notification-channel
configuration and Meta Ads Webhook setup. This is not an OAuth Safe Mode or
operator-scoped visibility problem: do not solicit credentials in chat,
reauthorize for those retired tools, or promise that restricted Settings can
restore them. Never expose internal IDs.

## Inspect

For alert status, use `notifications_list`; for counts, use
`notifications_summary`. Preserve returned public notification refs and use
only the advertised status/severity filters and bounded pagination.

Read `monitoring_capabilities` from the advertised response before describing
coverage. Missing capability evidence stays unknown.

## What AdsAgent Monitors

Cached asset-health monitoring runs after asset refresh,
or `notifications_scan`; it does not call
Meta directly:

- `ad_account_status`
- `ad_account_recharge`
- `page_unpublished`
- `page_ads_restricted`
- `page_no_advertise_access`
- `fb_user_abnormal`
- `fb_user_disabled`
- `fb_user_token_expiring`
- `fb_user_token_expired`

`notifications_scan` is a direct state-changing operation: it updates or
resolves alerts and may generate MCP Events for existing subscriptions. Use it
only when an alert refresh is requested or already authorized, making that
effect clear. A connection check or lingering alert alone is not a request to
scan or send notifications. Use the read-only notification list for status; do not
invent a scan prepare/confirm pair or replay an uncertain scan.

Defaults: remaining spend cap <= 50 major units or <= 10 percent; USER-token
expiry <= 7 days (warning) and already-expired USER tokens (critical);
3600-second cooldown. Product ownership and affected ad-account ids are included
when mapped.

Keep these boundaries explicit:

- MCP Events do not replace Insights pulls.
- MCP Events do not continuously stream spend or balance metrics.
- Balance, Page, and FB User health come from cached asset-health monitoring.
- Monitoring never changes customer permissions.

## Push And Retired Integrations

When both server and client advertise MCP Events support, an explicitly
requested subscription uses the client's supported `events/list` and
`events/subscribe` flow. These are protocol methods, not tools to invent in
`tools/call`. Do not create a webhook receiver or scheduler just to enable
notifications. If the client cannot subscribe, say push is unavailable there
and offer a bounded alert check; never claim background monitoring is active.

Events include `notification.created`, `approval.pending`, `approval.expiring`,
and `task.finished`. Read the relevant detail through `notifications_list`,
`operations_get_approval`, or `tasks_get_status(task_ref)`. An event is never
approval: a pending/expiring approval still requires explicit user approval,
and a finished-task event requires reading its terminal result before claiming
success. Reuse the packaged reliability contract for task polling.

For email, Feishu, Telegram, or Meta Ads Webhook configuration requests, explain
that the current Meta service no longer offers that integration. Offer MCP
Events only if supported and relevant; never collect a destination secret or
send a test message as part of setup.

## Recovery

- Never replay an uncertain scan, acknowledgement, or resolution. Re-read the
  same alert state before deciding what remains.
- Preserve any `support_ref` for operator review.
- Never create, enable, disable, or modify customer FB User permissions.
- Do not treat provider acceptance as destination delivery proof without
  observed state.
