#!/usr/bin/env bash
# Cloud-agent bootstrap for the AdsAgent repos (Cursor Cloud Agents and Codex
# cloud environments). One script for every repo: it discovers what the
# checked-out repo pins and installs exactly that.
#
#   - fnm + the Node version from .node-version (if present)
#   - uv + the CPython version from .python-version (if present)
#   - the devbox shims (node/npm/npx dispatcher, codex-python, python3.12) so the
#     repo AGENTS.md commands work unchanged
#   - codex-python environment for the repo's locks
#   - node_modules for every package directory that has a package-lock.json
#     (google-adsagent's dashboard-app goes through its own release_driver helper)
#
# Idempotent and non-interactive. No secrets, no services, no sudo required
# (uses sudo only opportunistically to expose the shims system-wide).
#
# usage: bash cloud-agent-install.sh [<repo-root>]      default: cwd
set -euo pipefail

REPO_ROOT="$(cd "${1:-$PWD}" && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
FNM_DIR="${FNM_DIR:-$HOME/.local/share/fnm}"
export PATH="$BIN_DIR:$PATH"
log() { printf '[cloud-agent-install] %s\n' "$*"; }

mkdir -p "$BIN_DIR" "$FNM_DIR"
for f in curl git tar; do command -v "$f" >/dev/null || { echo "missing $f" >&2; exit 1; }; done

# --- devbox shim sources -------------------------------------------------------
# When run from a checkout of adsagent-marketing, HERE is scripts/devbox. Other
# repos clone adsagent-marketing shallowly and call this script from there.
SHIM_SRC="$HERE/bin"
[[ -x "$SHIM_SRC/codex-python" ]] || { echo "devbox shim sources not found next to this script" >&2; exit 1; }

# --- Node -------------------------------------------------------------------------
if [[ -f "$REPO_ROOT/.node-version" ]]; then
    node_version="$(tr -d '[:space:]v' < "$REPO_ROOT/.node-version")"
    if [[ ! -x "$FNM_DIR/fnm" ]]; then
        log "installing fnm"
        curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir "$FNM_DIR" --skip-shell >/dev/null
    fi
    if [[ ! -x "$FNM_DIR/node-versions/v$node_version/installation/bin/node" ]]; then
        log "installing Node v$node_version"
        FNM_DIR="$FNM_DIR" "$FNM_DIR/fnm" install "$node_version"
    fi
    ln -sfn "$FNM_DIR/fnm" "$BIN_DIR/fnm"
fi

# --- Python -----------------------------------------------------------------------
if ! command -v uv >/dev/null; then
    log "installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$BIN_DIR" UV_NO_MODIFY_PATH=1 sh >/dev/null
fi
if [[ -f "$REPO_ROOT/.python-version" ]]; then
    py_version="$(cut -d. -f1,2 < "$REPO_ROOT/.python-version" | tr -d '[:space:]')"
    if ! uv python find --managed-python "$py_version" >/dev/null 2>&1; then
        log "installing CPython $py_version"
        uv python install "$py_version" --managed-python
    fi
fi

# --- shims --------------------------------------------------------------------------
install -m 0755 "$SHIM_SRC/node-dispatch" "$BIN_DIR/node-dispatch"
for tool in node npm npx; do ln -sfn "$BIN_DIR/node-dispatch" "$BIN_DIR/$tool"; done
install -m 0755 "$SHIM_SRC/codex-python" "$BIN_DIR/codex-python"
install -m 0755 "$SHIM_SRC/python3.12" "$BIN_DIR/python3.12"
# Agent shells may not read ~/.profile; expose the shims system-wide when allowed.
# ADSAGENT_NO_SYSTEM_LINKS=1 skips this (used when simulating on a shared box).
if [[ -z "${ADSAGENT_NO_SYSTEM_LINKS:-}" ]] && sudo -n true 2>/dev/null; then
    for tool in node npm npx codex-python python3.12; do
        sudo -n ln -sfn "$BIN_DIR/$tool" "/usr/local/bin/$tool"
    done
    uv_path="$(command -v uv || true)"
    if [[ -n "$uv_path" && "$uv_path" != /usr/local/bin/uv ]]; then
        sudo -n ln -sfn "$uv_path" /usr/local/bin/uv
    fi
fi
for rc in "$HOME/.profile" "$HOME/.bashrc"; do
    touch "$rc"
    grep -qF 'adsagent cloud-agent-install' "$rc" || printf '\n# adsagent cloud-agent-install\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$rc"
done

# --- repo dependencies ------------------------------------------------------------------
cd "$REPO_ROOT"
if [[ -f .python-version ]] && ls requirements*.lock >/dev/null 2>&1; then
    log "codex-python sync"
    codex-python sync --project .
elif [[ -f pyproject.toml && -f uv.lock ]]; then
    log "uv sync (project)"
    UV_PROJECT_ENVIRONMENT="$HOME/.local/share/adsagent-py/uv-projects/$(basename "$REPO_ROOT")" \
        uv sync --frozen --all-extras ${py_version:+--python "$py_version"}
fi

# Identify the repo by its origin URL, not the checkout directory: cloud VMs
# check out into /workspace, so the directory name says nothing.
origin_url="$(git config --get remote.origin.url 2>/dev/null || true)"
repo_name="$(basename "${origin_url%.git}")"          # last path component of https://, git@…:, or file:// URLs
[[ -n "$repo_name" && "$repo_name" != "." ]] || repo_name="$(basename "$REPO_ROOT")"
for lock in $(git ls-files -- '*/package-lock.json' 'package-lock.json' 2>/dev/null); do
    dir="$(dirname "$lock")"
    [[ -f "$dir/package.json" ]] || continue
    if [[ "$repo_name" == "google-adsagent" && "$dir" == "dashboard-app" ]]; then
        log "google dashboard-app via release_driver node-dependencies"
        codex-python run --project . -- python scripts/release_driver.py node-dependencies --repo-root .
    else
        log "npm ci in $dir"
        (cd "$dir" && npm ci --no-audit --no-fund --loglevel=error)
    fi
done

log "done: node=$(node -v 2>/dev/null || echo n/a) npm=$(npm -v 2>/dev/null || echo n/a) python=$(python3.12 -V 2>/dev/null || echo n/a)"
