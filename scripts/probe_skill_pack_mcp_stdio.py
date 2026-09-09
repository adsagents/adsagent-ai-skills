#!/usr/bin/env python3
"""Stdlib JSON-RPC probe for the skill-pack docs MCP over stdio.

Does not import the MCP SDK. Used to verify Docker/local stdio initialize and
tools/list. Not part of release pytest (that suite must stay SDK-free).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from typing import Any


def _encode(message: dict[str, Any]) -> bytes:
    body = json.dumps(message, separators=(",", ":")).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body


def _read_message(buffer: bytearray) -> dict[str, Any] | None:
    header_end = buffer.find(b"\r\n\r\n")
    if header_end == -1:
        newline = buffer.find(b"\n")
        if newline == -1:
            return None
        line = bytes(buffer[:newline]).strip()
        if not line:
            del buffer[: newline + 1]
            return _read_message(buffer)
        try:
            message = json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            return None
        del buffer[: newline + 1]
        return message
    header = bytes(buffer[:header_end]).decode("ascii", errors="replace")
    length = 0
    for raw_line in header.split("\r\n"):
        if raw_line.lower().startswith("content-length:"):
            length = int(raw_line.split(":", 1)[1].strip())
    start = header_end + 4
    if len(buffer) < start + length:
        return None
    body = bytes(buffer[start : start + length])
    del buffer[: start + length]
    return json.loads(body.decode("utf-8"))


def _pump(stream, buffer: bytearray, stop: threading.Event) -> None:
    while not stop.is_set():
        chunk = stream.read(1)
        if not chunk:
            break
        buffer.extend(chunk)


def _wait_response(
    buffer: bytearray, wanted_id: int, timeout: float
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = _read_message(buffer)
        if message is None:
            time.sleep(0.02)
            continue
        if message.get("id") == wanted_id:
            return message
    raise TimeoutError(f"timed out waiting for JSON-RPC id={wanted_id}")


def probe(command: list[str], timeout: float) -> dict[str, Any]:
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    buffer = bytearray()
    stop = threading.Event()
    reader = threading.Thread(
        target=_pump, args=(proc.stdout, buffer, stop), daemon=True
    )
    reader.start()
    try:
        proc.stdin.write(
            _encode(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "skill-pack-docs-probe",
                            "version": "0.0.1",
                        },
                    },
                }
            )
        )
        proc.stdin.flush()
        initialize = _wait_response(buffer, 1, timeout)
        proc.stdin.write(
            _encode(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
            )
        )
        proc.stdin.flush()
        proc.stdin.write(
            _encode(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {},
                }
            )
        )
        proc.stdin.flush()
        tools = _wait_response(buffer, 2, timeout)
        return {"initialize": initialize, "tools": tools}
    finally:
        stop.set()
        try:
            proc.stdin.close()
        except OSError:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docker",
        metavar="IMAGE",
        help="run `docker run --rm -i IMAGE` instead of a local command",
    )
    parser.add_argument(
        "--cmd",
        nargs=argparse.REMAINDER,
        help="local command after --cmd, e.g. --cmd python -m skill_pack_mcp",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    if args.docker:
        command = ["docker", "run", "--rm", "-i", args.docker]
    elif args.cmd:
        command = list(args.cmd)
    else:
        parser.error("pass --docker IMAGE or --cmd COMMAND")
    result = probe(command, args.timeout)
    initialize = result["initialize"]
    if "error" in initialize:
        print(json.dumps(initialize, indent=2))
        return 1
    server_info = initialize["result"].get("serverInfo", {})
    tools = [
        tool["name"]
        for tool in result["tools"]["result"].get("tools", [])
    ]
    print(f"server: {server_info.get('name')}")
    print(f"version: {server_info.get('version')}")
    print("tools:")
    for name in tools:
        print(f"  - {name}")
    expected = {
        "list_skills",
        "get_skill",
        "get_hosted_mcp_urls",
        "get_pack_readme",
    }
    if server_info.get("name") != "AdsAgent Skill Pack (docs)":
        print("error: unexpected server name", file=sys.stderr)
        return 1
    if set(tools) != expected:
        print(f"error: unexpected tools {tools}", file=sys.stderr)
        return 1
    print("ok: docs MCP initialize + tools/list")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
