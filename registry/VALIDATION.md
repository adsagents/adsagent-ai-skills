# Preparation evidence — 2026-10-09

Status: **prepared, not published**. No successful official Registry API record
has been observed for these candidates. No new OAuth grant or persistent
publisher credential was created. No advertising backend was deployed.

## Passed locally

- All three `server.json` files pass the official `2025-12-11` JSON Schema,
  using Python 3.12 and `jsonschema==4.26.0` with `Draft7Validator` and
  `FormatChecker`. The schema was read from official upstream commit
  `970df037919faa70456dde08c295473002d850e5`, file
  `internal/validators/schemas/2025-12-11.json`.
- `python scripts/validate_registry_manifests.py`: all three manifests match
  both existing client configurations and have no package or static auth header.
- Repository pytest suite: **219 passed, 2 subtests passed**.
- `scripts/validate_tri_channel_pack.py`: passed.
- `scripts/validate_public_tool_manifests.py`: all three channels passed.
- `git diff --check`: passed.

The repository-required checks used `uv run --no-project --managed-python
--python 3.12` (with `pytest==9.0.2` for tests). Because the cloud home is
read-only, `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` pointed to temporary
writable directories; no in-repository virtual environment was created.

## Blocked checks and publication prerequisites

- Official `mcp-publisher` **1.8.1**, build commit
  `f52dc8525a441a3abf5fedc9912152d95af5aab1`, was downloaded from the official
  release. Running `validate <manifest>` for **each of the three manifests**
  reached the validation request but failed with
  `Post "https://registry.modelcontextprotocol.io/v0/validate": Forbidden`.
  This is not a successful online validation.
- Registry duplicate search and exact-name readback were unavailable through
  the current network path. No conclusion that a name is unused can be drawn.
- Public endpoint reachability checks were also rejected by the network proxy
  before reaching the three hosts. Endpoints are supported by committed public
  README/client configuration evidence, not a successful live transport check.
- No existing publisher token was present at the official current token path or
  repository legacy path. Git repository access is not Registry authentication.
  The owner must authorize/perform a new publisher OAuth flow if a suitable
  already authorized identity is unavailable.

Next: restore access to the official Registry and public MCP hosts, perform
online validation and duplicate checks, then authorize publisher login with an
eligible `adsagents` organization Owner and follow [the runbook](README.md).
Report exact-version and latest `active` records only after successful readback.
The draft PR is for review only; merge and GitHub directory acceptance remain
separate steps. Do not repeat existing directory-review outreach.
