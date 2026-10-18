# Meta Update Contract

For changing existing Meta Campaigns, Ad Sets, or Ads. Approval, `needs_input`, amount-guard, and recovery rules are in `adsagent-approvals`; this file only names the Meta tools and limits.

## Unified Update

When advertised, prefer `entities_prepare_update`: one approval covers several entities of the same level (Campaign, Ad Set, or Ad; the schema states the limit). It handles status, name, budget, bid, schedule, spend cap, targeting, and frequency. For Ads it also edits creative text fields (title, body, description, link, caption, call to action, URL tags), including per-card carousel fields and candidate lists for flexible or multi-asset ads.

- The live schema is the authority for allowed fields; never invent a field or a level.
- A batch may include accepted and excluded rows. Show both, including exclusion reasons; one rejected row does not erase the accepted rows. If every row is rejected, `needs_input` creates no approval.
- Confirm once with the returned `confirm_tool`, or the tool named in a legacy result's `next_action`. The service reads fields back after the write; consume `verification_result` first.
- Use the per-level prepare tools in [creation-and-copy-contract.md](creation-and-copy-contract.md) only when this tool is not advertised or the level is not covered.

## Reading And Changing Ad Copy

Before editing Ad text, read the current copy with `ads_get_copy` and show before and after. For changes `entities_prepare_update` does not cover, use `ads_update_copy_prepare`, `ads_replace_creative_prepare`, `ads_replace_page_prepare`, or `ads_update_url_prepare`; each is prepare-only and is confirmed with the tool its `next_action` names.

## Dry Run And Amount Guard

Prepare may ask Meta for a dry run (`validate_only`). A batch retains a rejected row as an exclusion; a rejected legacy single-use prepare creates no draft. A changed value needs fresh approval.

A budget or bid change refused with `money_change_exceeds_guard` is final for that request. Report the reason, never retry the same amount, never split it into smaller steps or move it to another level, and ask the user for a different amount or to contact support. Never state a limit.

## Unknown Results

If a confirm result is unclear, call `operations_get` with the exact reference. Never replay confirm and never prepare the same change again to "try again".

For a batch, that replay prohibition applies to the uncertain row. A separate `not_attempted` tail follows the same-digest, original-expiry recovery in `adsagent-approvals` when advertised.
