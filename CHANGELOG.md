# Changelog

Version history for the AdsAgent tri-channel skill pack.
The GitHub repo stays `adsagent-ai-skills`; Claude plugin slug is `adsagent`.

Version 0.7.64 adds a narrow Anthropic Claude plugin directory mirroring
exception to LICENSE.md so the community marketplace can pin commit SHAs
without treating the pack as open source. Connectors Directory MCP listings
remain URL-only and unchanged.
Version 0.7.63 bundles hosted MCP connection metadata with the Claude plugin.
Install `adsagent@adsagent` from this marketplace to get skills plus root
`.mcp.json` HTTP endpoints (Meta, Google Ads, TikTok) without pasting dashboard
install prompts. Anthropic Connectors Directory registration remains a separate
MCP-only path and is not this plugin package.
Version 0.7.62 completes Meta Phase 5 direct-write `mutation_ref` guidance
(templates, interests, products, permissions, MMP, setup, notifications,
tasks) and pins the Meta manifest to prod `1ffa06f7` (guide `2026-08-14.13`).
It builds on 0.7.59 Phase 6 durable-ref adoption: prefer
`operations_confirm_approval` with `approval_ref` and `expected_plan_digest`,
recover lost context via `operations_get_approval` /
`operations_get(mutation_ref|upload_ref=...)`, and treat legacy `confirm_token`
tools as compatibility-only.

AdsAgent helps operators analyze ad performance across Meta, Google Ads, and TikTok, compare safe platform state where supported, and prepare safer ad workflows. This repository teaches AI agents how to use AdsAgent responsibly without exposing internal tool catalogs, payload schemas, validation internals, or backend implementation details.

The operating model is B2B and resource-aware:

- answer operators in Markdown,
- fetch only the data needed for the user's question,
- prefer cleaned and aggregated reads,
- do not read raw rows in normal agent conversations,
- summarize before expanding,
- preserve server stability by respecting AdsAgent MCP retry and concurrency contracts.

Version 0.7.4 adds `agent-scheduled-tasks`, which teaches agents to distinguish reminder-only jobs from auditable execution, create deterministic schedules, read them back, run them once, and report execution proof honestly. It does not add an AdsAgent-hosted scheduler or bypass platform capabilities. Agents reuse top-level `client_skill_pack` from `setup_get_status`; they never run a separate version poll or automatic update.

Version 0.7.5 makes Meta partnership-copy behavior explicit: partnership and boosted-post ads use deep copy, unsupported fresh mode stops before approval, and cross-account eligibility failures are never retried automatically.

Version 0.7.6 keeps Meta candidate selection server-side with bounded pages, spend thresholds, deterministic name deduplication, and self-correctable public query validation.

Version 0.7.7 keeps Meta filtering server-side while making exhaustive Ad reads lossless: agents retain every `ad_id`, paginate serially with an unchanged filter, and aggregate duplicate Ad names only after all requested pages arrive.

Version 0.7.8 teaches agents to preserve an opaque MCP `support_ref` for unresolved error handoff without exposing tokens or raw payloads. It also separates Meta `scope_unavailable` from Meta creation permission.

Version 0.7.9 makes completed Meta consistency tasks terminal evidence: agents consume the bounded task result directly instead of querying page 1 again, and later pages use a fixed source watermark through `min_as_of` so a long read stays on one snapshot.

Version 0.7.10 adds safe grouped Meta copy guidance: one seed per target Campaign, remaining distinct Ads appended only after the target AdSet exists, explicit country or worldwide-minus-country targeting frozen in approvals, and a hard stop when the requested settings reference is missing.

Version 0.7.11 adds bounded Meta structured filtering across hierarchy names and IDs, performance metrics, configured/effective delivery status, budgets, objectives, events, Pixel, and App metadata. Conditions are server-side AND filters; exact Ad-name deduplication, language classification, and business grouping remain client responsibilities, while large exhaustive results use a grouped export artifact.

Version 0.7.12 routes multiple distinct Meta source Ads through one server-owned `grouped_plan` prepare. Agents verify the explicit settings-source order, geography, budget, bid, and paused-by-default structure in one approval, then consume the returned single-use confirmation token exactly once. Existing single-Ad, structure-clone, and recreate workflows remain compatible.

Version 0.7.13 corrects Meta scope recovery: `scope_unavailable` alone does not prove another workspace/token. Agents run bounded setup and matching discovery once, retry the identical read once only when the scope remains listed, then preserve `support_ref` for operator review without changing customer permissions.

Version 0.7.14 aligns Meta creation with the hosted v2 contract: canonical single/grouped copy examples, path-scoped legacy compatibility, typed QuickCreate launch fields, and one safe prepare-only correction for public `invalid_fields`. Confirm/write calls remain approval-gated and are never retried automatically.

Version 0.7.15 aligns the Hosted onboarding prompt with that Meta v2 creation contract: read the bounded creation resource, use canonical single/grouped fields, correct public `invalid_fields` on prepare at most once, preserve `support_ref` on repeat failure, and poll the returned `task_ref`.

Version 0.7.16 removes public name-role ambiguity. New creation clients read both bounded contract resources and use explicit `campaign_name`, `adset_name`, `ad_name`, `template_name`, `new_template_name`, `folder_name`, and `interest_pack_name` fields. Exact-path legacy `name` inputs remain compatible, but agents never emit them for new requests or move them across object roles.

Version 0.7.17 adds the bounded Meta metadata contract. Agents keep configured delivery state, effective delivery outcome, write targets, task lifecycle, money units, budget ownership, bid strategy, optimization goal, and source evidence in distinct roles. New status mutations emit `target_configured_status`; legacy `status` remains accepted only by the exact hosted mutation tools.

Version 0.7.18 aligns Google and TikTok recovery with their optimized Hosted MCP paths. Agents handle structured dependency failures without inventing tasks, consume verified terminal results without rerunning page 1, and restart expired Google snapshots from an unchanged first-page request.

Version 0.7.19 pins exhaustive Meta pagination to one completed cached snapshot and distinguishes confirmed rejection from uncertain write outcomes. Agents continue page 2 and later with the first-page source anchor, never replay an uncertain write, and only start a fresh task with fresh approval after the server proves the prior write was rejected or not created.

Version 0.7.20 makes Google and TikTok continuation rules platform-specific. Agents keep the original scope, route, ordering, page size, and source snapshot bound to each opaque continuation; they never apply Meta `min_as_of` to another channel. Expired or replayed continuations restart the identical first page, while uncertain writes remain receipt-recovery only when the hosted capability profile advertises those tools.

Version 0.7.21 makes terminal Meta create/copy failures actionable without exposing raw diagnostics. Agents report each bounded `result.failures.items` entry, follow its public `next_action`, never retry the unchanged write, and hand off only unclassified items or explicit operator-review states.

Version 0.7.22 makes Meta export delivery lossless across MCP clients. Terminal `insights_export` polls retain `result.artifact`; agents send its opaque short-lived `download_url` byte-for-byte to HTTP GET and never redact, rebuild, decode, truncate, or substitute it. Expired or missing links require a newly requested export.

Version 0.7.23 distinguishes local pre-send Meta quota admission from uncertain writes. Agents recover only from the strict `mcp_meta_quota_deferred` contract, preserve completed batch receipts, wait for `retry_after_seconds`, and re-prepare the exact same entity/value with fresh approval. They never reuse a confirm token or replay a sent/uncertain write.

Version 0.7.24 publishes the canonical Meta QuickCreate Append contract. Agents use `append_mode=append-campaign` with `target_campaign_id`, or `append_mode=append-adset` with `target_adset_id`; append-adset creates only Ads and inherits the existing parent budget. Unsupported legacy fields receive bounded `invalid_fields`, which may be corrected on prepare once before a new summary and fresh explicit approval.

Version 0.7.25 makes partial Meta Ad-create recovery receipt-driven. Agents report each bounded failed Ad and follow its returned retry flags, preserve already-created Ads, and prepare a new task only when `manual_new_task_allowed=true`. AdsAgent may split bulk Ad writes into configurable sequential chunks as a defensive reliability policy; the chunk size is not evidence of a fixed Meta platform limit.

Version 0.7.26 added TikTok-native Quick Create append guidance and the original single-row creatives_confirm_upload readiness step, which version 0.7.28 supersedes with bounded batch reconciliation. Agents distinguish `append-campaign` from `append-adgroup`; every append remains prepare-first, explicitly confirmed once, and receipt-recovered on the exact original route.

Version 0.7.27 adds a plan-level circuit breaker for strict pre-send Meta quota admission. On the first qualifying `mcp_meta_quota_deferred`, agents stop all later confirms, preserve completed/current/remaining partitions, wait for the largest `retry_after_seconds` plus jitter, and re-prepare only the unchanged remainder under one fresh consolidated approval. They never reuse a confirm token or replay completed, sent, or uncertain work.

Version 0.7.28 adds TikTok creative readiness recovery. Agents inspect the server's normalized readiness reason, retryability, supported formats, eligibility, and next action; reconcile 1..20 tenant-owned pending or historical verification rows in one bounded server call; never fan out per creative; and treat terminal upload failure as requiring the returned remediation before Quick Create or append.

Version 0.7.29 aligns TikTok Quick Create task receipts. Agents poll the returned opaque `ttask_*`, keep the internal `task_id` as legacy compatibility only, recover historical UUIDs that were mislabeled as `task_ref`, consume bounded terminal created-object and failure receipts, and never replay an uncertain or failed write.

Version 0.7.30 closes the TikTok Smart+ image-append contract. Agents use `task_ref` only for task polling and `operation_ref` only for `operations_get`; for eligible local image creatives, the server verifies advertiser ownership, maps the provider image reference to TikTok's Smart+ wire field, and inherits compatible image-family defaults without asking the agent to invent provider IDs or replay a failed write.

Version 0.7.31 adds controlled notification integration guidance. Agents can inspect masked email, Feishu, Telegram, and Meta Ads Webhooks state, then use prepare, sanitized review, explicit approval, and single-use confirm. Test notifications send exactly one real message only after approval; uncertain Meta subscription results are reconciled by read, never by replay.

Version 0.7.32 clarifies that credential-taking notification integration tools are operator-scoped. Agents use them only when advertised; OAuth Safe Mode keeps them hidden, and agents never solicit integration credentials in chat when the tools are absent.

Version 0.7.33 publishes the notification monitoring contract. Agents distinguish six event-driven Meta Ads Webhook fields from eight cached asset-health checks, report default recharge/token/cooldown thresholds, use the runtime capability map as truth, and never present Webhooks as continuous spend reporting or an Insights replacement.

Version 0.7.34 aligns TikTok's capability-gated management and reuse workflows. Agents use receipt-backed delivery, budget, bid, same-advertiser copy/clone/recreate, complete-evidence optimization recommendations, in-app notifications, manual support reporting, upload abandonment, and TikTok-channel product MMP aggregates only when Hosted setup advertises them. Every write remains prepare/review/explicit-confirm with exact-route recovery; uncertain operations are never replayed.

Version 0.7.34 also publishes a machine-readable release manifest used by all three Hosted MCP services. Meta, Google Ads, and TikTok can refresh the recommended client version from the same immutable tagged release without adding a GitHub request to customer MCP calls; invalid, untagged, or downgraded manifests are ignored.

Version 0.7.35 restores explicit Meta delivery-management discovery. Agents inspect `capabilities.delivery_mutations`, stop for the advertised human permission action when access is disabled, reconnect after access changes, and use distinct confirmation-gated ABO AdSet and CBO Campaign budget paths without substituting budget levels.

Version 0.7.36 reconciles terminal Meta QuickCreate tasks before recovery. Agents require requested-to-created accounting, map Ad names and available creative selection keys to created Ad IDs, treat URL-fallback image-upload failures as compensated rather than retryable, send explicit web/app destination types, and discover recent uploads with a bounded inclusive/exclusive time window.

Version 0.7.37 narrows Skill activation and adds progressive disclosure. A clear single-channel request activates only its specialized Skill; the router is reserved for ambiguous or cross-channel requests. Each `SKILL.md` now contains the decision path and links to bounded references for detailed contracts. Release CI validates documented tool names, required capabilities, and capability gates against pinned public Meta, Google Ads, and TikTok service manifests.

Version 0.7.38 adds the cached Meta product-health contract. Agents keep
connection, account, Page, delivery, and reporting health separate; inspect
coverage and truncation before conclusions; preserve unavailable values as
`null`; and never infer deliverability from a readable connection or Insights
alone.

Version 0.7.39 adds Meta current-entity inventory guidance. Agents distinguish
zero Insights from zero activity, require complete inventory coverage for
entity-existence totals, preserve inherited delivery blockers without
rewriting native status, and pin every paginated read to its first-page
inventory generation.

Version 0.7.47 makes Meta delivery confirmation self-contained across clients
with cached per-conversation tool catalogs. Agents consume inline
`verification_result` first and call a returned live-read `next_action` only
while pending. A local selector miss after `mutation_applied=true` is client
snapshot drift, never a reason to reauthorize, replace the bearer, or replay
the accepted write.

Version 0.7.48 makes Meta template creative-distribution updates deterministic.
Agents use the existing `templates_update` tool with flat `template_name` and
`creative_distribution` fields, never invent a separate distribution tool,
and always read the exact template back before QuickCreate. Hosted also accepts
an exact-mask, revision-bound compatibility patch without silently broadening
or replaying the update.

Version 0.7.49 keeps reads available when a long-lived client has an older
local tool catalog. When setup advertises an Agent Method Profile but its
consistent read tool is absent only from the client selector, agents use the
profile's named native overview/batch fallback (or the documented channel
fallback), preserve native completeness semantics, and do not misreport a
server registration failure. Applied writes remain receipt-bound and are never
replayed.

Version 0.7.54 treats an exact missing template selector as a normal bounded
read result. Agents may continue an already explicitly approved create, while
the same missing result after a write still means persistence is unverified and
must never trigger replay.

Version 0.7.55 separates post-create delivery evidence from spend evidence.
Reconciled Meta create/copy tasks expose one bounded read-only live-config
action for their created Ads; agents execute it once without replaying the
write. Exact zero metrics require `metrics_evidence.zero_proven=true`, while
`mutation_coverage` remains limited to metrics reads using
`after_mutation_ref`.

Version 0.7.57 pins Meta Quick Copy fields to their owning tools. Existing
Campaign expansion uses `mode=new_adsets` with `target_campaign_id` and the
`campaign_status`/`adset_status`/`ad_status` fields; `status_option` remains
structural-clone-only and `append_mode` remains QuickCreate-only.

Version 0.7.53 keeps saved-template workflows available in clients that expose
tools but not MCP Resources. Agents use the request-scoped
`template_mutations.inline_contract`; when `guide_resource_required=false`, an
`Unknown resource` result for the optional template catalog does not block the
guarded write or masquerade as server tool-registration drift.

Version 0.7.52 uses the request-scoped template capability block from
`setup_get_status` before saved-template writes. Agents can distinguish an
authorized `mcp.templates.write` grant from a tool name appearing elsewhere,
then perform the existing exact-name read-back without broadening permissions.

Version 0.7.51 correlates scheduled Meta candidate delivery state by exact
`entity_type` and `entity_id`. Agents read up to 50 explicit candidates in one
bounded live-config batch, require complete one-to-one coverage, and never let
a parent status or an out-of-scope manual change alter the candidate decision.

Version 0.7.50 keeps scheduled Meta workflows safe when a long-lived Work
conversation receives only part of the hosted tool catalog. A matching prepare
remains the live preflight, confirm-side inline verification is consumed first,
and pending recovery uses the profile's native operation fallback. A missing
optional selector before mutation no longer disables read-only rule evaluation;
an unreconciled applied write remains receipt-bound and makes later runs
read-only rather than being replayed.

Version 0.7.46 aligns all three channels with the MCP 2026-07-28 dual-era
contract. Agents keep product endpoints/profiles separate from negotiated
protocol revisions, let the client choose the supported revision, use
stateless `server/discover` for modern connections, and limit session recovery
to negotiated legacy clients. A protocol or guide update alone never requires
MCP re-registration, bearer replacement, customer-permission changes, or an
automatic Skill Pack update.

Version 0.7.45 allows arbitrary natural-language modifiers on direct Meta
template objects while keeping reports, dashboards, charts, and analyses that
describe template performance with `meta-insights`. The router distinguishes a
direct template object from an indirect template dimension introduced by
relations such as `by`, `about`, `showing`, or `using`, instead of maintaining
adjective or entity-name whitelists. Direct lifecycle overrides are limited to
the same Meta-qualified clause, so unrelated email or document templates do
not capture a Meta performance request.

Version 0.7.44 restricts Meta template lifecycle routing to requests whose
verb operates directly on the template object, so analytics reports that
mention templates remain with `meta-insights`. It also makes the exact
server-owned source-import mode the only source-reference-only template-write
exception; all other provenance-only payloads remain non-snapshot writes.

Version 0.7.43 aligns Meta template lifecycle routing and delivery writes with
the current Hosted contract. Explicit template open, reverse-engineer, and
read-back requests route to `meta-copy` even when a template name contains
analytics words. Agents use `templates_list` only for bounded screening and
exact-name `templates_get` before QuickCreate. Manual complete-map templates
may retain an account binding without claiming source-AdSet provenance, and
unsupported object-field writes stop instead of substituting another level.

Version 0.7.42 separates one-entity live configuration checks from historical
Insights. Known Campaign, Ad Set, and Ad status/budget/bid changes call prepare
directly because prepare reads current Meta state without mutating it; optional
read-only preflight uses one typed `overview_get_live_configs` request.
`read_query_too_large` is self-correctable and no longer becomes a false
operator handoff.

Version 0.7.41 synchronizes the Meta `2026-07-27.8` manifest. Bounded
`templates_list` rows now report the same persisted v1 migration state as
`templates_get` without loading full configuration envelopes. Agents still use
the exact-name detail read before QuickCreate prepare.

Version 0.7.40 adds a fail-closed Meta template snapshot contract. A
reverse-engineered result remains an unsaved preview; saving is blocked unless
Hosted first exposes a verifiable snapshot-write contract, every accepted
template write requires exact-name read-back, and affected-template
QuickCreate stays blocked until Hosted returns machine-verifiable persistence,
normalization, revision, rejected-path, and launch-readiness evidence. Generic
template validation without bounded public fields stops for operator review.
This is a client-side safety mitigation; it does not claim that Hosted
persistence or validation has been repaired. Persistence-only verification is
non-launchable until QuickCreate binding is complete, template diagnostics are
bounded and sanitized with completeness flags, and explicit Meta template
list/view/delete/rename requests route through `meta-copy`.

