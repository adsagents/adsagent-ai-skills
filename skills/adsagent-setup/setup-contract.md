# AdsAgent Setup Contract

## Plugin vs MCP (distribution split)

| Surface | What it is | Where |
| --- | --- | --- |
| **Claude plugin** (this repo) | Behavior skills + root `.mcp.json` HTTP MCP URLs | `adsagent@adsagent` from marketplace `adsagent` |
| **Cursor plugin** (this repo) | Behavior skills + root `mcp.json` HTTP MCP URLs | `.cursor-plugin/plugin.json` when installed from Cursor Marketplace |
| **Anthropic Connectors Directory** | Hosted MCP server listing only | Registered separately on `adsagent.md` services — not this plugin package |
| **Dashboard install prompt** | Manual MCP-only fallback for non-plugin clients | Settings -> MCP Access -> Copy install prompt |

When the Claude plugin is installed, OAuth MCP setup comes from this repo's
`.mcp.json`. When the Cursor plugin is installed, OAuth MCP setup comes from
`mcp.json` (same URLs). Do not add `headers.Authorization` to either file.

For Claude web/Desktop or Cowork, use the installed connection's **Connect**
action in Settings -> Connectors. If only skills are installed and no AdsAgent
connector exists, add a custom connector with the requested channel's hosted
URL below and complete browser OAuth. Do not give terminal commands to a
Claude chat user. Organization-managed connectors may need an administrator
to enable them.

For Claude Code, use `/mcp` to authenticate the selected bundled server. For
Cursor, use its MCP connection settings. Reuse an existing AdsAgent connector;
installing skills alone does not prove its tools are available in this chat.

For other manual clients, use the dashboard-generated install prompt when
available for that account:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

If MCP Access is unavailable, use the hosted OAuth URLs below or
[AdsAgent connection help](https://adsagent.md/connect); do not send an ordinary
account to restricted Settings. Never invent local relays, stdio setup, URLs,
or credentials. The docs-only Glama MCP cannot access advertising accounts.

## Hosted Endpoints

| Channel | URL |
| --- | --- |
| Meta default | `https://adsagent.md/mcp/v2` |
| Meta legacy fallback | `https://adsagent.md/mcp` |
| Google Ads | `https://google.adsagent.md/mcp` |
| TikTok | `https://tiktok.adsagent.md/mcp` |

Use the Meta v2 product profile for new connections. Keep `/mcp` as the legacy
product-profile fallback. These endpoint names are not MCP protocol versions.

## Protocol Negotiation

Keep the existing hosted endpoint and bearer. Let the MCP client negotiate a
supported protocol revision:

- modern `2026-07-28`: stateless `server/discover`;
- supported legacy revisions: `initialize` with legacy session recovery.

Do not synthesize `MCP-Protocol-Version` or `Mcp-Session-Id`. A protocol or
guide update alone never requires MCP re-registration, bearer replacement,
customer-permission changes, or a Skill Pack reinstall. A transport reconnect
means close and reopen the existing connection, then re-list tools; it is not a
new registration.

## Setup Flow

1. Identify the requested channel from the task. If unknown, ask once whether
   the user wants Meta, Google Ads, or TikTok. Preserve any supplied account,
   dates, and goal. Connect only the requested channels; another disconnected
   channel does not block this one.
2. Reuse the installed plugin or connector. If the selected server's tools
   are absent, show the matching client connection step above. Do not call a
   nonexistent tool or install a second copy of an already configured server.
3. After connecting, re-list that server's tools. When
   `mcp.guide_version` changes, repeat this step before using cached schemas;
   do not re-register or replace the bearer solely for that change.
4. Use the installed skill and its local references for workflow instructions. Discover only the relevant live tool schemas and structured capabilities. Do not fetch `adsagent://guide/brief`, `adsagent://guide/catalog/<domain>`, or `adsagent://guide/tools` to load behavioral instructions. Historical `adsagent://guide/creation-contract` names identify schema topics, not an instruction source.
5. Run the selected server's `setup_get_status` once when readiness is unknown,
   the user requests a check, or a relevant step has changed state. Reuse a
   current result; a new chat or an unrelated question alone needs no setup
   call. Resolve duplicate tool names through their MCP server namespace.
6. Inspect `setup_get_status.capabilities`; use optional consistency, delivery mutation, verification, recovery, and `mutation_lifecycle` only when advertised. When `mutation_lifecycle` is present, prefer `operations_confirm_approval` with `approval_ref` and `expected_plan_digest` over legacy `confirm_token` tools.
7. Inspect top-level `client_skill_pack` once. Its `reminder_mode=notify_only` policy is not a capability or command.
8. Follow the smallest returned setup action needed for the original task.
   Readiness for reporting and readiness for creation are separate. Never
   infer either from screenshots, a central login, or another channel's status.

| Observed state | Next step |
| --- | --- |
| MCP server missing or awaiting OAuth | Connect/authenticate that server in the client; platform connect tools are not available yet. |
| MCP works, platform connection missing | Use the channel flow below and show one returned authorization link. |
| Human authorization pending | Wait for the user; do not poll or generate another link. |
| Authorization completed, assets/history syncing | Keep the returned connection/task reference and report what is still loading; do not restart OAuth or report empty data as zero spend. |
| Required account or permission missing | Show the returned account-specific blocker and human action; do not grant permissions or select a similarly named account. |
| Requested workflow ready | Resume the original task using its channel skill. For setup-only requests, report readiness and stop. |

Use one short status sentence plus one clickable action in the user's language.
For example: "Google MCP is connected. Your Google Ads account still needs
authorization: [Connect Google Ads](<returned authorize_url>). Tell me when
you have finished; I will continue your campaign report." Substitute the exact
returned URL; never assemble an OAuth URL or ask for an authorization code.

## Update Reminder

Read the installed version from the package root `VERSION` file. If the file, policy, or version is missing or invalid, continue silently. When packaged `scripts/update_reminder.py` is available, pass only its four scalar version/interval flags; never pass raw setup data. Follow its bounded result:

- `up_to_date` or `unknown`: continue silently.
- `update_available` plus `should_remind=true`: show one soft reminder, then continue.
- `below_minimum` plus `should_remind=true`: warn that advanced guidance may be incompatible, but keep MCP available.

No automatic update occurs. Show only the matching local instruction:

```text
Claude: claude plugin update --scope user adsagent@adsagent
Codex: codex plugin marketplace upgrade adsagent; Git fallback: git -C ~/.codex/skills/adsagent-ai-skills pull --ff-only
Manual/unknown: open https://github.com/adsagents/adsagent-ai-skills and repeat the original install method.
```

After an update, tell the user to start a fresh session.

## Platform Authorization

MCP OAuth signs the client into AdsAgent. Provider authorization links Facebook,
Google Ads, or TikTok assets to that AdsAgent account. Completing one does not
complete the other. Use the same AdsAgent login on the website and in the MCP
client; opening a website link does not switch the plugin's account.

| Channel to authorize | Owning MCP server and flow |
| --- | --- |
| Meta | On Meta, use `setup_begin_channel_connect(channel=meta)`, then `setup_check_channel_connect` with the same channel and returned `connect_id`. |
| Google Ads | If Meta is already available under the same AdsAgent account, its unified pair accepts `channel=google_ads`. The Google server currently advertises neither begin/check tool. Without Meta, use [Google Ads Settings](https://google.adsagent.md/dashboard/settings) -> Account -> Connect Google Ads account; do not require a Meta advertising account. Verify completion on Google with `setup_get_status`. |
| TikTok | Prefer TikTok's own unified pair with `channel=tiktok`; that server accepts only TikTok. Meta's pair is an alternative when it created the link. Keep begin and check on the same server. |

Use these tools only when present in the live catalog. For older Meta catalogs,
`setup_begin_facebook_connect` / `setup_check_facebook_connect` or
`connections_create_intent(channel=...)` / `connections_check_intent` are
compatibility paths; use the exact handle field from that tool's schema.
Never call Meta's cross-channel tools on Google or send `channel=google_ads`
to TikTok.

Create one link for the requested connect/renewal, display `authorize_url`
(legacy `connect_url`) unchanged, and retain its `connect_id` on the originating
server. Wait until the human confirms completion, then check that exact handle
once. Do not poll OAuth automatically, select the latest session, or mint
another link while one is pending. An expired/failed link needs its returned
remediation before a fresh attempt. Never collect passwords, cookies, OAuth
codes, or bearer tokens in chat.

After the check, read the requested channel's setup state and discover only
the scope needed for the original task:

- **Meta:** a returned binding/asset-refresh task may still be running. Follow
  its `task_ref` and delay through the packaged reliability contract; do not
  restart the connect flow or asset pull. Report observed refresh coverage,
  failed connections, and pending history separately. A bounded asset sample
  or completed task alone is not complete coverage or launch permission. Keep
  an existing connection's label on renewal; ask for one only when
  `connection.needs_label=true`. For reporting, discover products/accounts
  only as needed; do not create templates to complete a read-only setup.
- **Google Ads:** inspect `overall.ready` and `oauth.connected`, then use
  `google_ads_accounts_list` for an enabled non-manager customer. Preserve
  its login-customer route. An MCC or OAuth success alone is not a spend scope.
- **TikTok:** distinguish connection, advertiser sync, and templates.
  `overall.ready` can describe QuickCreate readiness; a template-only blocker
  does not require another OAuth flow or template creation for an Insights
  read. Use the advertised account discovery for the requested advertiser and
  keep missing history unknown.

The same AdsAgent login can authorize each server, but new OAuth credentials
are resource-bound. Let the client obtain credentials for each exact hosted
URL; never copy a bearer from Meta into Google or TikTok. Existing supported
legacy bearer connections are compatibility-only, not new setup instructions.
Missing central-auth identity requires the client's OAuth or the supported
dashboard path. Do not use email fallback, guessed email, manually entered
identity, passwords, cookies, or authorization codes.

## Safety

- Never print/store bearer tokens in notes, logs, generated docs, or chat.
- Never enable or modify customer permissions automatically. For Meta delivery access, follow `capabilities.delivery_mutations.permission_action`: `reauthorize_with_scope` uses client OAuth, `enable_in_dashboard` uses the returned settings link, and `contact_support` uses official support. Full Settings is not available to every account; use `website_links.settings` and its label when returned.
- Follow returned authorization links and status actions; do not scrape the dashboard.
- Use public handles only.
- On `operator_review_required`, stop and ask the AdsAgent operator to inspect internal diagnostics.
