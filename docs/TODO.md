# TODO

## Done 2026-09-15: email-reply review commands
Reply to the Thursday issue email (or comment on the issue) with one command per line:
`approve 73 79`, `cancel 151`, `not-cancelled 222`, `merge 271 269`, `never-merge 271 269`,
`alias "Raw venue name" = venue-slug`, `venue new-slug "Name" City`, `ignore 73`.
`.github/workflows/review-commands.yml` applies them, re-processes, republishes, replies, and
closes the issue when nothing is left. Only comments from the repo owner are honored.

## Also pending
- Blurbs in `series_notes.yaml` for the top recurring series (biggest SEO lever)
- Decide: show Foley / Gulf Shores / Orange Beach on the Mobile site (`regions: [mobile, coastal]`) or keep for GCBV
- Tier 2 parsers by volume: Mobile Arts Council, Lagniappe, Callaghan's, Blue Gill
- Watch the first scheduled (not manual) Thursday run
- Project review date: October 1, 2027
