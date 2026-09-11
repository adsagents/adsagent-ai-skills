# Glama listing for this repository

Glama can Build and Make Release against this repo so the directory can score
Quality. That listing is the **AdsAgent Skill Pack (docs)** MCP, not the
production ads product.

## What a Glama release is

- A stdio MCP process that reads public files from this repository
  (`skills/`, `README.md`, `VERSION`, `mcp.json`).
- A deploy/preview target for Glama Quality scoring (tool-description quality,
  build, and container start).
- Honest directory metadata: the server name is **AdsAgent Skill Pack (docs)**.

It does **not** implement Meta, Google Ads, or TikTok ads tools, insights,
mutations, or OAuth. It does not hold tokens or `.env` credentials.

## What production ads MCP remains

The real ads MCP stays on AdsAgent hosted HTTP endpoints declared in root
`mcp.json` / `.mcp.json`:

| Channel | URL |
| --- | --- |
| Meta | `https://adsagent.md/mcp/v2` |
| Google Ads | `https://google.adsagent.md/mcp` |
| TikTok | `https://tiktok.adsagent.md/mcp` |

Clients must complete AdsAgent OAuth against those hosted services. Installing
or deploying this image is not a substitute for that connection.

## Repository files

| File | Role |
| --- | --- |
| [`glama.json`](../glama.json) | Glama ownership claim. The published schema (`https://glama.ai/mcp/schemas/server.json`) allows only `maintainers`. Name, description, and Docker form fields are set in the Glama admin UI — use **AdsAgent Skill Pack (docs)** and the wording above. |
| [`Dockerfile`](../Dockerfile) | Slim Python image, public files only, non-root `app` user, `CMD ["python", "-m", "skill_pack_mcp"]` on stdio. |
| [`skill_pack_mcp/`](../skill_pack_mcp/) | Stdlib pack reader plus official `mcp` SDK stdio wrapper. The SDK pin lives only in `skill_pack_mcp/requirements.txt` (container/Glama). Release pytest does not install it. |

If Glama generates its own image instead of using this `Dockerfile`, point
build at `pip install -r skill_pack_mcp/requirements.txt` and CMD
`["python", "-m", "skill_pack_mcp"]`. No environment secrets are required.

## Local container check

```bash
docker build -t adsagent-skill-pack-docs .
# The process waits on stdin (stdio MCP). Probe initialize + tools/list:
python scripts/probe_skill_pack_mcp_stdio.py --docker adsagent-skill-pack-docs
```

The probe must show server name `AdsAgent Skill Pack (docs)` and only
`list_skills`, `get_skill`, `get_hosted_mcp_urls`, and `get_pack_readme`.
