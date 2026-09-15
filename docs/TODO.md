# TODO

## Next up: email-reply review commands (Brooks picked this 2026-09-15)
Goal: make the weekly review loop phone-only. Reply to the Thursday issue email with commands;
an Action applies them, re-processes, republishes, and replies on the issue.

Commands to support (one per line in the comment):
- `approve 73 79`              -> pipeline approve --ids
- `cancel 151 222`             -> overrides.yaml cancelled: [...]
- `not-cancelled 222`          -> overrides.yaml not_cancelled: [...]
- `alias "raw venue name" = venue-slug`   -> append alias in venues.yaml
- `merge 271 269` / `never-merge 271 269` -> overrides.yaml
- `hide 73`                    -> keep held (no-op, records the decision)

Build: `.github/workflows/review-commands.yml` on `issue_comment` (label `review`, author = repo
owner only), a `pipeline/commands.py` parser that edits the YAML + calls approve, then
`process` + `publish`, commit, push, and `gh issue comment` with what changed. ~60 lines + tests.
Prereq: Brooks turns on repo notifications (Watch -> Custom -> Issues) so the issue lands in email.

## Also pending
- Confirm two Ticketmaster cancellations: `cancelled: [151, 222]` (When a Woman's Fed Up, Karen Morgan)
- Address-only venues: #73 Statemint pop-up (7701 Hitt Rd), #79 GO Run (no venue)
- Blurbs in `series_notes.yaml` for the top recurring series (biggest SEO lever)
- Decide: show Foley / Gulf Shores / Orange Beach on the Mobile site (`regions: [mobile, coastal]`) or keep for GCBV
- Tier 2 parsers by volume: Mobile Arts Council, Lagniappe, Callaghan's, Blue Gill
- Watch the first scheduled (not manual) Thursday run
- Project review date: October 1, 2027
