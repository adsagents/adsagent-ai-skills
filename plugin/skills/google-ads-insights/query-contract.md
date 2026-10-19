# Google Ads Query Contract

Use Google Ads fields and tools only.

## First Steps

1. Run `setup_get_status` before analysis.
2. Inspect `setup_get_status.capabilities.agent_method_profile` before choosing a query tool.
3. Discover accessible Google Ads accounts with `google_ads_accounts_list`.
4. Choose an `enabled`, `non-manager` account; never analyze an MCC as a spend account. A test account (marked `test_account`) is also usable even when its status reads CLOSED.
5. Verify named customer IDs, and report customer/date/grouping.

## Product Cards And Templates

- List product cards with `google_ads_product_cards_list`. `date_from` and `date_to` are required. This list is not an insights breakdown.
- When a card includes `product_card.product_ref`, that public id is only for a destination app or URL card. Do not treat another row as that id.
- `google_ads_templates_list` lists saved ad-creation templates. Do not group, filter, or total insights by template. When a row includes `product_link`, that is the saved card link, not a breakdown.
- `google_ads_insights_overview_query` and `google_ads_insights_overview_batch` do not take a product card or a template as a breakdown. This channel has no funnel-values read. A missing funnel count is unknown, not zero.

## Freshness Boundary

Google Insights uses a read-only ledger; report `as_of` as observation time.
Its common query profile accepts only `consistency=cached` and
does not advertise require_fresh, common mutation receipts, since-launch, product
refresh, or live config verification. This limits the query profile, not the
whole Google MCP service. The read profile does not add a public MCP write capability;
native writes can be advertised independently.

This skill covers analysis. For a Google change use `google-ads-create` (new
campaigns) or `google-ads-manage` (existing ones); never substitute Meta tools
or conclude that all Google writes are unavailable from the read profile.
An advertised prepare/confirm flow requires a sanitized before/after summary,
explicit user approval, and one confirmation before expiry. Preserve the
returned receipt and original connection/login-customer route; recover an
uncertain outcome only through its advertised readback, never by replaying
the write. Native receipts do not imply common mutation-aware freshness.

## Query Pattern

- When `agent_method_profile.profile_id=adsagent_agent_methods_v1` and its consistent query tool is present in the client-local catalog, call that tool once with root `query_contract_version=1`, `consistency=cached`, and exactly one `scope` or one ordered `scopes` batch up to advertised `max_scopes`.
- If that advertised read tool is missing only from the client-local catalog, use the profile's named native fallback when present, otherwise `google_ads_insights_overview_query` or `google_ads_insights_overview_batch`. Do not report a server registration failure solely from a local selector miss.
- Trust top-level `complete=true`, ordered result contracts, and server `summary/total`; missing scopes are unknown, never zero.
- Follow returned `next_action` only; poll its task tool with exact `task_ref` and `poll_after_ms`. Consume a completed bounded terminal `result` directly; never rerun page 1 or invent a refresh task.
- Without the profile, or during the client-local read fallback above, use `google_ads_insights_overview_query` for one scope and `google_ads_insights_overview_batch` for multiple scopes.
- Do not create client-side fan-out by customer or date.
- If the server returns `mcp_fanout_detected`, stop the loop and combine current plus pending scopes through profile `insights_query_consistent` when advertised, otherwise `google_ads_insights_overview_batch`.
- For later pages, use the opaque continuation only through its advertised path. Keep customer, login-customer route, dates, grouping, filters, order, page size, and source snapshot unchanged. Never add Meta `min_as_of`.
- Never sum visible rows; distinguish rows shown from totals.

## Retry And Backoff

If Google Ads MCP returns `429` with `mcp_concurrency_limited`:

1. Honor `Retry-After + jitter`.
2. Retry serially within a small budget.
3. Prefer one profile `scopes` request or the native server-side batch tool instead of parallel calls.
4. Do not use token rotation or multiple sessions to bypass limits.

Parse backoff from the header, top-level `data`, or JSON-RPC `error.data`; never regex messages.

Treat `503` as dependency unavailable, not as a concurrency cap. Follow `/adsagent-reliability` for retry boundaries.

On `snapshot_expired` or continuation replay rejection, restart at page 1 with the same customer, dates, grouping, filters, and order, plus the original login-customer route and page size. Do not reuse the continuation, broaden scope, or fan out.

If Google Ads MCP returns `429` with `mcp_fanout_detected`, do not backoff-retry the same call. Switch to the profile batch shape or native batch overview tool.

## Name Lookup

To find campaigns, ad groups, or ads by name, call `entities_lookup_by_name`, then prepare the change from `prepare_groups`.

## User-Facing Output

Return Markdown with a direct answer, customer/date/grouping, compact metrics table, `as_of`, completeness, and rows shown versus total. Do not dump raw JSON, diagnostics, schemas, or every field.

For explicit full-table/export requests, poll the returned task handle to terminal and return the artifact link instead of raw rows.
