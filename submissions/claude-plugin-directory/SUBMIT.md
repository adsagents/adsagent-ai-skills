# Claude Plugin Directory Submission

Portal: https://claude.ai/admin-settings/directory/submissions/plugins/new

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
| Version | See root `VERSION` (currently `0.7.66`) |
| Homepage | `https://adsagent.md`（**单行 URL，前后不能有空格**；文档站放 description，不要拼两个 URL） |
| Documentation (in description copy) | `https://adsagent.md/skills` |
| Support email | `support@adsagent.md` |
| Publisher | adsagents LLC |

## Short description

AdsAgent tri-channel Claude plugin: hosted OAuth MCP for Meta, Google Ads, and TikTok plus behavior skills for bounded reads and safer prepare/confirm ad workflows.

## Portal pitfalls

- **`plugin_homepage`**: Anthropic API rejects spaces/control characters. Use exactly `https://adsagent.md` with no leading/trailing spaces. Do not paste two URLs, markdown links, or display names into this field.

- Root `.mcp.json` declares HTTP MCP URLs only (no `Authorization` header).
- License includes a narrow Anthropic community marketplace mirroring exception (`LICENSE.md`).
- This is separate from Connectors Directory MCP server registration on `adsagent.md`.

## Does not affect

OpenAI ChatGPT app submission artifacts in the Meta service repo.
