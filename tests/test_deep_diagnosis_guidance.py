from __future__ import annotations

import json
from pathlib import Path

from scripts.skill_routing_contract import expected_skill_activation
from tests.contract_reader import read_contract


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return read_contract(ROOT, relative_path)


def _bundle() -> str:
    return " ".join(_read("skills/adsagent-diagnosis/SKILL.md").split())


def _contract() -> str:
    return _read("skills/adsagent-diagnosis/diagnosis-contract.md")


def test_skill_is_packaged_and_routed() -> None:
    plugin = json.loads(_read(".claude-plugin/plugin.json"))
    assert "./skills/adsagent-diagnosis" in plugin["skills"]

    router = _read("skills/adsagent-router/SKILL.md")
    assert "`adsagent-diagnosis`" in router
    assert "adsagent-diagnosis" in _read("README.md")


def test_diagnosis_is_user_triggered_only() -> None:
    text = _bundle()

    for term in (
        "诊断",
        "体检",
        "审计",
        "账户检查",
        "diagnosis",
        "audit",
        "account health check",
        "Only when the user asks",
        "Never run a diagnosis on a schedule, automatically, "
        "or as a background habit",
    ):
        assert term in text, term


def test_run_flow_checks_status_then_confirms_before_spending_a_run() -> None:
    text = _bundle()

    for term in (
        "diagnosis_get_status",
        "diagnosis_run",
        "diagnosis_get_report",
        "diagnosis_list_reports",
        "acknowledge_credit_use=true",
        "explicit user confirmation",
        "this window's one run",
        "Pro",
        "Max",
        "needs_confirmation",
    ):
        assert term in text, term
    assert text.index("diagnosis_get_status") < text.index("diagnosis_run")


def test_report_reading_rules_keep_unknown_and_partial_honest() -> None:
    text = _bundle()

    for term in (
        "score_drivers",
        "`unknown` dimension is not healthy",
        "partial",
        "Do not invent numbers",
        "data_as_of",
    ):
        assert term in text, term


def test_recommendations_stay_on_the_prepare_and_approve_path() -> None:
    text = _bundle()

    for term in (
        "diagnosis_prepare_recommendation",
        "same channel connector",
        "A prepare changes nothing by itself",
        "Never claim a change was made",
        "recommendation_other_channel",
        "recommendation_stale",
        "recommendation_not_actionable",
    ):
        assert term in text, term


def test_plan_and_window_errors_stop_instead_of_retrying() -> None:
    text = _bundle()

    for term in (
        "diagnosis_not_in_plan",
        "diagnosis_runs_exhausted",
        "diagnosis_in_progress",
        "billing_read_only",
        "do not retry in a loop",
        "diagnosis_update_schedule",
        "email_summary",
        "never schedules a run",
    ):
        assert term in text, term


def test_contract_keeps_internal_scoring_details_out() -> None:
    text = _contract().lower()

    for forbidden in (
        "weight",
        "threshold",
        "multiplier",
        "gaql",
        "quota ledger",
        "recheck_of",
    ):
        assert forbidden not in text, forbidden


def test_scheduled_diagnosis_request_lands_on_diagnosis_skill() -> None:
    assert expected_skill_activation(
        "Schedule a weekly account health check."
    ) == ("adsagent-diagnosis",)
    assert expected_skill_activation(
        "给我的广告账户做一次深度诊断。"
    ) == ("adsagent-diagnosis",)
