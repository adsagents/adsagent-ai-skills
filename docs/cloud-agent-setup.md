# Repository-local cloud setup

`scripts/cloud-agent-setup.sh` is maintained in this public skill pack. It prepares
the Python 3.12 and pinned pytest cache used by `AGENTS.md` with an existing
`uv` installation. Provision `uv` in the cloud image before setup; if it is
missing, the script stops with an actionable error.

Run `bash scripts/cloud-agent-setup.sh` from the checkout root. When invoked by
absolute path from another directory, it still locates the checkout; an
explicit checkout root can also be passed. `.cursor/environment.json` calls this bundled script;
use the same command for a Codex cloud environment's setup/maintenance step.

The plugin does not ship a general-purpose bootstrap or `bin/` shims.
`/scripts/devbox/` is ignored by Git so generated copies never enter ordinary
plugin commits, and the setup command lives outside that directory. Do not
force-add generated bootstrap files: they reintroduce unused Node setup,
shell-profile changes, system links, and remote installer execution into the
reviewed plugin. The cloud setup regression
tests exercise setup with an isolated home and executable search path.
