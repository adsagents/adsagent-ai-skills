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

For clients without plugin support, the dashboard-generated install prompt is
authoritative for MCP URLs and bearer/OAuth flow:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

Do not invent local relays, stdio setup, URLs, or credentials.

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

1. **Plugin path:** install `adsagent@adsagent`, authenticate each MCP server in `/mcp`.
2. **Non-plugin path:** use dashboard install prompt, then reconnect transport.
3. Reconnect the existing transport and re-list tools. When
   `mcp.guide_version` changes, repeat this step before using cached schemas;
   do not re-register or replace the bearer solely for that change.
4. Read `adsagent://guide/brief`, then one bounded `adsagent://guide/catalog/<domain>` topic if needed. Read `adsagent://guide/creation-contract` only for Meta creation/copy work. Never read `adsagent://guide/tools` end-to-end.
5. Run `setup_get_status`; report readiness, blockers, and next action.
6. Inspect `setup_get_status.capabilities`; use optional consistency, delivery mutation, verification, recovery, and `mutation_lifecycle` only when advertised. When `mutation_lifecycle` is present, prefer `operations_confirm_approval` with `approval_ref` and `expected_plan_digest` over legacy `confirm_token` tools.
7. Inspect top-level `client_skill_pack` once. Its `reminder_mode=notify_only` policy is not a capability or command.
8. Never infer readiness from screenshots or a central token alone.

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

- Meta uses the begin/check Facebook-connect flow exposed by Meta MCP; the human opens the returned URL.
- For Google Ads/TikTok, call `connections_create_intent(channel=...)`, let the human complete the single-use browser flow, then poll its check tool.
- The same AdsAgent bearer / OAuth identity can route across servers when issued by central auth, but each platform authorization is independent.
- Missing central-auth identity requires a fresh dashboard prompt or OAuth. Do not use email fallback, guessed email, manually entered identity, passwords, cookies, or authorization codes.

## Safety

- Never print/store bearer tokens in notes, logs, generated docs, or chat.
- Never enable or modify customer permissions automatically. For Meta delivery access, follow `capabilities.delivery_mutations.permission_action`; dashboard-token users act at `/dashboard/settings#mcp-access`, while OAuth users reconnect with the advertised scope.
- Follow returned authorization links and status actions; do not scrape the dashboard.
- Use public handles only.
- On `operator_review_required`, stop and ask the AdsAgent operator to inspect internal diagnostics.
