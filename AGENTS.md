# Repository Guidelines

This is the public AdsAgent tri-channel skill pack (Meta, Google Ads, TikTok)
consumed by AI agents as a plugin. It ships Markdown skills, contracts, and
stdlib-only Python validators; there are no runtime dependencies or lock files.
Tool names are public; never add tool descriptions, payload schemas, risk-control
numbers, private repository names, or backend details here — the repository is
public.

## Validation

- `uv run --no-project --managed-python --python 3.12 --with pytest==9.0.2 python -m pytest -q`
- `uv run --no-project --managed-python --python 3.12 python scripts/validate_tri_channel_pack.py`
- `uv run --no-project --managed-python --python 3.12 python scripts/validate_public_tool_manifests.py`

Skills live only in `skills/`. `.claude-plugin/marketplace.json` sets the
`adsagent` source to `./`. Directory review scans this whole repository.
Claude, Cursor, Codex, and Glama all read that root. Do not add a second
skill tree, and do not read the process environment in this repository.
Pass paths as arguments.

## Changes

- One PR per logical change, with a short imperative title and a body that states
  what changed and pastes the check results.
- Do not skip, mark, or delete failing tests to get green.
- Releases are batched. Feature PRs add their notes under `Unreleased` in
  `CHANGELOG.md` and do not touch `VERSION`; a release batch bumps `VERSION`,
  the manifests that mirror it, and the changelog together.
- Release order: the candidate head already carries `VERSION` and
  `release-manifest.json`. Before merging it, run
  `bin/check-skillpack-release-tag` in adsagent-ops against this clone and
  that head. It passes only when the manifest tag is already published and
  the tag tree is the same tree as the head. This repository does not run
  that check and does not contact GitHub.
- Never force-add generated bootstrap files or in-repo virtual environments.
