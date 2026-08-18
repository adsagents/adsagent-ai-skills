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
| Version | See root `VERSION` (currently `0.7.64`) |
| Homepage | `https://adsagent.md` |
| Documentation | `https://adsagent.md/skills` |
| Support email | `support@adsagent.md` |
| Publisher | adsagents LLC |

## Short description

AdsAgent tri-channel Claude plugin: hosted OAuth MCP for Meta, Google Ads, and TikTok plus behavior skills for bounded reads and safer prepare/confirm ad workflows.

## Notes

- Root `.mcp.json` declares HTTP MCP URLs only (no `Authorization` header).
- License includes a narrow Anthropic community marketplace mirroring exception (`LICENSE.md`).
- This is separate from Connectors Directory MCP server registration on `adsagent.md`.

## Does not affect

OpenAI ChatGPT app submission artifacts in the Meta service repo.
