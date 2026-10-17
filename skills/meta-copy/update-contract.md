# Meta Update Contract

For changing existing Meta Campaigns, Ad Sets, or Ads. Approval, `needs_input`, amount-guard, and recovery rules are in `adsagent-approvals`; this file only names the Meta tools and limits.

## Unified Update

When advertised, prefer `entities_prepare_update`: one approval covers several entities of the same level (Campaign, Ad Set, or Ad; the schema states the limit). It handles status, name, budget, bid, schedule, spend cap, targeting, and frequency. For Ads it also edits creative text fields (title, body, description, link, caption, call to action, URL tags), including per-card carousel fields and candidate lists for flexible or multi-asset ads.

- The live schema is the authority for allowed fields; never invent a field or a level.
- An unsupported format or field returns `needs_input` and creates no draft: tell the user what cannot be changed this way, or ask for the missing value, and prepare again.
- Confirm once with the tool named in the prepare result's `next_action`. The service reads fields back after the write; consume `verification_result` first.
- Use the per-level prepare tools in [creation-and-copy-contract.md](creation-and-copy-contract.md) only when this tool is not advertised or the level is not covered.

## Reading And Changing Ad Copy

Before editing Ad text, read the current copy with `ads_get_copy` and show before and after. For changes `entities_prepare_update` does not cover, use `ads_update_copy_prepare`, `ads_replace_creative_prepare`, `ads_replace_page_prepare`, or `ads_update_url_prepare`; each is prepare-only and is confirmed with the tool its `next_action` names.

## Dry Run And Amount Guard

Prepare asks Meta for a dry run (`validate_only`) before saving a draft. A rejection comes back with Meta's reason and no draft exists: change only the named field and prepare once more.

A budget or bid change refused with `money_change_exceeds_guard` is final for that request. Report the reason, never retry the same amount, never split it into smaller steps or move it to another level, and ask the user for a different amount or to contact support. Never state a limit.

## Unknown Results

If a confirm result is unclear, call `operations_get` with the exact reference. Never replay confirm and never prepare the same change again to "try again".
