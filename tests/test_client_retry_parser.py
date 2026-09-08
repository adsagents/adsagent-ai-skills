from __future__ import annotations

import math
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.validate_tri_channel_pack import validate_retry_parser_reference


PARSER_PATH = (
    ROOT / "skills/adsagent-reliability/retry-parser.md"
)


@pytest.fixture(scope="module")
def parser():
    source = re.search(
        r"```python\n(.*?)```", PARSER_PATH.read_text(), re.DOTALL,
    ).group(1)
    validate_retry_parser_reference(source)
    namespace = {}
    # Execute only this checked-in pure reference function. The release
    # validator itself continues to inspect Markdown with AST, never exec.
    exec(compile(source, str(PARSER_PATH), "exec"), namespace)
    return namespace["retry_after_seconds"]


@pytest.mark.parametrize("payload", [
    {"retry_after_seconds": 120},
    {"data": {"retry_after_seconds": 120}},
    {"details": {"retry_after_seconds": 120}},
    {"error": {"retry_after_seconds": 120}},
    {"error": {"data": {"retry_after_seconds": 120}}},
    {"error": {"details": {"retry_after_seconds": 120}}},
    {"structuredContent": {"details": {"retry_after_seconds": 120}}},
    {"structuredContent": {"error": {"retry_after_seconds": 120}}},
    {"result": {"details": {"retry_after_seconds": 120}}},
    {"result": {"structuredContent": {"details": {"retry_after_seconds": 120}}}},
])
def test_supported_mcp_error_envelopes_preserve_delay(parser, payload):
    assert parser(payload) == 120


def test_all_applicable_delays_use_maximum(parser):
    payload = {
        "retry_after": 8,
        "retry_after_seconds": 10,
        "data": {"retry_after": 12},
        "error": {"data": {"retry_after_seconds": 30}},
        "result": {"structuredContent": {"details": {"retry_after_seconds": 120}}},
    }
    assert parser(payload, {"rEtRy-AfTeR": "5"}) == 120
    assert parser(payload, {"Retry-After": "240"}) == 240


@pytest.mark.parametrize("value", [
    True, False, None, 0, -1, "", "invalid", [], {},
    float("nan"), float("inf"), float("-inf"), "NaN", "Infinity", "-Infinity",
    pytest.param(10 ** 500, id="overflowing_integer"),
])
def test_invalid_delays_are_ignored(parser, value):
    assert parser({"retry_after_seconds": value}) is None
    assert parser({"retry_after_seconds": value}, {"Retry-After": "3"}) == 3
    assert parser({"retry_after_seconds": 7}, {"Retry-After": value}) == 7


@pytest.mark.parametrize("payload", [None, [], "error", 5, True, {"error": "not-an-object"}])
def test_malformed_error_envelopes_do_not_break_backoff(parser, payload):
    assert parser(payload) is None
    assert parser(payload, {"Retry-After": " 2.5 "}) == 2.5


def test_nested_non_error_business_values_are_not_delays(parser):
    payload = {"result": {"structuredContent": {"data": {
        "items": [{"retry_after_seconds": 900}],
    }}}}
    assert parser(payload) is None


def test_parser_only_returns_finite_delay_and_does_not_authorize_write_retry(parser):
    payload = {"structuredContent": {
        "retryable": False,
        "details": {"retry_after_seconds": "0.25", "request_sent": True},
    }}
    delay = parser(payload)
    assert delay == 0.25 and math.isfinite(delay)
    assert payload["structuredContent"]["retryable"] is False
    assert payload["structuredContent"]["details"]["request_sent"] is True
