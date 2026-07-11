# AdsAgent Tri-Channel AI Skills

Private skill pack for using AdsAgent tri-channel hosted MCP with AI agents: Meta, Google Ads, and TikTok.

Current contract version: `0.6.2`. New Meta connections default to the stateless v2 endpoint; legacy clients remain supported.

AdsAgent helps operators analyze ad performance across Meta, Google Ads, and TikTok, compare safe platform state where supported, and prepare safer ad workflows. This repository teaches AI agents how to use AdsAgent responsibly without exposing internal tool catalogs, payload schemas, validation internals, or backend implementation details.

The operating model is B2B and resource-aware:

- answer operators in Markdown,
- fetch only the data needed for the user's question,
- prefer cleaned and aggregated reads,
- do not read raw rows in normal agent conversations,
- summarize before expanding,
- preserve server stability by respecting AdsAgent MCP retry and concurrency contracts.

## What This Is

- A private, semi-black-box skill pack for AdsAgent tri-channel users.
- A behavior guide for Claude Code, Cursor, Grok-style agents, and other MCP-aware clients.
- A reliability and safety layer that tells agents when to retry, when to wait, and when to stop.
- A private GitHub staging repo for AdsAgent demos, Product Hunt copy, and user onboarding context.
- A data-minimization contract for AI agents that should not scan AdsAgent like a raw database.

## What This Is Not

- Not the source of truth for MCP installation.
- Not a complete MCP tool reference.
- Not an SDK.
- Not a local transport relay.
- Not a disclosure of AdsAgent backend routes, schemas, database tables, or internal diagnostics.

The authoritative setup flow lives inside the AdsAgent dashboard:

```text
AdsAgent dashboard -> Settings -> MCP Access -> Copy install prompt
```

Use that copied prompt to install or refresh the hosted HTTP MCP connection. This repository only teaches the agent how to behave after the connection exists.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `adsagent-router` | Route AdsAgent requests to setup, reliability, insights, or copy workflows. |
| `adsagent-setup` | Connect through the AdsAgent dashboard install prompt and verify Meta, Google Ads, or TikTok readiness. |
| `adsagent-reliability` | Respect retry, backoff, session refresh, and concurrency limits. |
| `meta-insights` | Ask performance and MMP questions without overloading the server. |
| `meta-copy` | Copy or compare Meta ads with confirmation and operator-review safety. |
| `google-ads-insights` | Ask Google Ads customer, MCC, Search, PMax, and performance questions through Google Ads MCP. |
| `tiktok-insights` | Ask TikTok advertiser, tenant, campaign, ad group, and ad performance questions through TikTok MCP. |

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

## Example Prompts

```text
Use AdsAgent to list my connected Meta products, Google Ads customers, or TikTok advertisers, then ask which scope's today data I want to inspect.
```

```text
For Google Ads, use google_ads_accounts_list, pick an enabled non-manager customer, and summarize yesterday's campaign spend.
```

```text
For TikTok, use insights_query_batch_overview for these advertisers and report server summary/total instead of summing visible rows.
```

```text
Prepare a copy of this winning Meta ad into the target account, but ask me for confirmation before creating anything.
```

More examples are in [docs/examples.md](docs/examples.md).

## Installation

This repo is designed to be installed as a skill/plugin bundle in clients that support GitHub-hosted skills. The exact command depends on the client.

For Claude Code-style plugin flows after publishing to GitHub:

```bash
claude plugin marketplace add adsagents/adsagent-ai-skills
claude plugin install adsagent-ai-skills@adsagent-ai-skills
```

If Claude Code already has an older install, update the user-scope plugin:

```bash
claude plugin update --scope user adsagent-ai-skills@adsagent-ai-skills
```

If `claude plugin list` shows this plugin in both local and user scope, keep the user-scope install and remove the duplicate local-scope install from the project where that local install is registered:

```bash
claude plugin uninstall --scope local adsagent-ai-skills@adsagent-ai-skills
```

Start a fresh Claude Code session after installing or updating. Skill changes are not reliable inside an already-open session.

### Migrating from the legacy package name

Older installs used `adsagent-meta-ai-skills`. That package remains available
as a compatibility alias, but new installs should use `adsagent-ai-skills`.
If both packages are installed, keep `adsagent-ai-skills` and remove the legacy
package to avoid duplicate skill names:

```bash
claude plugin uninstall --scope user adsagent-meta-ai-skills@adsagent-meta-ai-skills
```

### Codex CLI and other Agent-Skills-compatible clients

The skills in `skills/` use the standard Agent Skills layout
(`skills/<name>/SKILL.md` with YAML frontmatter), so any client that consumes
that format (Codex CLI, Copilot CLI, Gemini CLI, etc.) can use them without a
Claude Code plugin flow. Install by cloning into your client's skills
directory — for Codex CLI:

```bash
git clone git@github.com:adsagents/adsagent-ai-skills.git ~/.codex/skills/adsagent-ai-skills
```

(or copy the directories under `skills/` into your project-level skills
folder, e.g. `.codex/skills/`). Update later with `git pull`. Skill names and
trigger descriptions are client-neutral; invoke them by skill name in
whatever syntax your client uses. Start a fresh session after installing or
updating, same as Claude Code.

For Codex CLI installs that still point at the legacy directory, install the
new package into `~/.codex/skills/adsagent-ai-skills` and remove the old
`~/.codex/skills/adsagent-meta-ai-skills` directory only after the new package
is present.

Then open AdsAgent and use:

```text
Settings -> MCP Access -> Copy install prompt
```

Paste the copied prompt into a fresh chat in your AI client. The prompt provides the hosted HTTP MCP URLs and bearer token flow for:

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
- Use server-side batch tools for multi-scope reads: Meta/TikTok `insights_query_batch_overview`, Google `google_ads_insights_overview_batch`.
- Query aggregated data first.
- For one Meta product/account scope, use `insights_query_overview`; for several scopes, call `insights_query_batch_overview` once instead of client-side fanout.
- Report server-computed totals from the response; do not sum currently visible rows.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- Poll queued tasks to `terminal=true` and return the artifact link instead of raw CSV.
- Avoid raw-row reads in normal user conversations.
- Use Markdown tables for numbers.
- Confirm before ad creation or modification.
- Stop on operator-review errors.

## Links

- Product: https://adsagent.md
- Public onboarding path: https://adsagent.md/docs/mcp-onboarding

## License

All rights reserved. See [LICENSE.md](LICENSE.md).
