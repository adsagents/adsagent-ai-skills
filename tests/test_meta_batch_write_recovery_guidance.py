from pathlib import Path

from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return read_contract(ROOT, path)


def test_meta_batch_write_guidance_is_receipt_driven_and_never_replays():
    combined = "\n".join(
        _read(path)
        for path in (
            "README.md",
            "skills/meta-copy/SKILL.md",
            "skills/adsagent-reliability/SKILL.md",
            "docs/output-contract.md",
            "docs/examples.md",
        )
    )
    lowered = combined.lower()

    for term in (
        "automatic_retry_allowed",
        "manual_new_task_allowed",
        "operator_review_required",
        "configurable sequential",
        "fresh approval",
    ):
        assert term in combined

    assert "not evidence of a fixed meta limit" in lowered
    assert "preserve every acknowledged object and receipt" in lowered
    assert "never recreate successful" in lowered
    assert "never replay" in lowered


def test_meta_batch_write_release_surfaces_are_consistently_versioned():
    assert _read("VERSION").strip() == "0.7.53"
    assert '"version": "0.7.53"' in _read(".claude-plugin/plugin.json")
    assert '"version": "0.7.53"' in _read(".claude-plugin/marketplace.json")
    assert "Current contract version: `0.7.53`" in _read("README.md")
    assert 'VERSION = "0.7.53"' in _read("scripts/validate_tri_channel_pack.py")
