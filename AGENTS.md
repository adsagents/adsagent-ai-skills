# Repository Guidelines

This is the public AdsAgent tri-channel skill pack (Meta, Google Ads, TikTok)
consumed by AI agents as a plugin. It ships Markdown skills, contracts, and
stdlib-only Python validators; there are no runtime dependencies or lock files.
Never add internal tool catalogs, payload schemas, or backend details here —
the repository is public.

## Validation

- `uv run --no-project --managed-python --python 3.12 --with pytest==9.0.2 python -m pytest -q`
- `uv run --no-project --managed-python --python 3.12 python scripts/validate_tri_channel_pack.py`
- `uv run --no-project --managed-python --python 3.12 python scripts/validate_public_tool_manifests.py`

Bump `VERSION` and `CHANGELOG.md` together when skill content changes.

## Cloud Agent delivery (owner standing authorization, 2026-09-04)

Applies to Cursor Cloud Agents and Codex cloud agents working in this
repository (environment: `.cursor/environment.json` →
`scripts/devbox/cloud-agent-install.sh`). The owner does not review or merge
by hand; this section is the standing authorization that lets a cloud agent
take a change from task to `main` on its own. It does **not** extend to
anything in the "still forbidden" list.

1. Finish the task, then run every check below. Everything that passed on
   `main` must still pass; do not skip, mark, or delete failing tests to get
   green.
2. Open one PR per logical change with a short imperative title and a body
   that states what changed and pastes the check results.
3. If Bugbot review is enabled on the PR, wait for it and address every
   comment, then re-run the checks.
4. Squash-merge into `main` yourself. Report the PR link, the merge SHA, and
   the check results.

Still forbidden for cloud agents, without exception: deploying or releasing
(`release_local.sh`, `deploy.sh`, `wrangler deploy`), connecting to the VPS,
touching Cloudflare, Supabase production data, or any secret, and creating an
in-repo `.venv`. Releases happen on the shared dev box with explicit operator
authorization (see `docs/internal/DEV_BOX_RUNBOOK.md` in adsagent-marketing).

Checks for this repository:

- the three validation commands above
- `CHANGELOG.md` and `VERSION` updated when any file under `skills/` or
  `contracts/` changed
