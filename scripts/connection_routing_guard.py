"""Client-adapter connection routing guard; never dispatches MCP calls.

Connections come from the client's current selector catalog, not tool results.
An adapter must call prepare_call before dispatch and retain export_context
beside its workflow's approval/task handles. Installing skills does not install
this guard into a hosted client's executor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Any, Mapping, Sequence


HANDLE_FIELDS = frozenset({
    "approval_ref", "confirm_token", "task_ref", "mutation_ref", "upload_ref",
    "operation_ref", "validation_ref",
})


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RouteError("invalid_context")
    return value


class RouteError(ValueError):
    """A routing failure, with safe candidates for an account chooser."""

    def __init__(self, code: str, candidates: Sequence[Connection] = ()):
        super().__init__(code)
        self.code = code
        self.candidates = tuple(candidates)


@dataclass(frozen=True)
class Connection:
    resource: str
    link_id: str
    profile_id: str

    def __post_init__(self) -> None:
        for value in (self.resource, self.link_id, self.profile_id):
            _text(value)


def resolve_connection(
    resource: str,
    connections: Sequence[Connection],
    *,
    bound: Connection | None = None,
    requested_link_id: str | None = None,
    requested_profile_id: str | None = None,
    ownership_candidates: Sequence[Connection] | None = None,
    ownership_complete: bool = False,
) -> Connection:
    """Resolve a flow without a global current account or ordered fallback.

    Ownership candidates must be exact observed object owners from authorized
    reads, with complete coverage. Names, spend, role labels and permission
    failures alone are not ownership evidence.
    """
    _text(resource)
    available = tuple(c for c in connections if c.resource == resource)
    if len({c.link_id for c in available}) != len(available):
        raise RouteError("invalid_connection_catalog")
    if not available:
        raise RouteError("connection_unavailable")

    if bound is not None:
        if bound.resource != resource:
            raise RouteError("resource_mismatch")
        matches = tuple(c for c in available if c.link_id == bound.link_id)
        if not matches:
            raise RouteError("connection_unavailable")
        if matches[0] != bound:
            raise RouteError("profile_mismatch")
        candidates = (bound,)
    else:
        candidates = available

    if requested_link_id is not None:
        _text(requested_link_id)
        candidates = tuple(c for c in candidates if c.link_id == requested_link_id)
    if requested_profile_id is not None:
        _text(requested_profile_id)
        candidates = tuple(c for c in candidates if c.profile_id == requested_profile_id)
    if not candidates:
        raise RouteError("connection_mismatch")

    if ownership_candidates is not None:
        if not ownership_complete:
            raise RouteError("ownership_incomplete")
        owners = set(ownership_candidates)
        if any(c.resource != resource for c in owners):
            raise RouteError("resource_mismatch")
        if not owners.issubset(set(available)):
            raise RouteError("connection_unavailable")
        candidates = tuple(c for c in candidates if c in owners)
        if not candidates:
            raise RouteError("scope_not_found")

    if len(candidates) != 1:
        raise RouteError("connection_selection_required", candidates)
    return candidates[0]


@dataclass
class _Workflow:
    connection: Connection
    handles: dict[str, set[str]] = field(default_factory=dict)
    plan_digests: dict[str, str] = field(default_factory=dict)


class WorkflowRoutes:
    """Per-workflow bindings for concurrent tenants, with safe JSON snapshots."""

    def __init__(self) -> None:
        self._workflows: dict[str, _Workflow] = {}
        self._lock = RLock()

    def _get(self, workflow_id: str) -> _Workflow:
        _text(workflow_id)
        if workflow_id not in self._workflows:
            raise RouteError("workflow_context_required")
        return self._workflows[workflow_id]

    def bind(
        self, workflow_id: str, resource: str,
        connections: Sequence[Connection], **selection: Any,
    ) -> Connection:
        _text(workflow_id)
        with self._lock:
            existing = self._workflows.get(workflow_id)
            connection = resolve_connection(
                resource, connections,
                bound=existing.connection if existing else None, **selection,
            )
            if existing is None:
                self._workflows[workflow_id] = _Workflow(connection)
            return connection

    def remember(
        self, workflow_id: str, *, plan_digest: str | None = None,
        **handles: str,
    ) -> None:
        """Retain only advertised opaque handles, never raw business payloads."""
        if not handles.keys() <= HANDLE_FIELDS:
            raise RouteError("invalid_context")
        for value in handles.values():
            _text(value)
        if plan_digest is not None:
            _text(plan_digest)
            if "approval_ref" not in handles:
                raise RouteError("approval_context_required")
        with self._lock:
            workflow = self._get(workflow_id)
            if plan_digest is not None:
                approval = handles["approval_ref"]
                previous = workflow.plan_digests.get(approval)
                if previous is not None and previous != plan_digest:
                    raise RouteError("plan_digest_mismatch")
                workflow.plan_digests[approval] = plan_digest
            for kind, value in handles.items():
                workflow.handles.setdefault(kind, set()).add(value)

    def prepare_call(
        self, workflow_id: str, arguments: Mapping[str, Any],
        connections: Sequence[Connection], *, selector_supported: bool = True,
    ) -> dict[str, Any]:
        """Validate every dispatch, including reads, confirms and retries.

        For a native client without link_id, select the returned workflow
        context's connection in its transport instead; do not send new fields.
        This guard does not authorize an operation or a write retry.
        """
        with self._lock:
            workflow = self._get(workflow_id)
            resolve_connection(
                workflow.connection.resource, connections, bound=workflow.connection,
            )
            if "link_id" in arguments:
                if not selector_supported:
                    raise RouteError("selector_not_supported")
                if arguments["link_id"] != workflow.connection.link_id:
                    raise RouteError("connection_mismatch")
            for kind in HANDLE_FIELDS & arguments.keys():
                if _text(arguments[kind]) not in workflow.handles.get(kind, set()):
                    raise RouteError("handle_context_mismatch")
            approval = arguments.get("approval_ref")
            digest = workflow.plan_digests.get(approval) if approval else None
            if digest and "expected_plan_digest" in arguments:
                if arguments["expected_plan_digest"] != digest:
                    raise RouteError("plan_digest_mismatch")
            result = dict(arguments)
            if selector_supported:
                result["link_id"] = workflow.connection.link_id
            return result

    def workflow_for_handle(self, resource: str, kind: str, value: str) -> str:
        """Recover only an unambiguous locally retained handle association."""
        if kind not in HANDLE_FIELDS:
            raise RouteError("invalid_context")
        _text(value)
        with self._lock:
            candidates = [
                workflow_id for workflow_id, workflow in self._workflows.items()
                if workflow.connection.resource == resource
                and value in workflow.handles.get(kind, set())
            ]
            if len(candidates) != 1:
                raise RouteError("workflow_context_required")
            return candidates[0]

    def export_context(self, workflow_id: str) -> dict[str, Any]:
        with self._lock:
            workflow = self._get(workflow_id)
            return {
                "workflow_id": workflow_id,
                "connection": asdict(workflow.connection),
                "handles": {k: sorted(v) for k, v in workflow.handles.items()},
                "plan_digests": dict(workflow.plan_digests),
            }

    def restore_context(self, context: Mapping[str, Any]) -> None:
        """Restore adapter-owned state; current connection is checked on dispatch."""
        if set(context) != {"workflow_id", "connection", "handles", "plan_digests"}:
            raise RouteError("invalid_context")
        workflow_id = _text(context["workflow_id"])
        raw_connection = context["connection"]
        raw_handles = context["handles"]
        digests = context["plan_digests"]
        if not isinstance(raw_connection, dict) or set(raw_connection) != {
            "resource", "link_id", "profile_id",
        }:
            raise RouteError("invalid_context")
        if not isinstance(raw_handles, dict) or not raw_handles.keys() <= HANDLE_FIELDS:
            raise RouteError("invalid_context")
        if not isinstance(digests, dict):
            raise RouteError("invalid_context")
        handles = {}
        for kind, values in raw_handles.items():
            if not isinstance(values, list):
                raise RouteError("invalid_context")
            handles[kind] = {_text(v) for v in values}
        for approval, digest in digests.items():
            _text(approval)
            _text(digest)
            if approval not in handles.get("approval_ref", set()):
                raise RouteError("approval_context_required")
        workflow = _Workflow(Connection(**raw_connection), handles, dict(digests))
        with self._lock:
            if workflow_id in self._workflows and self._workflows[workflow_id] != workflow:
                raise RouteError("workflow_context_conflict")
            self._workflows[workflow_id] = workflow
