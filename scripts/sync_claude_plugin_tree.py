#!/usr/bin/env python3
"""Generate the Claude plugin directory from the skill-pack sources.

Hand-edit ``skills/``, ``.mcp.json``, and ``.claude-plugin/plugin.json``.
This script rewrites ``plugin/`` from those files. The marketplace entry
``adsagent`` points at ``./plugin``, which is the tree directory review scans.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLUGIN_DIR = Path("plugin")
PLUGIN_SOURCE = "./plugin"
SOURCE_FILES = (
    Path(".claude-plugin/plugin.json"),
    Path(".mcp.json"),
)
SKILLS_DIR = Path("skills")

CREDENTIAL_ENV_RE = re.compile(r"os\.environ|\bos\.getenv\b|\bgetenv\s*\(")
ASSET_REF_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Za-z0-9_./\\-]*\."
    r"(?:png|jpe?g|gif|webp|bmp|ico|tiff?|ttf|otf|woff2?|eot)\b"
)
ASSET_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".ico",
    ".tif",
    ".tiff",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".eot",
}


def source_map(root: Path) -> dict[Path, Path]:
    """Map each generated path to the source path it must match."""
    mapping = {
        PLUGIN_DIR / relative: relative
        for relative in SOURCE_FILES
    }
    skills_root = root / SKILLS_DIR
    if not skills_root.is_dir():
        return mapping
    for path in sorted(skills_root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root)
        mapping[PLUGIN_DIR / relative] = relative
    return mapping


def plugin_files(root: Path) -> list[Path]:
    plugin_root = root / PLUGIN_DIR
    if not plugin_root.exists():
        return []
    files: list[Path] = []
    for path in sorted(plugin_root.rglob("*")):
        if path.is_symlink() or path.is_file():
            files.append(path.relative_to(root))
    return files


def write_plugin_tree(root: Path) -> None:
    mapping = source_map(root)
    expected = set(mapping)
    plugin_root = root / PLUGIN_DIR
    for relative in plugin_files(root):
        path = root / relative
        if relative not in expected and path.is_symlink():
            path.unlink()
        elif relative not in expected and path.is_file():
            path.unlink()
    if plugin_root.exists():
        for directory in sorted(
            (path for path in plugin_root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()
    for destination_rel, source_rel in mapping.items():
        source = root / source_rel
        destination = root / destination_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if destination.is_symlink() or not destination.is_file():
            destination.unlink(missing_ok=True)
            destination.write_bytes(data)
            continue
        if destination.read_bytes() != data:
            destination.write_bytes(data)


def plugin_tree_problems(root: Path) -> list[str]:
    problems: list[str] = []
    mapping = source_map(root)
    plugin_root = root / PLUGIN_DIR
    if not plugin_root.is_dir():
        problems.append("missing plugin/")
        return problems

    actual = plugin_files(root)
    actual_set = set(actual)
    for destination_rel, source_rel in sorted(mapping.items()):
        source = root / source_rel
        destination = root / destination_rel
        if not source.is_file():
            problems.append(f"missing source {source_rel.as_posix()}")
            continue
        if destination_rel not in actual_set or not destination.is_file():
            problems.append(f"missing {destination_rel.as_posix()}")
            continue
        if destination.is_symlink():
            problems.append(f"symlink not allowed: {destination_rel.as_posix()}")
            continue
        if destination.read_bytes() != source.read_bytes():
            problems.append(
                f"{destination_rel.as_posix()} differs from {source_rel.as_posix()}"
            )

    for relative in actual:
        if relative not in mapping:
            problems.append(f"unexpected plugin file {relative.as_posix()}")
        path = root / relative
        if path.is_symlink():
            problems.append(f"symlink not allowed: {relative.as_posix()}")
            continue
        problems.extend(_cleanliness_problems(path, relative))
    return problems


def _cleanliness_problems(path: Path, relative: Path) -> list[str]:
    problems: list[str] = []
    display = relative.as_posix()
    if path.suffix.lower() in ASSET_SUFFIXES:
        problems.append(f"{display} is an image or font file")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        problems.append(f"{display} is not UTF-8 text")
        return problems
    if CREDENTIAL_ENV_RE.search(text):
        problems.append(f"{display} reads environment credentials")
    if ASSET_REF_RE.search(text):
        problems.append(f"{display} references an image or font")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when plugin/ differs from its sources or is not clean",
    )
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if not args.check:
        write_plugin_tree(root)
    problems = plugin_tree_problems(root)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print("PASS: claude plugin tree matches its sources and is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
