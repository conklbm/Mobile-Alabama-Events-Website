# Review routine notes — 2026-10-09 (issue #8, run #13, follow-up pass)

Issue #8 was already mostly resolved by yesterday's run (28 of 37 items: 16 venue
aliases/new venues, 7 merge/never-merge calls — see the issue's own comment for that
list). This pass picked up the 9 items still open in the live queue after that run.

## Resolved automatically

**Cleared as not-cancelled (confirmed live on the venue's own site)**
- `#235` Scott Bradlee's Postmodern Jukebox — Pensacola Saenger Theatre, Thu Oct 8. Still
  listed on pensacolasaenger.com, "All Seats Reserved: Ticket Required." Source:
  https://www.pensacolasaenger.com/events/scott-bradlees-postmodern-jukebox-the-future-is-vintage-world-tour
- `#238` Rodney Carrington — Pensacola Saenger Theatre, Sat Oct 10. Still listed on
  pensacolasaenger.com ("Rodney Carrington Live 2026"), doors 6 PM / show 7 PM, ticket
  required. Source: https://www.pensacolasaenger.com/?p=114

Both were flagged `cancellation_flagged` (inferred — primary source had missed two runs);
the venue's own calendar confirms they're still on, so added to `not_cancelled:` in
`data/overrides.yaml`.

## Needs Brooks

Everything below is `venue_unknown` with an **empty venue field at the source** — checked
the database directly: `venue_name_raw` is literally blank for these occurrences, not just
unmatched. That means adding an alias in `venues.yaml` can't resolve them — the matcher
only matches against the raw venue text, and there's none to match. This is a gap in what
the eastern-shore-chamber collector pulls off the page, not a missing alias.

- **`#932` / `#965` — The Moonlight Chasse' Ballroom Dance Society.** Confirmed via several
  independent business.eschamber.com listings (2024–2027, consistent address each time):
  held 1st/3rd Mondays at Hot Wheels Skating Rink, 616 Whispering Pines Rd, Daphne —
  which is already in `venues.yaml` (`hot-wheels-skating-rink`), so the venue itself isn't
  the problem. Recommend `ignore 932 965` to quiet the queue (the event is real; the
  chamber's listing just doesn't carry a location field this collector captures).
- **`#937` / `#964` — BILL-E's BACON, BURGERS, & BIKES.** Confirmed the business: Bill-E's,
  19992 State Hwy 181, Fairhope, AL 36532 (business directory + USDA facility listing
  agree). Same blank-field problem as above. Recommend `ignore 937 964`.
- **`#941` — Dedication & Commissioning Ceremony for The Schreiber Water Treatment
  Facility**, raw venue "120-B CO RD 20, Foley, AL 36535." Still can't confirm this name
  — no news coverage, no ADEM/EPA record, nothing from Riviera Utilities' own site names
  "Schreiber." Closest lead: Riviera Utilities has a new "South Water Treatment Plant" bid
  package (5 MGD, Foley, 2024) that could plausibly be the same project under a dedication
  name, but I can't confirm the address or name match. Recommend calling Riviera Utilities
  (251-943-5001) to confirm, then `venue schreiber-water-treatment-facility "Schreiber
  Water Treatment Facility" Foley`, or `ignore 941`.
- **`#682` — Lowes Kid Workshops- Firefighting Plane**, venue "Lowes Home Improvement
  (Locations Vary)." Still unresolvable to one address — the listing itself says locations
  vary. Recommend `ignore 682`.

One judgment call carried over from the cancellation side:
- **`#192` — Adult Talent Show**, Crescent Theater, Sat Oct 24 (`cancellation_flagged`,
  venue already resolved to Crescent Theater). Couldn't find this listed anywhere
  currently — not on crescenttheater.com via search, not on any ticketing site — but also
  found nothing saying it's cancelled. Recommend checking crescenttheater.com or calling
  the box office directly, then `not-cancelled 192` or `cancel 192`.

If the blank-venue pattern above keeps recurring from eastern-shore-chamber, it's probably
worth asking the collector to pull whatever location field the chamber's event page
actually has — but that's a `pipeline/collectors/` change, outside what this routine
touches.
