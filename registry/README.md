# AdsAgent hosted MCP Registry records

These manifests are snapshots of three existing remote-only entries in the
[official MCP Registry](https://registry.modelcontextprotocol.io/), published on
**2026-08-18**. Each exact `1.0.0` record and `latest` record returned HTTP 200,
`status: "active"` and `isLatest: true` on 2026-10-09. This PR records those
publications; it does not publish or replace them.

| Manifest | Existing Registry name | OAuth MCP endpoint | Published at (UTC) |
| --- | --- | --- | --- |
| [Meta](meta/server.json) | `md.adsagent/meta-mcp` | `https://adsagent.md/mcp/v2` | 2026-08-18T06:06:05.853855Z |
| [Google Ads](google-ads/server.json) | `md.adsagent/google-mcp` | `https://google.adsagent.md/mcp` | 2026-08-18T07:54:07.279685Z |
| [TikTok](tiktok/server.json) | `md.adsagent/tiktok-mcp` | `https://tiktok.adsagent.md/mcp` | 2026-08-18T07:54:07.988395Z |

GitHub first-time MCP directory inclusion is a separate manual review and remains
pending (support ticket **166275**). Official Registry publication does not mean
GitHub has accepted the submission. Do not send duplicate outreach.

Each manifest reproduces the API's `server` object: name, title, description,
repository, website URL, version, schema and Streamable HTTP remote. Registry
`_meta` status/timestamps are evidence recorded here, not fields to publish in
`server.json`. Root `mcp.json` and `.mcp.json` remain client configurations.
The optional docs-only Docker/Glama MCP is a separate product surface.

## Public wording and rights

The published titles and descriptions are:

| Name | Title | Description |
| --- | --- | --- |
| `md.adsagent/meta-mcp` | AdsAgent — Meta Ads MCP | Hosted Meta ads MCP with OAuth, bounded reads, and prepare/confirm writes. |
| `md.adsagent/google-mcp` | AdsAgent — Google Ads MCP | Hosted Google Ads MCP with OAuth, bounded reads, and prepare/confirm writes. |
| `md.adsagent/tiktok-mcp` | AdsAgent — TikTok Ads MCP | Hosted TikTok ads MCP with OAuth, bounded reads, and prepare/confirm writes. |

These descriptions quote existing Registry metadata. They do not expand the
permissions of the installed skills. In particular, the current
[Google Ads skill](../skills/google-ads-insights/SKILL.md) supports read/analysis
workflows; a Registry description mentioning writes does not authorize a write.
For all channels, use advertised capabilities and explicit user approval for
advertising changes.

The published repository links are retained exactly:

- Meta: `https://github.com/kimlucky7/smartads`
- Google Ads: `https://github.com/adsagents/google-adsagent`
- TikTok: `https://github.com/kimlucky7/tiktok-adsagent`

Recording those links does not claim public access or an open-source backend.
The skills, documentation, connection configurations and manifest snapshots in
this repository are covered by [MIT](../LICENSE). The hosted Meta, Google Ads
and TikTok backend implementations are **proprietary**. This repository grants
no license to those backends, trademarks or customer data. See [NOTICE.md](../NOTICE.md),
[privacy](https://adsagent.md/privacy) and [support](mailto:support@adsagent.md).

## Documentation changes versus future metadata updates

This PR only records current public metadata and adds verification guidance.
It makes no Registry update. Do not overwrite or republish the existing `1.0.0`.
Do not create duplicate `io.github.adsagents/*` entries for these endpoints.

Documentation explanations, verification dates and license-boundary notes can
change here without publishing. Any future change to published titles,
descriptions, repository URLs, website URLs, remotes or other server metadata
requires a separately reviewed metadata diff and a new version on the **existing**
entry. For example, pointing repository links to this public guide, using
`https://adsagent.md/connect` as the website, or narrowing the Google description
to the installed read-only skill would change published metadata. None of those
changes is proposed for publication by this snapshot PR.

`1.0.0` is the existing Registry metadata version, not the skill-pack VERSION or
a backend build. A skill-pack version bump does not release a backend.

## Connect with OAuth

1. Add the needed channel's endpoint to an OAuth-capable remote MCP client, or
   use the existing plugin configuration. Start at [AdsAgent Connect](https://adsagent.md/connect).
2. Use the client's Connect/Authenticate action. Each protected resource requires
   its own appropriate authorization; never copy tokens between hosts. All three
   currently advertise `https://adsagent.md` as their authorization server.
3. Check the channel's connection and complete missing advertising-platform
   authorization. Platform access, account scope and history sync are separate
   from client MCP OAuth and Registry publisher authentication.
4. Resume the task only when the selected account is ready. A listing does not
   authorize an advertising account.

## Domain publisher identity

Follow the [official authentication guidance](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/authentication.mdx).
`md.adsagent/*` is the reverse-DNS namespace for `adsagent.md`. Updates require an
identity authorized for that domain namespace, using the official domain-based
DNS or HTTP authentication flow. The public record does not reveal which method
or operator was used for the original publication.

GitHub Owner membership and `mcp-publisher login github` authorize GitHub
namespaces, not these domain entries. Repository write access is also insufficient.
Reuse an existing authorized domain publisher/operator. If none is available,
stop before authentication and obtain explicit owner authorization for the
chosen domain-proof/signing setup. Do not create credentials, change DNS or HTTP
proof files, add CI secrets, or retrieve secrets from another environment.
This PR installs no publication automation and requires no new authorization.

## Validate and inspect existing records

Install the official [mcp-publisher CLI](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx)
and record its version. From the repository root:

```sh
python scripts/validate_registry_manifests.py
mcp-publisher validate registry/meta/server.json
mcp-publisher validate registry/google-ads/server.json
mcp-publisher validate registry/tiktok/server.json
```

CLI validation calls the Registry API without publisher login. Run the checks in
[AGENTS.md](../AGENTS.md) too. Validation does not publish anything.

Query for duplicates and follow every URL-encoded `metadata.nextCursor`:

```sh
curl --fail-with-body 'https://registry.modelcontextprotocol.io/v0.1/servers?search=adsagent&limit=100'
```

Inspect names, repository URLs and remote URLs. The unrelated
`io.github.nowork-studio/adsagent` / `adsagent.org` belongs to another product and
must not be claimed or modified. A timeout or proxy denial is not evidence of
absence. The three existing AdsAgent entries above should be reused.

Read both the exact version and latest record for each existing name:

```sh
for channel in meta google tiktok; do
  for version in 1.0.0 latest; do
    curl --fail-with-body "https://registry.modelcontextprotocol.io/v0.1/servers/md.adsagent%2F${channel}-mcp/versions/${version}"
  done
done
```

Compare the returned `server` object with the corresponding snapshot. Inspect
`_meta["io.modelcontextprotocol.registry/official"]` for status, `isLatest` and
publication time; these can change after this verification date.

- [Meta latest](https://registry.modelcontextprotocol.io/v0.1/servers/md.adsagent%2Fmeta-mcp/versions/latest)
- [Google Ads latest](https://registry.modelcontextprotocol.io/v0.1/servers/md.adsagent%2Fgoogle-mcp/versions/latest)
- [TikTok latest](https://registry.modelcontextprotocol.io/v0.1/servers/md.adsagent%2Ftiktok-mcp/versions/latest)

For a separately authorized future update, first review the new-version diff,
validate it online, check current records and confirm domain publisher authority.
Publish one entry at a time through the official CLI, then read its new exact
version and latest record before continuing. If the response is ambiguous, read
back before retrying. Never run publish against these unchanged `1.0.0` snapshots.
No merge, Registry publication, backend deployment or GitHub outreach is part of
this documentation reconciliation.
