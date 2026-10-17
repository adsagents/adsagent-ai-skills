---
name: adsagent-diagnosis
description: Use when the user requests a deep diagnosis, audit, or account health check (诊断 / 体检 / 审计 / 账户检查), or wants a diagnosis report read or acted on.
---

# AdsAgent Deep Diagnosis

Follow [routing](connection-routing.md) and [data rules](data-boundary.md).

Shared by the Meta, Google Ads, and TikTok connectors.

1. Only when the user asks for a diagnosis. Never on a schedule.
2. `diagnosis_get_status` first; confirm, then `diagnosis_run`.
3. Write the report explanation yourself from the returned findings.
4. Prepare recommendations for approval; a prepare changes nothing
   by itself.

Read [diagnosis-contract.md](diagnosis-contract.md) before a run,
report reading, or recommendation prepare.
