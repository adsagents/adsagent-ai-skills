# Meta Product Health Contract

Use `products_list` first and pass only the selected public `product_ref` to
`products_get_health`. The tool is cached-only and never calls Meta.
`products_get_health` never starts an asset refresh. It returns a bounded
snapshot, not proof that every advertising object can deliver now.

## Read The Dimensions Separately

Never collapse these fields into one healthy/unhealthy label:

- `connection_health`: authentication and readable route state.
- `account_health`: cached account disablement or spend-limit blockers.
- `page_health`: cached Page publication, promotion, and ADVERTISE access.
- `delivery_health`: blockers proven by the checked inventory.
- `reporting_health`: cached Insights availability and freshness.

A connected account or fresh Insights ledger does not prove delivery health.
When campaign, adset, or ad inventory is `not_checked`, delivery is unknown,
never healthy. Inspect `data_coverage.levels`, `data_coverage.limitations`,
`collection_meta`, and `channel_availability` before giving a conclusion.
Truncated or incomplete coverage cannot support a healthy conclusion.

Unavailable, unsupported, stale, missing, and zero activity are distinct.
Unavailable numeric metrics must not be converted to zero. Preserve
`null` values and the returned availability reason.

## Page And Billing Boundaries

Use `assets_list_pages` only when Page-level detail is needed. It reads the
cached Page snapshot; because asset discovery is an existing onboarding
contract, it may queue the shared singleflight asset refresh on a cache miss.
Passing `refresh=true` is an explicit refresh request. Page-owned
`promotion_eligible` and connected-user `ads_eligible` diagnose different
blockers and must not be merged.

Raw Meta account balance is intentionally reported with unclassified
`balance_semantics`; `requires_top_up=null` means AdsAgent cannot safely decide
that the account needs a recharge. Do not reinterpret this as false.

## Next Actions

- Use `overview_get_live_configs` for a bounded live configuration read when
  campaign, adset, or ad state is required.
- Use an advertised Insights tool for performance, not for live delivery
  configuration proof.
- For a non-Meta product, preserve the explicit unsupported availability and
  follow: `Use the channel-specific AdsAgent MCP`.
- Never change customer permissions, refresh assets, or perform a write merely
  to make a health result look complete. Ask for the required explicit action.
