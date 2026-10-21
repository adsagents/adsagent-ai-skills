# Claude Plugin Directory Submission

Portal: https://claude.ai/directory/manage/new

Choose **Bundle** (GitHub-hosted skills and MCP connections).
**Connector only** submits one remote MCP separately.

Directory review scans this **whole repository**, not a marketplace `source`
subdirectory. `.claude-plugin/marketplace.json` keeps the plugin name
`adsagent` and sets `"source": "./"`. Skills live only in `skills/`. Claude,
Cursor, Codex, and Glama all read that root.

## Pre-submit

```bash
claude plugin validate . --strict
python3 scripts/validate_tri_channel_pack.py
python3 -m pytest -q
```

## Copy-paste reference

| Field | Value |
|---|---|
| Repository | `adsagents/adsagent-ai-skills` |
| Plugin slug | `adsagent` |
| Display name | `AdsAgent` |
| Version | See root `VERSION` (currently `0.7.87`) |
| Homepage | `https://adsagent.md/connect`（**单行 URL，前后不能有空格**；文档站放 description，不要拼两个 URL） |
| Documentation (in description copy) | `https://adsagent.md/docs/mcp-onboarding` |
| License type | `MIT` (root `LICENSE`) |
| Privacy policy URL | `https://adsagent.md/privacy` |
| Support email | `support@adsagent.md` |
| Publisher | adsagents LLC |

## Short description

AdsAgent tri-channel Claude plugin: hosted OAuth MCP for Meta, Google Ads, and TikTok plus behavior skills for bounded reads and safer prepare/confirm ad workflows.

## Portal pitfalls

- **`plugin_homepage`**: Anthropic API rejects spaces/control characters. Use exactly `https://adsagent.md/connect` with no leading/trailing spaces. Do not paste two URLs, markdown links, or display names into this field.

- Root `.mcp.json` declares HTTP MCP URLs only (no `Authorization` header).
- License is MIT (`LICENSE`).
- This is separate from Connectors Directory MCP server registration on `adsagent.md`.

## Does not affect

OpenAI ChatGPT app submission artifacts in the Meta service repo.

## Automated review notes

- `PRIVACY_URL_MISSING`: `.claude-plugin/plugin.json` now declares
  `privacyPolicyUrl: https://adsagent.md/privacy`, matching the existing README
  and submission policy link.
- `RUNTIME_FETCH_EXEC`: the general `scripts/devbox/cloud-agent-install.sh` has
  been removed. `scripts/cloud-agent-setup.sh` is a bundled, readable setup
  script for contributors' cloud environments. It requires a
  preinstalled `uv` and prepares Python 3.12 and `pytest==9.0.2` through that
  package manager. It no longer downloads shell installers and pipes them into
  a shell. The unused product devbox shims have been removed. Cloud configuration
  calls the new script, and the old devbox sync destination is ignored by Git.
- `MCP_FORWARDS_CREDENTIAL_ENV`: `.mcp.json` and `mcp.json` contain only the three
  AdsAgent HTTP resource URLs. They declare no headers, environment variables,
  credential helpers, or local server commands. Authentication uses the
  client's OAuth flow for each resource. The bundled setup script reads no
  installer credential and is not an MCP server or plugin hook. This repository
  does not read the process environment. Cache location, skill-pack root,
  and manifest paths are arguments. The docs image starts with
  `python -m skill_pack_mcp --root /app`. Child processes for the stdio probe
  receive a fixed literal environment.
  The release-tag check runs in adsagent-ops
  (`bin/check-skillpack-release-tag`), not in this repository. This
  repository does not start git, read a token, or request GitHub.
  No API-key `userConfig` option is needed for this OAuth plugin.
- `UNREAD_ASSET_REFERENCED`: this repository does not ship an image or font
  file. The Cursor manifest logo is an absolute https URL on `adsagent.md`.
- `UNKNOWN_KEY privacyPolicyUrl`: the directory reads `privacyPolicyUrl` from
  `plugin.json`. Keep `https://adsagent.md/privacy`. Do not remove the field to
  clear that notice.
