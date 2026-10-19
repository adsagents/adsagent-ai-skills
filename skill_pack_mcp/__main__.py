"""python -m skill_pack_mcp — stdio MCP entrypoint for Glama/Docker."""

from __future__ import annotations

import argparse

from skill_pack_mcp.pack import set_root_override


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AdsAgent Skill Pack (docs) stdio MCP."
    )
    parser.add_argument(
        "--root",
        help=(
            "Skill-pack root containing skills/, VERSION, and mcp.json. "
            "Defaults to the directory that contains this package."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    # The server captures its root at import, so the override has to land first.
    set_root_override(args.root)
    from skill_pack_mcp.server import main as serve

    serve()


if __name__ == "__main__":
    main()
