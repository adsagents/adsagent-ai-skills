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
- `uv run --no-project --managed-python --python 3.12 python scripts/validate_release_manifest_tag.py`

`scripts/check_drift.py` compares the skills with the services' current public
tool manifests. It only warns (see `docs/drift-check.md`); it is not a merge gate.

## Changes

- One PR per logical change, with a short imperative title and a body that states
  what changed and pastes the check results.
- Do not skip, mark, or delete failing tests to get green.
- Releases are batched. Feature PRs add their notes under `Unreleased` in
  `CHANGELOG.md` and do not touch `VERSION`; a release batch bumps `VERSION`,
  the manifests that mirror it, and the changelog together.
- Release order: tag the release commit and create the GitHub release first,
  then update `VERSION` and `release-manifest.json` on main. The manifest on
  main must never reference an unpublished tag — sync clients fetch the
  tagged manifest and fail with 404 until the tag exists.
  `scripts/validate_release_manifest_tag.py` enforces this in CI.
- Never force-add generated bootstrap files or in-repo virtual environments.
