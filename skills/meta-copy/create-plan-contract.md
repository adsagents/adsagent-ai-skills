# Meta Creation Plans

For performance-based creative selection, use `creatives_top` with the user's
account or product and metric within its advertised time window. If the user
requested another window, explain the limit before using the ranking.
Its rankings use cached observations. Show the reported age and coverage limits.
Keep the returned creative references.
Use only selections marked eligible for creation in `groups`. If the ranking
reports that a selection cannot be used by the available creation tool, explain
the limit and choose a supported source with the user. Keep the account's allowed
media sources unchanged; ranking alone does not make a selection usable.
Do not repeatedly list a creative library to compute the ranking yourself.
If the user only asks for "good" creatives, disclose an advertised default metric
or ask which metric to use; do not present a chosen metric as the user's choice.

Pass country and language names as the user said them. The server resolves them;
show any ambiguity for the user to choose. All languages requires an explicit
choice. Interests, devices and carriers must come from advertised search results.

Use `groups` for the requested structure, with video and image creatives in
separate groups when requested. Keep each selected creative in its intended group.
Do not infer group size from a shorthand such as “121” when it conflicts with the
user's stated counts; clarify the discrepancy before prepare.

Creation is paused by default. Request activation only when the user explicitly
asks to start delivery. Show the prepared tree, budget and currency, targeting,
schedule, final statuses and partial-completion policy together. One creation
plan uses one approval and one confirmation, even with several groups.

Before confirmation, use the advertised `campaigns_quick_create_revise` to change
names, schedule, activation or an allowed creative/group selection. Do not deny
and recreate the draft for those edits. Show the revised summary and obtain
approval of its current digest; the old digest no longer confirms it. A change
to budget or targeting requires a new prepare, as do unsupported selection edits.
Revision keeps the original expiry.

By default, complete groups follow the approved activation choice after a partial
failure; failed groups are cleaned up. If the user prefers to keep complete groups
paused or roll back all new objects, choose that policy during prepare. Show what
completed, what failed, what was cleaned up, and what remains unresolved. Unknown
results never authorize replay. Follow the returned recovery action.

When a resolved partial result permits a new attempt for missing groups, append
them to the same Campaign with a new prepare and explicit approval. Preserve the
successful groups; do not create a replacement Campaign. If the user deliberately
requests a fresh Campaign instead, explain that it is separate work.

The normal path is ranked creatives, prepare, optional revise, one confirmation,
then the returned task status. Use the prepare summary directly; do not repeat
setup or template reads merely to rebuild it.
