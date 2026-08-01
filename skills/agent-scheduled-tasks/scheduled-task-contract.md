# Agent Scheduled Task Contract

Design a deterministic job and report what the scheduler actually proves.

## Classify First

- `reminder_or_heartbeat`: wakes or notifies; it does not prove tool execution.
- `auditable_execution`: runs tools and produces a bounded result plus execution evidence.
- `consequential_execution`: may change external state and needs authorization, idempotency, receipts, and read-back.

Creation is not execution proof. If the platform only supports reminders, label it `scheduler_kind=heartbeat` and `execution_history_available=false`.

## Define The Contract

Before creating, determine:

- task name and `rule_id_and_version`;
- IANA timezone, cadence, start boundary, and enabled state;
- destination: existing thread, new task, channel, or artifact;
- stable scope and allowed tools;
- expected output, append-only run log location, and failure target;
- bounded retry policy and stop conditions.

Choose a cadence no faster than source freshness or useful decision frequency. Keep worst-case runtime plus bounded retry below the interval, prevent overlapping runs, and use stable jitter away from shared clock boundaries when the scheduler supports it.

Ask only for missing choices that materially change behavior. Never guess a timezone, account, destination, or permission.

Write the scheduled prompt as a deterministic entrypoint: state the goal, scope, ordered steps, evidence requirements, retry budget, forbidden actions, and final report shape. Do not put bearer tokens, cookies, credentials, raw customer payloads, or hidden diagnostics in the prompt or run log.

## Create Or Change

1. Use the platform's scheduler interface; do not invent unsupported fields.
2. Preserve scheduler enum casing; do not normalize status values.
3. Create or update once, then read back timezone, cadence, destination, status, and prompt version.
4. Run the same entrypoint with run-now when supported.
5. Record the run ID, timestamps, terminal status, result or artifact reference, and safe errors.
6. On update, show the bounded configuration diff and superseded rule version. On pause or delete, read back actual state and report any in-flight run.

Do not claim success from a saved schedule, notification, nearby data pull, or chat response. Require scheduler evidence and, for tool jobs, downstream evidence. A useful execution record includes scheduled/start/finish times, stable scope, downstream task refs, evaluated and matched counts, outcome, and append-only run log reference.

## AdsAgent Jobs

Read `setup_get_status.capabilities` once per run. Use stable public refs and server-side batch; never fan out. Trust an Insights decision only when the relevant result reports `complete=true`; poll a returned `task_ref` to terminal before reevaluating.

For a Meta rule or decision with explicit candidate IDs, call
`overview_get_live_configs` with up to 50 exact candidate entities in one
request. Match every result by `entity_type` and `entity_id`, require complete
one-to-one live coverage, and exclude any candidate whose
`configured_status` is not `ACTIVE`. If a candidate is missing, duplicated, or
incomplete, live status coverage is incomplete: stop before consequential
evaluation or mutation. Never infer an Ad's state from parent status, and keep
a reported manual change outside the candidate ID set separate until an exact
ID matches. A local selector miss may still permit a clearly labeled
metrics-only read, but it cannot prove candidate delivery state.

For writes, the matching prepare tool is the live preflight and does not mutate
the provider. Use recorded authorization, confirm once, and consume inline
`verification_result` first. Only while verification remains pending, follow
the advertised read-back. If the profile's canonical `operation_get_tool` is
absent from the client-local catalog, use its `native_operation_fallback`
(`operations_get_context` for Meta) scoped to the same known entity and run.
A selector miss before any mutation must not disable read-only schedule evaluation.
If an applied write cannot be recovered, preserve its `task_ref`/`mutation_ref`
receipt and keep subsequent runs read-only until it is reconciled; never replay
it. Stop when any capability, freshness, coverage, approval, receipt, or
verification gate required by the current phase is missing.
Never auto-enable permissions or retry an uncertain write.

## Report

Return task kind, timezone/cadence, destination, read-back state, next run, run-now result, execution evidence, and unresolved gaps. Do not claim more than the scheduler and downstream receipts prove.
