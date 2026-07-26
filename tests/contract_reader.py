"""Test helper that follows progressive Skill references."""

from __future__ import annotations

from pathlib import Path

from scripts.skill_contract import read_skill_bundle


def read_contract(root: Path, relative_path: str) -> str:
    path = Path(relative_path)
    parts = path.parts
    if (
        len(parts) == 3
        and parts[0] == "skills"
        and parts[2] == "SKILL.md"
    ):
        text, _ = read_skill_bundle(root, parts[1])
        return text
    return (root / path).read_text(encoding="utf-8")
