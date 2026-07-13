---
name: agent-scheduled-tasks
description: Use when the user asks an agent to create, update, verify, debug, pause, or delete a scheduled task, automation, cron job, monitor, reminder, or heartbeat, especially when execution proof and safe retries matter.
---

# Agent Scheduled Tasks

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

For writes, use prepare, recorded authorization, confirm once, recover the `mutation_ref` through `operations_get`, then perform the advertised read-back. Stop when any capability, freshness, coverage, approval, receipt, or verification gate is missing. Never auto-enable permissions or retry an uncertain write.

## Report

Return task kind, timezone/cadence, destination, read-back state, next run, run-now result, execution evidence, and unresolved gaps. Do not claim more than the scheduler and downstream receipts prove.
