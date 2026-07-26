---
name: agent-scheduled-tasks
description: Use when creating, changing, debugging, or proving an agent-owned scheduled task, automation, cron, reminder, or heartbeat.
---

# Agent Scheduled Tasks

1. Classify the job as reminder/heartbeat, auditable execution, or
   consequential execution.
2. Resolve timezone, cadence, destination, stable scope, allowed tools,
   evidence, retry budget, and stop conditions before creating it.
3. Use the actual scheduler interface once, then read back its stored contract.
4. Run now only when supported and record the scheduler plus downstream
   evidence separately.
5. Never put credentials in the prompt, guess permissions, or treat schedule
   creation as execution proof.

Read [scheduled-task-contract.md](scheduled-task-contract.md) only when
designing, creating, updating, debugging, pausing, deleting, or proving a
scheduled task.
