# Registry verification evidence — 2026-10-09

Status: **three existing publications verified**, not newly published by this PR.
The manifest snapshots reproduce the Registry's existing `server` objects for
`md.adsagent/meta-mcp`, `md.adsagent/google-mcp` and `md.adsagent/tiktok-mcp`.

## Online evidence

- All six reads (each exact `1.0.0` and `latest`) returned HTTP 200 with
  `status: "active"` and `isLatest: true`. Publication dates are 2026-08-18;
  exact timestamps and public API links are in [README.md](README.md).
- Search `?search=adsagent&limit=100` returned four entries with no next cursor:
  the three domain entries and unrelated `io.github.nowork-studio/adsagent`.
  The latter is deprecated and points to another product, `adsagent.org`.
- The initially proposed `io.github.adsagents/adsagent-{meta,google-ads,tiktok}`
  names each returned genuine HTTP 404. They are not needed: the domain entries
  already cover these exact endpoints. Do not create duplicates.
- Official `mcp-publisher` **1.8.1**, build
  `f52dc8525a441a3abf5fedc9912152d95af5aab1`, validates all three reconciled
  snapshots online successfully. The release archive SHA256 matched the official
  checksum: `a06c9096dcb9727c13555b6be26c7effa707b01f06a4c561ba7a3635443cf2cc`.
- Unauthenticated GETs to all three MCP URLs returned HTTP 401 with
  `WWW-Authenticate` protected-resource discovery. All three resource discovery
  documents returned HTTP 200 with the expected resource URL. Their common
  authorization server `https://adsagent.md` returned HTTP 200 discovery,
  advertising authorization-code flow and PKCE `S256`.
- No OAuth registration, authorization, token exchange or authenticated
  advertising operation was performed. These checks establish public endpoint
  and discovery reachability, not authenticated advertising functionality.

The older cloud environment's CONNECT 403 is superseded by these successful
checks in the refreshed environment. No network settings were changed. Initial
search timeouts were followed by a successful normal request; no policy refusal
was bypassed.

## Local checks

- `python scripts/validate_registry_manifests.py`: passed for all three snapshots
  and both existing OAuth client configurations.
- Repository pytest suite: **219 passed, 2 subtests passed**.
- `scripts/validate_tri_channel_pack.py`: passed.
- `scripts/validate_public_tool_manifests.py`: all three channels passed.
- `git diff --check`: passed.

Repository checks used `uv run --no-project --managed-python --python 3.12`
(with `pytest==9.0.2` for tests), temporary writable UV cache/Python directories,
and no in-repository virtual environment. Snapshot JSON was compared with the
live API `server` objects, including published repository links and descriptions.

## Remaining boundaries

No existing publisher token was found at the official current or checkout legacy
path; no new credentials or grants were created. Future updates require an
authorized `adsagent.md` domain publisher and a new metadata version. GitHub Owner
login does not grant this domain namespace. Existing `1.0.0` must not be republished.

GitHub first-time directory review remains pending (ticket **166275**). No email
or additional submission was sent. Registry publication is not GitHub acceptance.
The skills/docs/config are MIT; hosted advertising backends remain proprietary.
