from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from scripts.connection_routing_guard import (
    Connection, RouteError, WorkflowRoutes, resolve_connection,
)
from skill_pack_mcp.pack import get_skill, list_skills


A = Connection("meta", "link-a", "tenant-a")
B = Connection("meta", "link-b", "tenant-b")
GOOGLE = Connection("google", "link-a", "tenant-a")
LINKS = [A, B, GOOGLE]


def test_two_tenants_concurrently_keep_prepare_confirm_task_and_retry_routes():
    routes = WorkflowRoutes()

    def lifecycle(connection: Connection):
        workflow = connection.profile_id
        routes.bind(workflow, "meta", LINKS, requested_link_id=connection.link_id)
        calls = [routes.prepare_call(workflow, {"request": {}}, LINKS)]
        routes.remember(workflow, approval_ref=f"approval-{workflow}", plan_digest="digest")
        calls.append(routes.prepare_call(workflow, {
            "approval_ref": f"approval-{workflow}", "expected_plan_digest": "digest",
        }, LINKS))
        routes.remember(workflow, task_ref=f"task-{workflow}")
        calls.append(routes.prepare_call(workflow, {"task_ref": f"task-{workflow}"}, LINKS))
        # A permitted retry retains the original flow; the guard never dispatches.
        calls.append(routes.prepare_call(workflow, {"task_ref": f"task-{workflow}"}, LINKS))
        return connection, calls

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lifecycle, [A, B]))
    for connection, calls in results:
        assert {call["link_id"] for call in calls} == {connection.link_id}


def test_original_wrong_tenant_confirmation_is_rejected_before_dispatch():
    routes = WorkflowRoutes()
    routes.bind("launch", "meta", LINKS, requested_link_id=A.link_id)
    routes.remember("launch", approval_ref="approval-a", plan_digest="digest-a")
    with pytest.raises(RouteError, match="connection_mismatch"):
        routes.prepare_call("launch", {
            "link_id": B.link_id, "approval_ref": "approval-a",
            "expected_plan_digest": "digest-a",
        }, LINKS)
    with pytest.raises(RouteError, match="connection_mismatch"):
        routes.bind("launch", "meta", LINKS, requested_link_id=B.link_id)


def test_automatic_routing_uses_explicit_choice_exact_ownership_or_sole_link():
    assert resolve_connection("meta", LINKS, requested_profile_id=B.profile_id) == B
    for catalog in (LINKS, list(reversed(LINKS))):
        assert resolve_connection("meta", catalog, ownership_candidates=[A],
                                  ownership_complete=True) == A
    assert resolve_connection("meta", [B, GOOGLE]) == B
    assert resolve_connection("google", LINKS) == GOOGLE


@pytest.mark.parametrize("selection,code", [
    ({}, "connection_selection_required"),
    ({"ownership_candidates": [A]}, "ownership_incomplete"),
    ({"ownership_candidates": [A, B], "ownership_complete": True},
     "connection_selection_required"),
    ({"ownership_candidates": [], "ownership_complete": True}, "scope_not_found"),
    ({"ownership_candidates": [B], "ownership_complete": True,
      "requested_link_id": A.link_id}, "scope_not_found"),
])
def test_ambiguous_incomplete_shared_or_conflicting_scope_is_not_guessed(selection, code):
    with pytest.raises(RouteError, match=code):
        resolve_connection("meta", LINKS, **selection)


def test_same_profile_on_multiple_links_still_needs_a_connection_choice():
    other_link = Connection("meta", "link-a-second", A.profile_id)
    with pytest.raises(RouteError, match="connection_selection_required"):
        resolve_connection("meta", [A, other_link], requested_profile_id=A.profile_id)
    with pytest.raises(RouteError, match="invalid_connection_catalog"):
        resolve_connection("meta", [A, Connection("meta", A.link_id, B.profile_id)])


def test_bound_link_loss_or_profile_change_never_falls_back():
    routes = WorkflowRoutes()
    routes.bind("launch", "meta", LINKS, requested_link_id=A.link_id)
    with pytest.raises(RouteError, match="connection_unavailable"):
        routes.prepare_call("launch", {}, [B, Connection("meta", "new-link", A.profile_id)])
    with pytest.raises(RouteError, match="profile_mismatch"):
        routes.prepare_call("launch", {}, [Connection("meta", A.link_id, B.profile_id)])
    # Refreshed credentials do not change the selector/profile metadata.
    assert routes.prepare_call("launch", {}, [A])["link_id"] == A.link_id


def test_handles_and_plan_digests_cannot_be_mixed_between_flows():
    routes = WorkflowRoutes()
    routes.bind("a", "meta", LINKS, requested_link_id=A.link_id)
    routes.bind("b", "meta", LINKS, requested_link_id=B.link_id)
    routes.remember("a", approval_ref="approval-a", task_ref="task-a", plan_digest="digest-a")
    routes.remember("b", approval_ref="approval-b", task_ref="task-b", plan_digest="digest-b")
    for handle in ({"approval_ref": "approval-a"}, {"task_ref": "task-a"}):
        with pytest.raises(RouteError, match="handle_context_mismatch"):
            routes.prepare_call("b", handle, LINKS)
    with pytest.raises(RouteError, match="plan_digest_mismatch"):
        routes.prepare_call("a", {"approval_ref": "approval-a",
                                  "expected_plan_digest": "digest-b"}, LINKS)
    with pytest.raises(RouteError, match="plan_digest_mismatch"):
        routes.remember("a", approval_ref="approval-a", plan_digest="new-digest")


def test_resumed_workflow_restores_connection_handles_and_digest_without_payloads():
    original = WorkflowRoutes()
    original.bind("launch", "meta", LINKS, requested_link_id=A.link_id)
    arguments = {"request": {"campaign_name": "example"}}
    original.prepare_call("launch", arguments, LINKS)
    assert "link_id" not in arguments
    original.remember("launch", approval_ref="approval-a", task_ref="task-a", plan_digest="digest-a")
    context = json.loads(json.dumps(original.export_context("launch")))
    assert "example" not in json.dumps(context)
    resumed = WorkflowRoutes()
    resumed.restore_context(context)
    assert resumed.workflow_for_handle("meta", "task_ref", "task-a") == "launch"
    assert resumed.prepare_call("launch", {"task_ref": "task-a"}, LINKS)["link_id"] == A.link_id
    assert resumed.prepare_call("launch", {"approval_ref": "approval-a",
                                          "expected_plan_digest": "digest-a"}, LINKS)["link_id"] == A.link_id
    with pytest.raises(RouteError, match="resource_mismatch"):
        resumed.bind("launch", "google", LINKS)


def test_missing_or_colliding_handle_context_does_not_probe_tenants():
    routes = WorkflowRoutes()
    with pytest.raises(RouteError, match="workflow_context_required"):
        routes.prepare_call("missing", {}, LINKS)
    for workflow, connection in [("a", A), ("b", B)]:
        routes.bind(workflow, "meta", LINKS, requested_link_id=connection.link_id)
        routes.remember(workflow, task_ref="same-opaque-handle")
    with pytest.raises(RouteError, match="workflow_context_required"):
        routes.workflow_for_handle("meta", "task_ref", "same-opaque-handle")
    with pytest.raises(RouteError, match="workflow_context_required"):
        routes.workflow_for_handle("meta", "task_ref", "unknown")
    assert routes.prepare_call("b", {"task_ref": "same-opaque-handle"}, LINKS)["link_id"] == B.link_id


def test_native_transport_does_not_receive_undeclared_link_argument():
    routes = WorkflowRoutes()
    routes.bind("native", "meta", [A])
    assert routes.prepare_call("native", {}, [A], selector_supported=False) == {}
    assert routes.export_context("native")["connection"]["link_id"] == A.link_id
    with pytest.raises(RouteError, match="selector_not_supported"):
        routes.prepare_call("native", {"link_id": A.link_id}, [A], selector_supported=False)


def test_replacement_approval_and_task_keep_original_link():
    routes = WorkflowRoutes()
    routes.bind("launch", "meta", LINKS, requested_link_id=A.link_id)
    routes.remember("launch", approval_ref="expired", plan_digest="old-digest")
    assert routes.prepare_call("launch", {"request": {}}, LINKS)["link_id"] == A.link_id
    routes.remember("launch", approval_ref="replacement", plan_digest="new-digest")
    assert routes.prepare_call("launch", {"approval_ref": "replacement",
                                         "expected_plan_digest": "new-digest"}, LINKS)["link_id"] == A.link_id


def test_every_installed_skill_can_load_its_local_routing_contract():
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "skills/connection-routing.md").read_text()
    for skill in list_skills(root)["skills"]:
        payload = get_skill(root, skill["id"], references=["connection-routing.md"])
        assert payload["files"][1]["content"] == canonical
