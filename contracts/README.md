# Contracts

- `public-tool-references.json`: the tools each channel's skills reference, with
  the capability the skills expect. A reference must appear in a skill, and a
  tool named in a skill must be listed here. Checked offline in CI.
- `deprecated-tools.json`: tool names the services have deprecated, with the
  public replacement. Skills and docs must not mention them. Checked offline.
- `drift-policy.json`: whether the drift check only warns or blocks on removed
  tools. See [docs/drift-check.md](../docs/drift-check.md).

There are no committed snapshots of the services' tool lists. Freshness is
checked against the services' current manifests by `scripts/check_drift.py`.
