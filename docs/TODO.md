# TODO

## Done 2026-09-15: email-reply review commands
Reply to the Thursday issue email (or comment on the issue) with one command per line:
`approve 73 79`, `cancel 151`, `not-cancelled 222`, `merge 271 269`, `never-merge 271 269`,
`alias "Raw venue name" = venue-slug`, `venue new-slug "Name" City`, `ignore 73`.
`.github/workflows/review-commands.yml` applies them, re-processes, republishes, replies, and
closes the issue when nothing is left. Only comments from the repo owner are honored.

## Done 2026-09-17: automatic venue research
Cloud routine `Mobile Bay Events: resolve review queue` (Thu 12:00 and 16:00 UTC) + `.github/workflows/apply-config.yml`.
If it misbehaves: claude.ai/code/routines -> the routine -> run log. Its commits are titled "review routine: ...".

## Also pending
- mobile.org (Visit Mobile) events: Simpleview, JS-rendered, REST needs credentials (probed 2026-09-15). Two paths:
  (a) email Visit Mobile for feed/partner access; (b) Playwright in the weekly Action, which would also unlock
  gulfshores.com and Visit Pensacola. Brooks said "not yet" on the email.
- Blurbs in `series_notes.yaml` for the top recurring series (biggest SEO lever)
- Decide: show Foley / Gulf Shores / Orange Beach on the Mobile site (`regions: [mobile, coastal]`) or keep for GCBV
- Tier 2 parsers by volume: Mobile Arts Council, Lagniappe, Callaghan's, Blue Gill
- Watch the first scheduled (not manual) Thursday run
- Project review date: October 1, 2027
