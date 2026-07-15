# AdsAgent Tri-Channel AI Skills

Public skill pack for using AdsAgent tri-channel hosted MCP with AI agents: Meta, Google Ads, and TikTok.

**Official distribution:** [github.com/adsagents/adsagent-ai-skills](https://github.com/adsagents/adsagent-ai-skills)

**Website:** [adsagent.md](https://adsagent.md)
**Support:** [support@adsagent.md](mailto:support@adsagent.md)

Current contract version: `0.7.14`. New Meta connections default to the stateless v2 endpoint; legacy clients remain supported.

AdsAgent helps operators analyze ad performance across Meta, Google Ads, and TikTok, compare safe platform state where supported, and prepare safer ad workflows. This repository teaches AI agents how to use AdsAgent responsibly without exposing internal tool catalogs, payload schemas, validation internals, or backend implementation details.

The operating model is B2B and resource-aware:

- answer operators in Markdown,
- fetch only the data needed for the user's question,
- prefer cleaned and aggregated reads,
- do not read raw rows in normal agent conversations,
- summarize before expanding,
- preserve server stability by respecting AdsAgent MCP retry and concurrency contracts.

Version 0.7.4 adds `agent-scheduled-tasks`, which teaches agents to distinguish reminder-only jobs from auditable execution, create deterministic schedules, read them back, run them once, and report execution proof honestly. It does not add an AdsAgent-hosted scheduler or bypass platform capabilities. Agents reuse top-level `client_skill_pack` from `setup_get_status`; they never run a separate version poll or automatic update.

Version 0.7.5 makes Meta partnership-copy behavior explicit: partnership and boosted-post ads use deep copy, unsupported fresh mode stops before approval, and cross-account eligibility failures are never retried automatically.

Version 0.7.6 keeps Meta candidate selection server-side with bounded pages, spend thresholds, deterministic name deduplication, and self-correctable public query validation.

Version 0.7.7 keeps Meta filtering server-side while making exhaustive Ad reads lossless: agents retain every `ad_id`, paginate serially with an unchanged filter, and aggregate duplicate Ad names only after all requested pages arrive.

Version 0.7.8 teaches agents to preserve an opaque MCP `support_ref` for unresolved error handoff without exposing tokens or raw payloads. It also separates Meta `scope_unavailable` from Meta creation permission.

Version 0.7.9 makes completed Meta consistency tasks terminal evidence: agents consume the bounded task result directly instead of querying page 1 again, and later pages use a fixed source watermark through `min_as_of` so a long read stays on one snapshot.

Version 0.7.10 adds safe grouped Meta copy guidance: one seed per target Campaign, remaining distinct Ads appended only after the target AdSet exists, explicit country or worldwide-minus-country targeting frozen in approvals, and a hard stop when the requested settings reference is missing.

Version 0.7.11 adds bounded Meta structured filtering across hierarchy names and IDs, performance metrics, configured/effective delivery status, budgets, objectives, events, Pixel, and App metadata. Conditions are server-side AND filters; exact Ad-name deduplication, language classification, and business grouping remain client responsibilities, while large exhaustive results use a grouped export artifact.

Version 0.7.12 routes multiple distinct Meta source Ads through one server-owned `grouped_plan` prepare. Agents verify the explicit settings-source order, geography, budget, bid, and paused-by-default structure in one approval, then consume the returned single-use confirmation token exactly once. Existing single-Ad, structure-clone, and recreate workflows remain compatible.

Version 0.7.13 corrects Meta scope recovery: `scope_unavailable` alone does not prove another workspace/token. Agents run bounded setup and matching discovery once, retry the identical read once only when the scope remains listed, then preserve `support_ref` for operator review without changing customer permissions.

Version 0.7.14 aligns Meta creation with the hosted v2 contract: canonical single/grouped copy examples, path-scoped legacy compatibility, typed QuickCreate launch fields, and one safe prepare-only correction for public `invalid_fields`. Confirm/write calls remain approval-gated and are never retried automatically.

The local helper `scripts/update_reminder.py` compares strict semantic versions and stores only bounded version/timestamp state in `$XDG_CACHE_HOME/adsagent-ai-skills/update-reminder-v1.json` (or `~/.cache/...`). Cache failure never blocks MCP work.

## What This Is

- A public, semi-black-box skill pack for AdsAgent tri-channel users.
- A behavior guide for Claude Code, Cursor, Grok-style agents, and other MCP-aware clients.
- A reliability and safety layer that tells agents when to retry, when to wait, and when to stop.
- A versioned GitHub distribution for AdsAgent user onboarding and agent behavior guidance.
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
| `agent-scheduled-tasks` | Design, create, verify, update, pause, and delete agent-owned scheduled tasks without confusing reminders with execution proof. |
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

## Installation

This repo is designed to be installed as a skill/plugin bundle in clients that support GitHub-hosted skills. The exact command depends on the client.

For Claude Code plugin flows:

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

### Codex CLI

Current Codex CLI versions can install the same marketplace directly:

```bash
codex plugin marketplace add adsagents/adsagent-ai-skills
codex plugin add adsagent-ai-skills@adsagent-ai-skills
```

Refresh a Codex marketplace install with:

```bash
codex plugin marketplace upgrade adsagent-ai-skills
```

Start a fresh Codex session after installing or upgrading.

### Git fallback and other Agent-Skills-compatible clients

The skills in `skills/` use the standard Agent Skills layout
(`skills/<name>/SKILL.md` with YAML frontmatter), so any client that consumes
that format (Codex CLI, Copilot CLI, Gemini CLI, etc.) can use them without a
plugin marketplace. Install by cloning into the client's skills directory:

```bash
git clone https://github.com/adsagents/adsagent-ai-skills.git ~/.codex/skills/adsagent-ai-skills
```

(or copy the directories under `skills/` into your project-level skills
folder, e.g. `.codex/skills/`). A Git checkout updates with
`git -C ~/.codex/skills/adsagent-ai-skills pull --ff-only`; manually copied
installs must repeat their original install method. Skill names and
trigger descriptions are client-neutral; invoke them by skill name in the
client's syntax. Start a fresh session after installing or updating.

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
- Honor `mcp_fanout_detected` by switching to the platform batch overview tool instead of retrying the blocked single-scope request.
- When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, use one `insights_query_consistent` request with `scope` or ordered `scopes` for all three platforms.
- Without that profile, use native server-side batch tools for multi-scope reads: Meta/TikTok `insights_query_batch_overview`, Google `google_ads_insights_overview_batch`.
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
