# Deep Diagnosis Contract

Deep diagnosis （深度诊断） is one account-wide check across the connected
channels. The `diagnosis_*` tools have the same names and behavior on the
Meta, Google Ads, and TikTok connectors; use one connected connector for
status, run, and report reads. The server returns structured findings.
Writing the explanation for the user is your job in the conversation.

## When to call

- Only when the user asks, or clearly expresses the intent:
  诊断 / 体检 / 审计 / 账户检查, or diagnosis / audit / account health
  check in English.
- Never run a diagnosis on a schedule, automatically, or as a background
  habit. Do not create a scheduled task for it, do not add it to routine
  reporting, and do not run one just because a window is about to reset.
  If the user asks for a recurring automatic diagnosis, explain that each
  run is user-triggered and offer to run one now.
- If the `diagnosis_*` tools are not advertised on the connector, deep
  diagnosis is not available for that account yet. Say so plainly. Do not
  simulate a diagnosis or invent a score from ordinary insights reads.

## Run flow

1. Call `diagnosis_get_status` first. It is read-only and shows whether
   the plan includes deep diagnosis, how many runs are left in the
   current window, and the latest report. If the user only wants earlier
   findings, read that report instead of running again.
2. Before running, tell the user that a run uses this window's one run
   (Pro: one per month; Max: one per week) and get explicit user
   confirmation. Then call `diagnosis_run` with
   `acknowledge_credit_use=true`. A `needs_confirmation` result means the
   confirmation was missing: ask the user, and resubmit only after they
   confirm. Never set the acknowledgement on the user's behalf.
3. Read the result with `diagnosis_get_report` (the latest report by
   default, or one `report_ref`). Use `diagnosis_list_reports` for
   history. Both are read-only and do not use a run. When the user asks
   how things changed, compare two reports only on values each report
   actually returns.
4. Runs are counted per billing account, not per connector. Switching
   connectors never creates another run.

## Reading a report

- Build the narrative from what the report returns: dimension states,
  the 0-100 overall `score`, the `score_drivers` naming which dimensions
  lowered the score and why, finding evidence, and the ranked
  recommendations. Do not invent numbers, causes, or expected savings
  that are not in the returned evidence, and do not restate the score as
  a grade or ranking the report does not give.
- Dimension states are `ok`, `warning`, `critical`, and `unknown`.
  An `unknown` dimension is not healthy: it could not be assessed.
  Present it as not assessed, never as a pass, and do not let the user
  read silence as safety. A `null` score means there was not enough
  assessed data for a score; present it as unavailable, not as zero.
- When coverage is `partial`, some data was unavailable, so conclusions
  cover only the assessed parts. Say that plainly (for example
  部分数据不完整） without speculating about internal reasons.
- Cite the report's `data_as_of` time and window. A report describes the
  state at that time; do not present its evidence as live state.

## Acting on recommendations

- For a recommendation marked actionable, call
  `diagnosis_prepare_recommendation` with its `report_ref` and
  `recommendation_ref` on the same channel connector as the
  recommendation's channel. This creates the same kind of approval
  draft as that channel's own prepare tools; then follow the normal
  approval flow (`adsagent-approvals`): show the summary, wait for
  explicit user approval, then confirm with the named tool.
- A prepare changes nothing by itself. Never claim a change was made
  until the confirm step has completed and been read back.
- `recommendation_other_channel`: the recommendation belongs to another
  channel. Switch to that channel's connector and prepare it there with
  the same references; do not force it through the current connector.
- `recommendation_stale`: the underlying state has changed since the
  report. Re-check the current state with the channel's read tools, or
  offer a new diagnosis when a run is available. Do not reuse the stale
  draft or prepare around the refusal.
- `recommendation_not_actionable`: the recommendation is advice only and
  has no prepare path. Present the manual steps as given; do not
  substitute a different write tool for it.

## When a run cannot start

Explain the result and stop; do not retry in a loop and do not rerun
`diagnosis_run` hoping for a different answer.

- `diagnosis_not_in_plan`: the current plan does not include deep
  diagnosis (it is part of Pro and Max). Explain that and offer the
  latest existing report, if any.
- `diagnosis_runs_exhausted`: this window's run is already used. Tell
  the user when the next window starts, from the window in
  `diagnosis_get_status`, and offer the latest report.
- `diagnosis_in_progress`: a run is already going. Wait for it and read
  its report; do not start a second run.
- `billing_read_only`: new runs are paused while the billing account is
  read-only. Past reports stay readable through `diagnosis_get_report`
  and `diagnosis_list_reports`.
- `diagnosis_not_found`: check the `report_ref` against
  `diagnosis_list_reports` before asking the user for more detail.

## Email setting

`diagnosis_update_schedule` only changes the `email_summary` setting:
an email summary after a completed run, on by default, which the user
can turn off or back on. Change it only when the user asks about
diagnosis email. It never schedules a run.
