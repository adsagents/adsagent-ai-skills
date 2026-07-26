# Pinned MCP Tool Manifests

This directory contains public-safe snapshots of the Meta, Google Ads, and
TikTok Hosted MCP tool surfaces. Snapshots include names, bounded
classification metadata, capability/gate evidence, and digests. They do not
include tool schemas, descriptions, credentials, tenant data, raw requests, or
service source code.

`provenance.json` binds every snapshot to a channel, committed source revision,
public artifact path, guide version, tool count, and exact SHA-256. Release CI
uses only these committed files and never calls a live service or downloads an
artifact.

Update all three snapshots together:

```bash
python scripts/sync_public_tool_manifests.py \
  --source meta=/path/to/meta-tools.json \
  --source google=/path/to/google-tools.json \
  --source tiktok=/path/to/tiktok-tools.json
```

Every source repository must be clean, and each source artifact must exist
unchanged in its repository's `HEAD`. Missing channels and partial updates are
rejected.

## Service Artifact Contract

Each service artifact uses `manifest_version: 1` and declares `platform`,
`guide_version`, `tool_count`, and `tools[]`. Every tool entry has a canonical
`name`. A required capability may be expressed as `required_capability` or
`required_capabilities[]`; callable gates may be expressed as
`capability_gate`, `capability_gates[]`, or a separate
`capability_gated_tools` list. The Skill Pack normalizes these wire formats but
does not infer missing evidence: every capability or gate referenced by a
Skill must be present on that real service entry.
