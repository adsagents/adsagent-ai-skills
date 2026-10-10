#!/usr/bin/env bash
# Repository-local setup for Cursor Cloud Agents and Codex cloud environments.
# Provision uv in the cloud image before running this script. The skill pack
# needs only Python 3.12 and pytest; it has no Node or service dependencies.
# usage: bash scripts/cloud-agent-setup.sh [<repo-root>]
set -euo pipefail

repo_root="$(cd "${1:-$(dirname "${BASH_SOURCE[0]}")/..}" && pwd)"
cd "$repo_root"

if ! command -v uv >/dev/null 2>&1; then
    echo '[cloud-agent-setup] uv is required; provision it in the cloud image before setup.' >&2
    exit 127
fi

# Warm the managed Python and pinned pytest cache used by AGENTS.md checks.
# Dependency installation uses the existing package manager, without fetching
# and executing remote installer scripts or reading local credentials.
uv run --no-project --managed-python --python 3.12 --with pytest==9.0.2 \
    python -m pytest --version
