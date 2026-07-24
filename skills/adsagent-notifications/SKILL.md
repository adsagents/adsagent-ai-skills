---
name: adsagent-notifications
description: Use when viewing or configuring AdsAgent email, Feishu, Telegram, or Meta Ads Webhooks integrations, including sending a test notification.
---

# AdsAgent Notifications

Use only advertised operator-scoped hosted Meta MCP notification integration tools. OAuth Safe Mode does not expose credential-taking integration tools. If these tools are absent, do not solicit credentials in chat; direct the user to the dashboard/operator MCP setup. Never ask for or expose internal database IDs.

## Inspect

Call `notifications_integrations_list` first. Optional `app_ref` and `ad_account_id` filters are bounded. Treat masked destinations, public app refs, subscription refs, and status as the only supported identifiers.

## Configure

For any change:

1. Call `notifications_integration_prepare` with exactly one action.
2. Show the returned sanitized summary and warnings. Never repeat credentials, webhook URLs, recipients, bot tokens, app secrets, or signing secrets.
3. Wait for explicit user approval.
4. Call `notifications_integration_confirm` once with the returned `confirm_token`.
5. If a task is returned, poll `tasks_get_status(task_ref)` to terminal state.

Supported actions are `configure_channel`, `remove_channel`, `test_channel`, `create_meta_app`, `register_meta_app`, `subscribe_meta_account`, and `unsubscribe_meta_account`.

`test_channel` sends one real external message only after confirmation. A prepare response is never delivery evidence.

## Recovery

- Confirmation tokens expire after 15 minutes and are single-use.
- Never replay a confirm after success, timeout, transport failure, or uncertain Meta outcome.
- For uncertain Meta subscription results, call `notifications_integrations_list` with the same public filter and reconcile observed state.
- Correct returned `invalid_fields` once by preparing again, then show the new summary and obtain fresh approval.
- Preserve any `support_ref` for operator review.
- Never create, enable, disable, or modify customer FB User permissions.
- Never guess another FB User route. Use only the exact eligible route accepted during prepare.
- Do not treat provider acceptance as inbox, Feishu chat, Telegram chat, or Meta delivery proof unless the returned task or observed state says so.
