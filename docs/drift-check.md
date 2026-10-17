# Drift check

The skills name AdsAgent MCP tools. The services change independently, so a
scheduled check compares what the skills reference with what each service
currently publishes. **It only warns.** It never blocks a merge, a pack release,
or a service release.

## What it checks

For each channel (Meta, Google Ads, TikTok), against that channel's current
tool-name manifest:

| Finding | Meaning | Severity today |
| --- | --- | --- |
| Removed | A skill references a tool the service no longer lists | warning |
| Deprecated | A referenced tool is marked deprecated (with its replacement) | warning |
| Newly deprecated | The service deprecated a tool that is not yet in `contracts/deprecated-tools.json` | warning |
| Capability not proven | A referenced tool no longer carries the capability the skills expect | warning |
| Uncovered | A service tool no skill references (confirmation tools excluded) | info |

The blocking CI checks stay offline and need no service artifact: skill
structure, the reference contract (`contracts/public-tool-references.json`), and
the deprecated list. Skills and docs must not mention a deprecated tool.

## Where the manifests come from

The services' source repositories are private, so this repository never names
them. Each channel's manifest location is configuration, not code. Set one of
these per channel as a repository **variable** (not a secret):

| Variable | Channel |
| --- | --- |
| `ADSAGENT_DRIFT_SOURCE_META` | Meta |
| `ADSAGENT_DRIFT_SOURCE_GOOGLE` | Google Ads |
| `ADSAGENT_DRIFT_SOURCE_TIKTOK` | TikTok |

A value is an `https://` URL of a published manifest, or
`github:OWNER/REPO/PATH@REF` (read through the GitHub API with the repository
secret `ADSAGENT_DRIFT_READ_TOKEN`, a read-only token), or a local file path for
local runs. A channel without a source is skipped and listed as "not compared";
with no source at all the check does nothing.

Preferred setup, in order:

1. **Each service publishes its tool names at a public URL.** Same-origin and
   names only, in the format below. The scheduled job fetches it daily.
2. **Each service nudges the check after a release** with a
   `repository_dispatch` event of type `mcp-manifest-published` (no payload
   needed; the job then fetches the manifests). This needs a token with write
   access to this repository on the service side, which is an ops decision.
3. **Read the private repositories with a read-only token** through a
   `github:` source. Works today if a token is provisioned; the token never
   reaches pull requests from forks.

### Manifest format

```json
{
  "manifest_version": 1,
  "platform": "meta",
  "guide_version": "2026-10-17.5",
  "tool_count": 2,
  "tools": [
    {"name": "setup_get_status", "required_capability": "mcp.read"},
    {"name": "entities_prepare_update", "required_capability": "mcp.optimize.write"}
  ],
  "call_only_tools": [
    {
      "name": "old_confirm_tool",
      "deprecated_since": "2026-08-06",
      "remove_after": "2026-11-04",
      "replacement": "new_confirm_tool"
    }
  ]
}
```

Tool names, capability labels, and deprecation dates only. No schemas,
descriptions, digests, repository names, or commit numbers. The services'
existing generated tool manifests already use this shape.

## What happens on a finding

The scheduled workflow (`.github/workflows/drift-check.yml`) writes the report to
the run summary and opens one issue labelled `drift`, or comments on the open
one. GitHub emails repository watchers; there is no separate mail integration.
Pull-request CI runs the same check as a non-blocking step, so drift shows up as
a warning annotation.

Run it locally:

```bash
python scripts/check_drift.py --source meta=./meta-tools.json
```

Exit code `0` is clean or nothing to compare, `10` is warnings, `1` is a finding
the policy says must block, `2` is an unreadable source.

## Policy and the planned upgrade

`contracts/drift-policy.json` sets the mode:

- `warn` (now): report only.
- `block-removed`: exit `1` when a skill references a tool the service no longer
  lists. Deprecations and new tools stay warnings.

The plan is to run `warn` for two weeks from the first scheduled run with sources
configured, then switch to `block-removed` by editing that one file in a normal
pull request. Only a removed tool ever blocks, and only through this check's own
exit code: nothing is wired into a release automatically until that switch.
