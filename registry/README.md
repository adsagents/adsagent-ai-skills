# AdsAgent hosted MCP Registry publication

These are three independent **remote-only publication candidates** for the
[official MCP Registry](https://registry.modelcontextprotocol.io/). Committing
or validating these files does not publish them. GitHub MCP Registry inclusion
is a separate, manually reviewed process; official Registry publication does
not guarantee GitHub inclusion.

| Manifest | Proposed Registry name | OAuth MCP endpoint |
| --- | --- | --- |
| [Meta](meta/server.json) | `io.github.adsagents/adsagent-meta` | `https://adsagent.md/mcp/v2` |
| [Google Ads](google-ads/server.json) | `io.github.adsagents/adsagent-google-ads` | `https://google.adsagent.md/mcp` |
| [TikTok](tiktok/server.json) | `io.github.adsagents/adsagent-tiktok` | `https://tiktok.adsagent.md/mcp` |

Each entry has one Streamable HTTP remote, no installable package, and no static
authentication headers. Root `mcp.json` and `.mcp.json` remain the client/plugin
configurations. The optional docs-only Docker/Glama MCP is a separate product
surface and must not be published as any of these hosted advertising servers.

## Public capabilities and rights

Descriptions are supported by the public skills:

- Meta: [performance analysis](../skills/meta-insights/SKILL.md) and
  [approval-backed ad copy](../skills/meta-copy/SKILL.md).
- Google Ads: [account, Search, PMax and performance reads](../skills/google-ads-insights/SKILL.md).
  This entry makes no Google advertising write claim.
- TikTok: [performance, creative and campaign workflows](../skills/tiktok-insights/SKILL.md).
  Availability depends on the authenticated account and advertised capabilities;
  approval-backed advertising changes require user review and confirmation.

The manifest `repository` points to this **public guide and connection-config
repository**, following the remote-guide pattern used by
[Figma](https://github.com/figma/mcp-server-guide/blob/main/server.json).
It does not contain the hosted server implementations. Public skills, docs,
connection configurations and these manifests are covered by [MIT](../LICENSE).
Hosted Meta, Google Ads and TikTok backend implementations are **proprietary**;
this repository grants no license to them, trademarks or customer data. See
[NOTICE.md](../NOTICE.md), [privacy](https://adsagent.md/privacy), and
[support](mailto:support@adsagent.md).

`1.0.0` is the initial Registry metadata revision for each independent entry,
not the skill-pack VERSION or a claim about a backend build. Advance the
appropriate entry's version when publishing changed metadata. Do not reset an
already published version or treat a skill-pack version bump as a backend release.

## Connect with OAuth

1. Add only the needed channel's URL above to an OAuth-capable remote MCP client,
   or use the existing Claude/Cursor plugin configuration. Start at
   [AdsAgent Connect](https://adsagent.md/connect) for client onboarding.
2. Use the client's Connect/Authenticate action and complete browser OAuth with
   your AdsAgent login. Each server has its own OAuth authorization. Do not paste
   tokens into manifests or copy a token between hosts.
3. Ask AdsAgent to check the selected channel's connection and complete any
   missing advertising-platform authorization. Platform authorization, usable
   account scope and initial history sync are separate from client MCP OAuth.
4. Resume the intended task once the selected account is ready. Installing this
   guide or seeing a Registry listing does not authorize an advertising account.

Examples: “Show yesterday's Meta campaign performance”; “Analyze Google Ads
Search and PMax performance for my selected customer”; “Show TikTok advertiser
performance, then prepare a campaign change for my review.”

## Publisher identity and prerequisites

Use [official authentication guidance](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/authentication.mdx).
The proposed namespace requires a GitHub identity entitled to publish under
`io.github.adsagents/*`. Current upstream guidance requires an **Owner** of the
`adsagents` organization for GitHub OAuth/PAT organization publishing; repository
write access alone is insufficient. Verify the namespace granted at login.
Never fall back silently to a personal namespace or an unrelated product name.

Registry publisher authentication is separate from end-user AdsAgent OAuth.
Reuse a suitable already authorized publisher identity only. If none exists,
stop and ask the owner to perform/approve the official browser device flow:

```sh
mcp-publisher login github
```

Do not start a new OAuth grant, create/configure a persistent token, or add CI
secrets without owner approval. Do not retrieve credentials from other machines.
No automatic publication workflow is installed by this change. GitHub Actions
OIDC is an optional future setup requiring separately reviewed configuration.

## Validate and check for duplicates before publishing

Install the official [mcp-publisher CLI](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx)
and record its version. These manifests use schema `2025-12-11` from the
[current remote-server documentation](https://modelcontextprotocol.io/registry/remote-servers).
From the repository root:

```sh
python scripts/validate_registry_manifests.py
mcp-publisher validate registry/meta/server.json
mcp-publisher validate registry/google-ads/server.json
mcp-publisher validate registry/tiktok/server.json
```

The official CLI validation calls the Registry API and needs network access, but
not publisher login. Local consistency checks or offline JSON-schema validation
are not a replacement for that online check. Run the repository checks in
[AGENTS.md](../AGENTS.md) as well.

Before first publication, query the official API:

```sh
curl --fail-with-body 'https://registry.modelcontextprotocol.io/v0.1/servers?search=adsagent&limit=100'
```

Follow every `metadata.nextCursor` (URL-encoded in the `cursor` parameter),
inspect names, repository URLs and remote URLs, and check each proposed name's
`/versions/latest` route below. A genuine 404 means that exact name was absent;
a timeout, proxy denial or 5xx does not. Reuse an existing official entry if the
same AdsAgent service is already listed, and choose a new version if needed.
The unrelated `io.github.nowork-studio/adsagent` / `adsagent.org` is not this
product and must not be claimed or modified. If duplicate checks are unavailable,
stop before publication.

## Publish, then read back each result

Use the reviewed manifest commit. The manifests are metadata-only: publication
requires no backend deployment and technically does not require a merge. For
public review, preferably make the reviewed files reachable on the default branch
first, through a separately authorized merge; a draft PR is not a merged release.
Do not merge as part of the current preparation task.

After online validation, duplicate checks and authorized login succeed:

```sh
mcp-publisher publish registry/meta/server.json
mcp-publisher publish registry/google-ads/server.json
mcp-publisher publish registry/tiktok/server.json
```

Run one publish at a time. After each success, read both its exact version and
latest record before continuing. For example, for Meta:

```sh
curl --fail-with-body 'https://registry.modelcontextprotocol.io/v0.1/servers/io.github.adsagents%2Fadsagent-meta/versions/1.0.0'
curl --fail-with-body 'https://registry.modelcontextprotocol.io/v0.1/servers/io.github.adsagents%2Fadsagent-meta/versions/latest'
```

Repeat using `adsagent-google-ads` and `adsagent-tiktok`. Check the returned
`server.name`, `server.version`, `server.repository` and `server.remotes` against
the reviewed file, and check `_meta["io.modelcontextprotocol.registry/official"]`
for `status: "active"` and `isLatest: true`. Record the manifest commit, CLI
version, publication time, both API URLs and returned metadata for each entry.
If publication times out or returns an ambiguous error, read back first; do not
blindly retry or bump versions. Report partial success per channel.

These are **expected readback routes**, not evidence of existing listings:

- [Meta latest](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.adsagents%2Fadsagent-meta/versions/latest)
- [Google Ads latest](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.adsagents%2Fadsagent-google-ads/versions/latest)
- [TikTok latest](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.adsagents%2Fadsagent-tiktok/versions/latest)

Only after all three readbacks succeed should the operator report them as
published and use their real records for the existing GitHub directory review.
Do not resubmit outreach or represent pending manual review as acceptance.
