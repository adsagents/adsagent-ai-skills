"""Shared validation helpers for the public AdsAgent skill pack."""

from __future__ import annotations

import re
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)")


class SkillContractError(ValueError):
    """Raised when a skill reference graph violates the public contract."""


def markdown_references(path: Path) -> list[str]:
    """Return local Markdown references in source order."""
    text = path.read_text(encoding="utf-8")
    references: list[str] = []
    for target in MARKDOWN_LINK_RE.findall(text):
        target = target.split("#", 1)[0]
        if "://" in target or target.startswith("/"):
            continue
        references.append(target)
    return references


def read_skill_bundle(
    root: Path,
    skill_name: str,
    *,
    max_files: int = 16,
    max_bytes: int = 128_000,
) -> tuple[str, tuple[Path, ...]]:
    """Read one SKILL.md plus its bounded local reference graph."""
    skills_root = (root / "skills").resolve()
    entrypoint = (skills_root / skill_name / "SKILL.md").resolve()
    if not entrypoint.is_file():
        raise SkillContractError(f"missing skill entrypoint: {skill_name}")

    pending = [entrypoint]
    visited: set[Path] = set()
    ordered: list[Path] = []
    chunks: list[str] = []
    total_bytes = 0

    while pending:
        path = pending.pop(0).resolve()
        if path in visited:
            continue
        if skills_root not in path.parents:
            raise SkillContractError(
                f"skill reference escapes skills/: {path}"
            )
        if not path.is_file():
            raise SkillContractError(f"missing skill reference: {path}")

        data = path.read_bytes()
        total_bytes += len(data)
        if len(visited) + 1 > max_files:
            raise SkillContractError(
                f"{skill_name} reference graph exceeds {max_files} files"
            )
        if total_bytes > max_bytes:
            raise SkillContractError(
                f"{skill_name} reference graph exceeds {max_bytes} bytes"
            )

        text = data.decode("utf-8")
        visited.add(path)
        ordered.append(path)
        chunks.append(text)

        for target in markdown_references(path):
            candidate = (path.parent / target).resolve()
            if candidate not in visited and candidate not in pending:
                pending.append(candidate)

    return "\n".join(chunks), tuple(ordered)
