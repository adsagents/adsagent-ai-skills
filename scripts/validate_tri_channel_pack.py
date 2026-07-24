#!/usr/bin/env python3
"""Validate the AdsAgent tri-channel skill pack contract."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.34"

REQUIRED_SKILLS = {
    "adsagent-router",
    "adsagent-setup",
    "adsagent-notifications",
    "adsagent-reliability",
    "agent-scheduled-tasks",
    "meta-insights",
    "meta-copy",
    "google-ads-insights",
    "tiktok-insights",
}
MAX_SKILL_WORDS = 500

REQUIRED_REPO_TERMS = [
    "google_ads_insights_overview_batch",
    "insights_query_batch_overview",
    "mcp_concurrency_limited",
    "Retry-After",
    "connections_create_intent",
    "https://adsagent.md/mcp/v2",
    "legacy fallback",
    "error.data",
    "meta.complete=true",
    "missing scopes",
    "artifact",
    "setup_get_status.capabilities",
    "insights_query_consistent",
    "freshness_kind=age_only",
    "mutation_ref",
    "config_verified_live",
    "overview_get_live_configs",
    "next_action",
    "does not verify delivery configuration",
    "operations_get_context",
    "task_ref",
    "client_skill_pack",
    "notify_only",
    "No automatic update",
    "update-reminder-v1.json",
    "top-level complete=true",
    "query_contract_version=1",
    "adsagent_agent_methods_v1",
    "15 minutes",
    "single-use",
    "expires_at",
    "confirm_token_invalid",
    "no_create_permission",
    "/dashboard/assets/fb-users",
    "response_mode=compact",
    "adsagent_query_invalid",
    "page_size<=50",
    "allowlisted `filters`",
    "conditions are AND",
    "spend_gt",
    "campaign_id",
    "campaign_name",
    "Do not prefetch or fan out parents",
    "preserve each `ad_id`",
    "data.meta.has_more=true",
    "result.meta.source_observed_at",
    "result.query_contract.coverage.source_observed_at",
    "never rerun page 1",
    "Exact Ad-name deduplication",
    "language classification",
    "configured_status",
    "effective_status",
    "adsagent://guide/metadata-contract",
    "metadata_contract_version=1",
    "target_configured_status",
    "money_unit",
    "budget_level",
    "bid_strategy",
    "DISAPPROVED",
    "PENDING_REVIEW",
    "daily_budget",
    "lifetime_budget",
    "billing_event",
    "conversion_event",
    "insights_export_csv",
    "result.artifact",
    "download_url",
    "byte-for-byte",
    "Never redact",
    "artifact_status=expired",
    "scope_unavailable",
    "support_ref",
    "snapshot_expired",
    "source_anchor",
    "result.source_snapshot",
    "opaque continuation",
    "single-use continuation",
    "login-customer route",
    "Never send Meta `min_as_of` to Google or TikTok",
    "retry_after_seconds",
    "not authorization",
    "do not infer another workspace/token",
    "retry the identical bounded read once",
    "Never enable or modify customer permissions automatically",
    "grouped_plan",
    "creation_contract_version=3",
    "request_mode",
    "adsagent://guide/creation-contract",
    "adsagent://guide/name-contract",
    "adsagent_request_incomplete",
    "invalid_fields",
    "rerun prepare once",
    "settings_source_ad_id",
    "cgb_confirm_*",
    "support@adsagent.md",
    "https://github.com/adsagents/adsagent-ai-skills",
    "result.failures.items",
    "failures.unclassified_count",
    "mcp_meta_quota_deferred",
    "request_sent=false",
    "safe_to_retry=true",
    "operator_review_required=false",
    "completed_mutations",
    "not_sent_mutations",
    "remaining_mutations",
    "safe_resume_from",
    "support_refs",
    "append_mode=append-campaign",
    "target_campaign_id",
    "append_mode=append-adset",
    "target_adset_id",
    "append_mode=existing",
    "existing_campaign_id",
    "existing_adset_id",
    "inherits the existing parent budget",
    "fresh explicit approval",
]

FORBIDDEN_REPO_TERMS = [
    "Meta" + "-only",
    "meta" + "-only",
    "only " + "Meta",
    "Meta " + "package",
]

ROUTER_TERMS = [
    "Meta / Facebook / FB / Page / pixel / campaign copy",
    "Google Ads / MCC / customer / search / PMax",
    "TikTok / advertiser / TT",
    "429 / 503 / Retry-After / concurrency / stale session",
    "setup / connect / OAuth / MCP token",
    "scheduled task / automation / cron / reminder",
    "notification / webhook / email / Feishu / Telegram",
    "setup_get_status.capabilities",
    "capability",
    "Multiple distinct source Ads",
    "grouped_plan",
]

SCHEDULED_TASK_TERMS = [
    "reminder_or_heartbeat",
    "auditable_execution",
    "consequential_execution",
    "scheduler_kind=heartbeat",
    "execution_history_available=false",
    "Creation is not execution proof",
    "IANA timezone",
    "destination",
    "run-now",
    "read back",
    "run ID",
    "terminal status",
    "append-only run log",
    "setup_get_status.capabilities",
    "complete=true",
    "mutation_ref",
    "operations_get",
    "Never auto-enable permissions",
]

META_TERMS = [
    "insights_query_overview",
    "insights_query_batch_overview",
    "insights_query_consistent",
    "consistency=require_fresh",
    "freshness_kind=age_only",
    "not mutation coverage",
    "verification_pending",
    "data_not_fresh",
    "mutation_ref",
    "after_mutation_ref",
    "config_verified_live",
    "overview_get_live_configs",
    "next_action",
    "post-write metrics",
    "does not verify delivery configuration",
    "operations_get_context",
    "tasks_get_status(task_ref",
    "adsagent_query_invalid",
    "page_size<=50",
    "allowlisted `filters`",
    "All conditions are AND",
    "spend_gt",
    "campaign_id",
    "campaign_name",
    "Do not prefetch or fan out parents",
    "preserve each `ad_id`",
    "data.meta.has_more=true",
    "result.meta.source_observed_at",
    "result.query_contract.coverage.source_observed_at",
    "never rerun page 1",
    "Exact Ad-name deduplication",
    "language classification",
    "business grouping",
    "configured_status",
    "effective_status",
    "adsagent://guide/metadata-contract",
    "money_unit=major",
    "budget_level",
    "bid_strategy",
    "DISAPPROVED",
    "PENDING_REVIEW",
    "daily_budget",
    "lifetime_budget",
    "objective",
    "optimization_goal",
    "billing_event",
    "conversion_event",
    "pixel_id",
    "app_id",
    "insights_export_csv",
    "result.artifact",
    "download_url",
    "byte-for-byte",
    "Never redact",
    "artifact_status=expired",
    "scope_unavailable",
    "do not infer another workspace/token",
    "retry the identical bounded read once",
]

GOOGLE_TERMS = [
    "setup_get_status",
    "agent_method_profile.profile_id=adsagent_agent_methods_v1",
    "insights_query_consistent",
    "query_contract_version=1",
    "consistency=cached",
    "max_scopes",
    "top-level `complete=true`",
    "google_ads_accounts_list",
    "enabled",
    "non-manager",
    "google_ads_insights_overview_query",
    "google_ads_insights_overview_batch",
    "client-side fan-out",
    "summary/total",
    "mcp_concurrency_limited",
    "Retry-After + jitter",
    "read-only ledger",
    "as_of",
    "does not advertise require_fresh",
    "snapshot_expired",
    "restart at page 1",
    "opaque continuation",
    "login-customer route",
    "page size",
    "Never add Meta `min_as_of`",
    "does not add a public MCP write capability",
]

TIKTOK_TERMS = [
    "setup_get_status",
    "agent_method_profile.profile_id=adsagent_agent_methods_v1",
    "insights_query_consistent",
    "query_contract_version=1",
    "insights_query_contract.consistency_modes",
    "date_range_mode=since_launch",
    "top-level `complete=true`",
    "next_action",
    "task_ref",
    "mutation_receipts=true",
    "delivery_prepare_tool",
    "delivery_confirm_tool",
    "operation_get_tool",
    "tenant",
    "advertiser",
    "insights_query_overview",
    "insights_query_batch_overview",
    "fan-out",
    "server summary/total",
    "429",
    "503",
    "Retry-After",
    "age-only",
    "immediate write success is not mutation verification",
    "config_verified_live",
    "dependency_unavailable",
    "retry_after_seconds",
    "source_anchor",
    "result.source_snapshot",
    "never rerun page 1",
    "opaque continuation",
    "single-use",
    "authorization route",
    "page size",
    "Never add Meta `min_as_of`",
    "readiness.create_eligible=true",
    "verification_pending",
    "creatives_reconcile",
    "1..20",
    "never client-side fan out",
    "readiness.reason_code",
    "readiness.retryable",
    "readiness.next_action",
    "campaigns_quick_create",
    "append_mode=append-campaign",
    "target_campaign_id",
    "append_mode=append-adgroup",
    "target_adgroup_id",
    "operations_get",
    "reconnect the MCP transport",
]

META_COPY_TERMS = [
    'copy_mode="deep"',
    "partnership_fresh_copy_unsupported",
    "source_creative_type",
    "post_linkage",
    "do not auto-retry",
    "grouped_plan",
    "creation_contract_version=3",
    "campaign_name",
    "adset_name",
    "ad_name",
    "adsagent_request_incomplete",
    "invalid_fields",
    "source_ad_id",
    "settings_source_ad_id",
    "cgb_confirm_*",
    "paused-by-default",
    "adsagent://guide/metadata-contract",
    "target_configured_status",
    "current_configured_status",
    "mcp_meta_quota_deferred",
    "request_sent=false",
    "safe_to_retry=true",
    "operator_review_required=false",
    "append_mode=append-campaign",
    "target_campaign_id",
    "append_mode=append-adset",
    "target_adset_id",
    "append_mode=existing",
    "existing_campaign_id",
    "existing_adset_id",
    "product_ref",
    "inherits the existing parent budget",
    "fresh explicit approval",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} missing YAML frontmatter")
    try:
        _, frontmatter, _ = text.split("---\n", 2)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has malformed YAML frontmatter")
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    for key in ("name", "description"):
        if not data.get(key):
            fail(f"{path.relative_to(ROOT)} missing frontmatter field {key}")
    unexpected = sorted(set(data) - {"name", "description"})
    if unexpected:
        fail(
            f"{path.relative_to(ROOT)} has unsupported frontmatter fields: "
            f"{', '.join(unexpected)}"
        )
    if len(frontmatter.encode("utf-8")) > 1024:
        fail(f"{path.relative_to(ROOT)} frontmatter exceeds 1024 bytes")
    if re.fullmatch(r"[a-z0-9-]+", data["name"]) is None:
        fail(f"{path.relative_to(ROOT)} has invalid skill name")
    if not data["description"].startswith("Use when"):
        fail(f"{path.relative_to(ROOT)} description must start with 'Use when'")
    return data


def assert_terms(label: str, text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term not in text]
    if missing:
        fail(f"{label} missing terms: {', '.join(missing)}")


def assert_forbidden_terms_absent(label: str, text: str, terms: list[str]) -> None:
    matches = [term for term in terms if term in text]
    if matches:
        fail(f"{label} has forbidden single-channel wording: {', '.join(matches)}")


def validate_retry_parser_reference(source: str) -> None:
    """Validate the documented parser structurally without executing Markdown."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        fail(f"retry-parser.md has invalid Python: {exc.msg}")

    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        fail("retry-parser.md must contain exactly one function")
    function = tree.body[0]
    if function.name != "retry_after_seconds" or function.decorator_list:
        fail("retry-parser.md has an unexpected function definition")
    if [arg.arg for arg in function.args.args] != ["payload", "headers"]:
        fail("retry-parser.md has an unexpected function signature")

    named_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    if not named_calls <= {"float", "isinstance", "str"}:
        fail("retry-parser.md calls an unexpected function")

    attribute_calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    if not attribute_calls <= {"get", "items", "lower"}:
        fail("retry-parser.md calls an unexpected method")
    forbidden_nodes = (
        ast.AsyncFunctionDef,
        ast.Await,
        ast.ClassDef,
        ast.Global,
        ast.Import,
        ast.ImportFrom,
        ast.Lambda,
        ast.Nonlocal,
        ast.With,
        ast.Yield,
        ast.YieldFrom,
    )
    if any(isinstance(node, forbidden_nodes) for node in ast.walk(tree)):
        fail("retry-parser.md contains a forbidden construct")

    string_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    required_literals = {
        "data",
        "error",
        "retry-after",
        "retry_after",
        "retry_after_seconds",
    }
    if not required_literals <= string_literals:
        fail("retry-parser.md is missing a required response field")

    if not any(
        isinstance(node, ast.Return)
        and isinstance(node.value, ast.Constant)
        and node.value.value is None
        for node in ast.walk(function)
    ):
        fail("retry-parser.md must return None when no delay is available")


def main() -> None:
    version = read("VERSION").strip()
    if version != VERSION:
        fail(f"VERSION is {version}, expected {VERSION}")

    plugin = json.loads(read(".claude-plugin/plugin.json"))
    marketplace = json.loads(read(".claude-plugin/marketplace.json"))
    if plugin.get("version") != VERSION:
        fail(f"plugin.json version is {plugin.get('version')}, expected {VERSION}")
    if marketplace.get("metadata", {}).get("version") != VERSION:
        fail("marketplace metadata version mismatch")
    marketplace_plugins = marketplace.get("plugins", [])
    if not marketplace_plugins or marketplace_plugins[0].get("version") != VERSION:
        fail("marketplace plugin version mismatch")

    release_manifest = json.loads(read("release-manifest.json"))
    expected_release_manifest = {
        "schema_version": 1,
        "package": "adsagent-ai-skills",
        "repository": "adsagents/adsagent-ai-skills",
        "version": VERSION,
        "tag": f"v{VERSION}",
        "release_url": (
            "https://github.com/adsagents/adsagent-ai-skills/releases/tag/"
            f"v{VERSION}"
        ),
    }
    if release_manifest != expected_release_manifest:
        fail("release-manifest.json does not match the public release identity")

    reminder_helper = ROOT / "scripts" / "update_reminder.py"
    if not reminder_helper.exists():
        fail("missing scripts/update_reminder.py")
    if not (ROOT / "NOTICE.md").exists():
        fail("missing NOTICE.md")

    listed_skills = {Path(entry).name for entry in plugin.get("skills", [])}
    missing_listed = sorted(REQUIRED_SKILLS - listed_skills)
    if missing_listed:
        fail(f"plugin.json missing skills: {', '.join(missing_listed)}")

    for skill in sorted(REQUIRED_SKILLS):
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")
        frontmatter = parse_skill_frontmatter(path)
        if frontmatter["name"] != skill:
            fail(f"{path.relative_to(ROOT)} name is {frontmatter['name']}, expected {skill}")
        word_count = len(path.read_text(encoding="utf-8").split())
        if word_count > MAX_SKILL_WORDS:
            fail(
                f"{path.relative_to(ROOT)} has {word_count} words; "
                f"maximum is {MAX_SKILL_WORDS}"
            )

    assert_terms("adsagent-router", read("skills/adsagent-router/SKILL.md"), ROUTER_TERMS)
    assert_terms(
        "agent-scheduled-tasks",
        read("skills/agent-scheduled-tasks/SKILL.md"),
        SCHEDULED_TASK_TERMS,
    )
    assert_terms("meta-insights", read("skills/meta-insights/SKILL.md"), META_TERMS)
    assert_terms("meta-copy", read("skills/meta-copy/SKILL.md"), META_COPY_TERMS)
    assert_terms("google-ads-insights", read("skills/google-ads-insights/SKILL.md"), GOOGLE_TERMS)
    assert_terms("tiktok-insights", read("skills/tiktok-insights/SKILL.md"), TIKTOK_TERMS)

    setup = read("skills/adsagent-setup/SKILL.md")
    assert_terms(
        "adsagent-setup",
        setup,
        [
            "https://adsagent.md/mcp",
            "https://adsagent.md/mcp/v2",
            "legacy fallback",
            "https://google.adsagent.md/mcp",
            "https://tiktok.adsagent.md/mcp",
            "same AdsAgent bearer / OAuth identity",
            "connections_create_intent(channel=",
            "central-auth identity",
            "Do not use email fallback",
        ],
    )

    notifications = read("skills/adsagent-notifications/SKILL.md")
    assert_terms(
        "adsagent-notifications",
        notifications,
        [
            "notifications_integrations_list",
            "operator-scoped",
            "OAuth Safe Mode",
            "do not solicit credentials in chat",
            "notifications_integration_prepare",
            "notifications_integration_confirm",
            "tasks_get_status(task_ref)",
            "explicit user approval",
            "test_channel",
            "one real external message",
            "single-use",
            "Never replay",
            "notifications_integrations_list",
            "invalid_fields",
            "fresh approval",
            "support_ref",
            "Never create, enable, disable, or modify customer FB User permissions",
            "exact eligible route",
            "provider acceptance",
        ],
    )

    reliability = read("skills/adsagent-reliability/SKILL.md")
    assert_terms(
        "adsagent-reliability",
        reliability,
        [
            "mcp_concurrency_limited",
            "503 dependency unavailable",
            "429 concurrency",
            "server-side batch",
            "agent_method_profile.profile_id=adsagent_agent_methods_v1",
            "insights_query_consistent",
            "query_contract_version=1",
            "top-level `complete=true`",
            "google_ads_insights_overview_batch",
            "insights_query_batch_overview",
            "error.data",
            "meta.complete=true",
            "artifact",
            "result.artifact",
            "download_url",
            "byte-for-byte",
            "task_ref",
            "tasks_get_status",
            "operations_get_context",
            "snapshot_expired",
            "opaque continuation",
            "Never move Meta `min_as_of` into Google or TikTok requests",
            "retry_after_seconds",
            "identical bounded read once",
            "mcp_meta_quota_deferred",
            "request_sent=false",
            "safe_to_retry=true",
            "operator_review_required=false",
            "completed_mutations",
            "not_sent_mutations",
            "remaining_mutations",
            "safe_resume_from",
            "support_refs",
        ],
    )

    retry_reference = read("skills/adsagent-reliability/retry-parser.md")
    try:
        code = retry_reference.split("```python\n", 1)[1].split("\n```", 1)[0]
    except IndexError:
        fail("retry-parser.md missing Python block")
    validate_retry_parser_reference(code)

    repo_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in list((ROOT / "skills").glob("*/SKILL.md"))
        + [ROOT / "README.md", ROOT / "docs/examples.md", ROOT / "docs/output-contract.md"]
    )
    assert_terms("repository docs", repo_text, REQUIRED_REPO_TERMS)
    assert_forbidden_terms_absent("repository docs", repo_text, FORBIDDEN_REPO_TERMS)

    readme = read("README.md")
    assert_terms(
        "README",
        readme,
        ["AdsAgent tri-channel", "Meta", "Google", "TikTok", "mcp_fanout_detected"],
    )
    stale_readme_terms = ["five skills", "five directories"]
    readme_lower = readme.lower()
    stale_matches = [term for term in stale_readme_terms if term in readme_lower]
    if stale_matches:
        fail(f"README has stale skill-count wording: {', '.join(stale_matches)}")
    if readme.count("Meta") > 3 and "Google" not in readme and "TikTok" not in readme:
        fail("README still reads as Meta scoped only")
    for stale_term in (
        "private skill pack",
        "private github staging repo",
        "safe to publish later",
        "git@github.com:adsagents/adsagent-ai-skills.git",
    ):
        if stale_term in readme_lower:
            fail(f"README contains stale public-release wording: {stale_term}")

    output_contract = read("docs/output-contract.md")
    assert_terms(
        "output contract",
        output_contract,
        [
            "freshness_kind",
            "age_only",
            "mutation_ref",
            "config_verified_live",
            "overview_get_live_configs",
            "next_action",
            "verification_pending",
            "data_not_fresh",
            "task_ref",
        ],
    )

    print("PASS: tri-channel skill pack contract satisfied")


if __name__ == "__main__":
    main()
