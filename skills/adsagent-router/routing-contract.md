# AdsAgent Routing Contract

## Route Map

- Meta / Facebook / FB / Page / pixel / campaign copy: `meta-insights` or `meta-copy`.
- Google Ads / MCC / customer / search / PMax: `google-ads-insights`.
- TikTok / advertiser / TT / append to an existing TikTok campaign or ad group / copy / clone / recreate / delivery / budget / bid / optimization / support / TikTok MMP: `tiktok-insights`.
- 429 / 503 / Retry-After / concurrency / stale session / `mcp_meta_quota_deferred`: `adsagent-reliability` before recovery.
- setup / connect / OAuth / MCP token: `adsagent-setup`.
- notification / webhook / email / Feishu / Telegram: `adsagent-notifications`.
- scheduled task / automation / cron / reminder: `agent-scheduled-tasks`.

## Copy Routing

- One ad -> `copy_ad_quick_copy`.
- Multiple distinct source Ads regrouped into one destination tree -> `copy_ad_quick_copy` with `grouped_plan`.
- Campaign/ad set -> `copy_ad_clone_structure`.
- Known Campaign/Ad Set/Ad status, budget, or bid change -> `meta-copy`; do not
  route through a historical Meta performance read.
- Repeat prior creation -> `campaigns_recreate_from_task`.
- Template reverse-engineer, save, read-back, or reuse -> `meta-copy`; require
  snapshot verification before QuickCreate.
- Ask deep/fresh.

## Template Routing

- Route to `meta-copy` only when the explicit Meta/Facebook template itself is
  the lifecycle verb's direct object: list/view/open the templates,
  reverse-engineer/read back a template, or create/update/rename/delete/reuse
  one. Arbitrary compound modifiers such as `archived`, `campaign`, `report`,
  or `latest performance` do not change that direct-object route.
- Route reports, dashboards, charts, campaign lists, comparisons, and analyses
  to `meta-insights` when templates are a grouping, filter, subject, or
  performance dimension rather than the lifecycle object. This includes
  relation clauses such as "a report summarizing Meta template spend" or "a
  dashboard visualizing Meta template performance".
- Bind a direct-template override to the same Meta-qualified clause. An email,
  document, or other non-Meta template mentioned elsewhere in a compound
  request must not capture the Meta workflow.
- An unqualified natural-language template list/view/delete/rename request, or
  an unqualified `templates_*` tool request, remains in `adsagent-router` long
  enough to ask which channel. Do not assume Meta.
- An explicit Google Ads or TikTok template request routes to that channel's
  specialist. Capability discovery decides support; never substitute Meta
  template tools.
- In Meta, list with `templates_list`, view exact state with `templates_get`,
  delete only through `templates_delete`, and rename only through
  `templates_update` when the live guide advertises the operation.

## Ambiguous Scope

1. Read setup.
2. Inspect `setup_get_status.capabilities`; capability truth overrides guessed cross-platform parity.
3. Discover accounts.
4. Ask for scope and dates.
5. When `agent_method_profile.profile_id=adsagent_agent_methods_v1`, use its `consistent_query_tool` with root `query_contract_version=1`; otherwise use native tools.

## Shared Rules

- Hosted MCP is authoritative.
- Never read raw rows for questions or fan out across scopes/days.
- Trust totals only when `meta.complete=true`; missing scopes are unknown, never zero.
- On `mcp_fanout_detected`, stop the loop and use the platform batch tool.
- Before Meta delivery writes inspect `capabilities.delivery_mutations`; if denied follow `permission_action`, never self-elevate, then reconnect.
- For one known Meta entity, call the matching prepare tool directly. It reads
  live current configuration without mutation. Optional read-only preflight is
  one typed `overview_get_live_configs` request without `mutation_ref`; never
  substitute `management=true` or product/date Insights.
- Consequential platform/delivery writes require prepare, sanitized summary, explicit approval, then confirm; never substitute Campaign and AdSet budget levels.
- Meta creation uses `creation_contract_version=3`; read `adsagent://guide/creation-contract` and `adsagent://guide/name-contract`, then emit only explicit role fields. QuickCreate always sends `destination.type=web|app`.
- A reverse-engineered template preview is unsaved. Source labels and a
  successful template write do not prove persisted configuration; block
  QuickCreate until the exact saved template has server-owned snapshot
  readiness evidence. Template state writes are direct: require the exact
  advertised tool and explicit request instead of inventing prepare/confirm.
- Meta metadata: read `adsagent://guide/metadata-contract`; status writes use `target_configured_status`.
- On public `invalid_fields`, correct prepare once. Never replay confirm. A strict pre-send quota defer stops the plan before later confirms; follow `adsagent-reliability`.
- QuickCreate tokens are single-use for 15 minutes. On `confirm_token_invalid`, prepare again; never retry old confirm.
- Poll `task_ref`. Terminal create/copy requires `result.create_reconciliation.reconciled=true`; a `recovered_by_url_fallback` auxiliary image failure is not permission to retry. On `no_create_permission`, use `/dashboard/assets/fb-users`; never alter permissions.
- Meta delivery confirms may return inline `verification_result`; consume it
  first. Follow a returned `next_action` to `overview_get_live_configs` only
  while pending, and never substitute an Insights watermark. A local selector
  miss after `mutation_applied=true` is client snapshot drift, not a reason to
  reauthorize, replace the bearer, or replay the write.
- Meta decisions use `insights_query_consistent(require_fresh)` only when advertised; uncertain task writes use `operations_get_context` and are never replayed.
- Meta candidate reads use one AND plan; keep IDs; deduplicate and group client-side.
- Continue Meta pages with the unchanged cached contract and first-page `min_as_of`; do not rerun page 1 merely to continue. If the server rejects the continuation anchor, discard partial rows and restart page 1 serially.
- Use the common envelope only for `agent_method_profile.profile_id=adsagent_agent_methods_v1`; otherwise preserve native output.
- Preserve `support_ref` for unresolved handoff. It is not authorization.
- Google is a cached read-only ledger. TikTok features are capability-gated; a shared profile does not imply evidence parity.
- TikTok append uses native `append-campaign` / `append-adgroup` and `target_adgroup_id`; never translate it to Meta `append-adset`.
