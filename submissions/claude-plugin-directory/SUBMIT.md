# Claude Plugin Directory Submission

Portal: https://claude.ai/directory/manage/new

Choose **Bundle** (GitHub-hosted skills and MCP connections).
**Connector only** submits one remote MCP separately.

## Pre-submit

```bash
claude plugin validate .
python3 scripts/validate_tri_channel_pack.py
python3 -m pytest -q
```

## Copy-paste reference

| Field | Value |
|---|---|
| Repository | `adsagents/adsagent-ai-skills` |
| Plugin slug | `adsagent` |
| Display name | `AdsAgent` |
| Version | See root `VERSION` (currently `0.7.75`) |
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
  installer credential and is not an MCP server or plugin hook. No API-key
  `userConfig` option is needed for this OAuth plugin. If this flag persists,
  request review of the actual source and destination rather than adding an
  unused credential field.
- `UNREAD_ASSET_REFERENCED`: `assets/logo.png` is the 192 x 192 PNG referenced by
  `.cursor-plugin/plugin.json` for display. The Python validator checks only
  its existence; the release test checks only the manifest's path string.
  No bundled command executes it. Retain the logo and request the image review
  allowed by the submission guidance; an automated hold can remain until that
  review completes. The printable-text screening notice is informational.
