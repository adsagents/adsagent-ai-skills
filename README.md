# AdsAgent Tri-Channel Plugin

Public Claude plugin + skill pack for AdsAgent tri-channel hosted MCP: Meta, Google Ads, and TikTok.

**Distribution split (important):**

| Surface | What it is | This repo? |
| --- | --- | --- |
| **Claude plugin** (self-hosted marketplace) | Skills + root `.mcp.json` HTTP MCP URLs (OAuth) | Yes |
| **Anthropic Connectors Directory** | Hosted MCP server listing only | No — separate submission on `adsagent.md` services |

**Official GitHub repo:** [github.com/adsagents/adsagent-ai-skills](https://github.com/adsagents/adsagent-ai-skills)

**Website:** [adsagent.md](https://adsagent.md?utm_source=github&utm_medium=readme&utm_campaign=adsagent-ai-skills)  
**Official links hub:** [adsagent.md/connect](https://adsagent.md/connect?utm_source=github&utm_medium=readme&utm_campaign=adsagent-ai-skills)  
**Skill pack landing page:** [adsagent.md/skills](https://adsagent.md/skills?utm_source=github&utm_medium=readme&utm_campaign=adsagent-ai-skills)  
**Support:** [support@adsagent.md](mailto:support@adsagent.md)

Current contract version: `0.7.63`. The plugin slug is `adsagent` (marketplace key `adsagent`).
New Meta connections default to the v2 product profile; all three hosted endpoints
negotiate modern MCP `2026-07-28` stateless discovery while retaining supported
legacy initialize clients.


Version history lives in [CHANGELOG.md](CHANGELOG.md).

The local helper `scripts/update_reminder.py` compares strict semantic versions and stores only bounded version/timestamp state in `$XDG_CACHE_HOME/adsagent-ai-skills/update-reminder-v1.json` (or `~/.cache/...`). Cache failure never blocks MCP work.

## What This Is

- A public Claude plugin marketplace package: **behavior skills** plus **hosted MCP URLs** via `.mcp.json`.
- A behavior guide for Claude Code, Cursor, Codex, and other MCP-aware clients.
- A reliability and safety layer that tells agents when to retry, when to wait, and when to stop.
- A versioned GitHub distribution for AdsAgent user onboarding and agent behavior guidance.
- A data-minimization contract for AI agents that should not scan AdsAgent like a raw database.

## What This Is Not

- Not the Anthropic Connectors Directory MCP listing (that is registered separately on the hosted servers).
- Not a complete MCP tool reference.
- Not an SDK.
- Not a local transport relay.
- Not a disclosure of AdsAgent backend routes, schemas, database tables, or internal diagnostics.

For Claude Code plugin installs, OAuth MCP setup comes from this repo's `.mcp.json`.
For clients without plugin support, the AdsAgent dashboard install prompt remains
the manual fallback:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

Use that copied prompt only when you are not installing the Claude plugin bundle.
This repository teaches agent behavior after the MCP connection exists.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `adsagent-router` | Route AdsAgent requests to setup, reliability, insights, or copy workflows. |
| `adsagent-setup` | Connect through the AdsAgent dashboard install prompt and verify Meta, Google Ads, or TikTok readiness. |
| `adsagent-notifications` | Inspect and safely configure notification channels and Meta Ads Webhooks. |
| `adsagent-reliability` | Respect retry, backoff, session refresh, and concurrency limits. |
| `agent-scheduled-tasks` | Design, create, verify, update, pause, and delete agent-owned scheduled tasks without confusing reminders with execution proof. |
| `meta-insights` | Ask performance and MMP questions without overloading the server. |
| `meta-copy` | Copy or compare Meta ads with confirmation and operator-review safety. |
| `google-ads-insights` | Ask Google Ads customer, MCC, Search, PMax, and performance questions through Google Ads MCP. |
| `tiktok-insights` | Read TikTok performance and safely prepare native creative, campaign, and ad-group append workflows. |

## Progressive Disclosure

Agent clients load every Skill description for discovery, but should load only
the selected `SKILL.md` body. Each entrypoint is intentionally small and links
to local reference files that are read only when the selected workflow needs
those details.

The files under `docs/` are human-facing product and operator documentation.
They are not automatic agent context and are not part of Skill reference
traversal. Agent behavior contracts live under `skills/` and are reached from
the selected `SKILL.md`.

## Agent Output Contract

Agents using AdsAgent should answer in Markdown by default:

```markdown
## Answer
One-sentence answer.

## Scope
- Date:
- Entity:
- Grouping:
- Attribution / channel:

## Results
| Metric | Value |
| --- | ---: |

## Notes
- Data freshness:
- Limits or missing fields:
- Next safe action:
```

Do not dump JSON, CSV, hidden diagnostics, raw rows, or every returned field into chat. Clean the response into operator-facing tables and short bullets. If forensic raw inspection is needed, create an operator handoff instead of making raw rows the agent answer.

## Semi-Black-Box Policy

This repository intentionally documents outcomes and agent behavior, not the complete internal interface. Agents should:

- Read the live AdsAgent MCP guide after connecting.
- Use available tools through the authenticated MCP session.
- Avoid guessing hidden payload fields.
- Avoid probing rejected requests.
- Stop on operator-review responses and ask the AdsAgent operator to inspect internal diagnostics.
- Use the smallest safe data plan before making calls.
- Prefer grouped summaries and cleaned breakdowns over raw rows.

The external agent contract is: ask clear questions, respect limits, confirm before writes, and use dashboard-provided onboarding.

## Official Source And Rights

This repository contains only the client-readable behavior pack. AdsAgent server source, credentials, schemas, routing logic, and operational diagnostics are not distributed here.

The package is proprietary and all rights are reserved by adsagents LLC. Public GitHub hosting allows people to view and fork the repository under GitHub's Terms of Service, but a fork or local copy does not grant any additional intellectual-property license. No permission is granted to redistribute, mirror, sell, sublicense, publish modified versions, create derivative works, train a competing product from the pack, or represent a fork as official. See [LICENSE.md](LICENSE.md) and [NOTICE.md](NOTICE.md).

## Example Prompts

```text
Use AdsAgent to list my connected Meta products, Google Ads customers, or TikTok advertisers, then ask which scope's today data I want to inspect.
```

```text
For Google Ads, inspect agent_method_profile, pick an enabled non-manager customer, and use one cached insights_query_consistent request when the profile is advertised.
```

```text
For TikTok, inspect agent_method_profile and use one insights_query_consistent scopes request when advertised; otherwise use the native batch overview fallback.
```

```text
Prepare a copy of this winning Meta ad into the target account, but ask me for confirmation before creating anything.
```

```text
Group these distinct Meta Ads by language into the requested Campaign and AdSet layout. Prepare one grouped_plan, show every settings_source_ad_id and geography override, and wait for my approval before confirming once.
```

More examples are in [docs/examples.md](docs/examples.md).

## Validation

Run the local release contract and tests:

```bash
python scripts/validate_tri_channel_pack.py
python -m pytest -q
```

Release validation is fail-closed against the three committed snapshots in
`contracts/manifests/`. Each snapshot is copied byte-for-byte from a committed
service artifact and locked to its channel, source revision, public artifact
path, metadata, and SHA-256 in `contracts/manifests/provenance.json`. CI does
not make live network requests.

```bash
python scripts/validate_public_tool_manifests.py
```

An operator can deterministically update all three snapshots after the service
manifest changes. The command rejects uncommitted, dirty, missing, or
contract-incompatible sources and never fetches from the network:

```bash
python scripts/sync_public_tool_manifests.py \
  --source meta=/path/to/meta-tools.json \
  --source google=/path/to/google-tools.json \
  --source tiktok=/path/to/tiktok-tools.json
```

All three sources are mandatory. A missing referenced tool, an unproven
required capability or gate, a stale provenance digest, or an absent channel
fails release validation. `--allow-missing` exists only for explicit local
diagnostics and is not used by release CI.

## Installation

This repo ships as the **`adsagent` Claude plugin** (skills + `.mcp.json` MCP URLs).
The GitHub repository name stays `adsagent-ai-skills`.

### Claude Code (recommended)

```bash
claude plugin marketplace add adsagents/adsagent-ai-skills
claude plugin install adsagent@adsagent
```

Update an existing user-scope install:

```bash
claude plugin update --scope user adsagent@adsagent
```

If `claude plugin list` shows duplicate local and user installs, keep user scope:

```bash
claude plugin uninstall --scope local adsagent@adsagent
```

Start a fresh Claude Code session after installing or updating.

### Cloud / Cowork preinstall (settings snippet)

```json
{
  "extraKnownMarketplaces": {
    "adsagent": {
      "source": {
        "source": "github",
        "repo": "adsagents/adsagent-ai-skills"
      }
    }
  },
  "enabledPlugins": ["adsagent@adsagent"]
}
```

After install, authenticate each MCP server shown in `/mcp` (Meta, Google, TikTok).
Do not add `headers.Authorization` to `.mcp.json`; OAuth must remain the auth path.

### Migrating from legacy plugin slugs

Older installs used `adsagent-ai-skills@adsagent-ai-skills` or
`adsagent-meta-ai-skills@adsagent-meta-ai-skills`. The marketplace declares a
rename to `adsagent@adsagent`. After migrating, remove legacy duplicates:

```bash
claude plugin uninstall --scope user adsagent-ai-skills@adsagent-ai-skills
claude plugin uninstall --scope user adsagent-meta-ai-skills@adsagent-meta-ai-skills
```

### Codex CLI

```bash
codex plugin marketplace add adsagents/adsagent-ai-skills
codex plugin add adsagent@adsagent
```

Refresh:

```bash
codex plugin marketplace upgrade adsagent
```

Start a fresh Codex session after installing or upgrading.

### Git fallback and other Agent-Skills-compatible clients

The skills in `skills/` use the standard Agent Skills layout
(`skills/<name>/SKILL.md` with YAML frontmatter). Clients that only consume skills
(without the plugin MCP bundle) can clone manually:

```bash
git clone https://github.com/adsagents/adsagent-ai-skills.git ~/.codex/skills/adsagent-ai-skills
```

Those clients still need a separate MCP connection (dashboard install prompt or
Connectors Directory). The plugin path is the one-step skills + MCP bundle.

Then open AdsAgent only if you need dashboard OAuth/token setup for non-plugin clients:

```text
Settings -> MCP Access -> Copy install prompt
```

Paste the copied prompt into a fresh chat when the plugin bundle is not used.
The prompt provides hosted HTTP MCP URLs for:

```text
Meta default: https://adsagent.md/mcp/v2
Meta legacy fallback: https://adsagent.md/mcp
Google Ads: https://google.adsagent.md/mcp
TikTok: https://tiktok.adsagent.md/mcp
```

## Important Runtime Rules

- Hosted HTTP MCP only.
- Use `https://adsagent.md/mcp/v2` for new Meta connections; `/mcp` is the legacy fallback.
- Do not run AdsAgent MCP code locally.
- Do not use a local relay unless the AdsAgent dashboard explicitly says to.
- Cache connection setup where the client supports it.
- Keep per-token MCP concurrency bounded.
- Respect `Retry-After`.
- Parse `Retry-After` from the HTTP header, top-level `data`, or JSON-RPC `error.data`.
- Honor `mcp_concurrency_limited` with wait plus jitter.
- Honor `mcp_fanout_detected` by switching to the platform batch overview tool instead of retrying the blocked single-scope request.
- When `agent_method_profile.profile_id=adsagent_agent_methods_v1` and its consistent read is present in the client-local catalog, use one `insights_query_consistent` request with `scope` or ordered `scopes` for all three platforms.
- Without that profile, or when its advertised read is missing only from the client-local catalog, use the profile's named native fallback or the documented server-side tools: Meta/TikTok `insights_query_batch_overview`, Google `google_ads_insights_overview_batch`. Do not report a server registration failure from a local selector miss.
- Query aggregated data first and never infer cross-platform capability parity from a shared tool name.
- Report server-computed totals from the response; do not sum currently visible rows.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- Poll queued tasks to `terminal=true` and return the artifact link instead of raw CSV.
- Poll queued work directly with `tasks_get_status(task_ref=...)` when the server advertises direct task refs.
- QuickCreate confirm tokens are single-use and expire after 15 minutes. Check `expires_at`; after `confirm_token_invalid`, prepare again, show the new summary, and obtain fresh explicit approval.
- Poll Meta creation tasks with `tasks_get_status(task_ref=..., response_mode=compact)`. On `no_create_permission`, direct the user to `/dashboard/assets/fb-users`; never change customer permissions or replay the failed creation automatically.
- Avoid raw-row reads in normal user conversations.
- Use Markdown tables for numbers.
- Confirm before ad creation or modification.
- Use `grouped_plan` for multiple distinct source Ads; never emulate it through a client-side series of copy mutations.
- Stop on operator-review errors.
- When an error includes `support_ref`, preserve and show it verbatim for support. It is not authorization; never invent, modify, enumerate, or replace it with tokens, request bodies, or logs.

## Links

- Official website: https://adsagent.md
- Official repository: https://github.com/adsagents/adsagent-ai-skills
- Support: support@adsagent.md
- Public onboarding path: https://adsagent.md/docs/mcp-onboarding

## License

All rights reserved. See [LICENSE.md](LICENSE.md).
