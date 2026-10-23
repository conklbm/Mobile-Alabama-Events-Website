# Review routine notes — 2026-10-23

Source: issue #12 ("27 items need review — 2026-10-22"), re-checked against the live
`pipeline queue` (an earlier same-day routine run on 2026-10-22 had already resolved
12 of the original 27 items). 9 items remain open.

## Resolved automatically

- **Ina Pullen Smallwood Memorial Library** (Chickasaw) — added as a new venue.
  224 Grant St, Chickasaw, AL 36611. Source: library's own site,
  https://www.inapullensmallwoodmemoriallibrary.com/, corroborated by Yellow Pages.
  Resolves `#1228` (Book Character Costume Contest).
- **Empanola Mobile** — added as a new venue. 4415 Old Shell Rd, Ste C, Mobile, AL 36608.
  Source: restaurant's own site, https://empanolamobile.com/location-and-hours
  (corroborated by Yelp and the Mobile Chamber directory). Resolves `#1225` (Coffee & Chat).
- **Crescent Comedy Workshop vs. Crescent Comedy Chaos** (4 ambiguous matches: `#1171`/`#997`,
  `#1174`/`#1004`, `#1176`/`#1009`, `#1179`/`#1016`) — added to `never_merge`. Confirmed via
  TicketWeb/crescenttheater.com listings these are two different, separately ticketed products
  on the same Wednesday nights: "Comedy Workshop" is a 5:30 PM all-ages joke-writing class,
  "Comedy Chaos" is an 8 PM 18+ open-mic show with ~16 comics. Different audience, different
  time, different ticket page — not a duplicate.

## Needs Brooks

- **`#1207` McDonald's Harvest Party — "McDonald's – Airport Boulevard."** Airport Blvd runs
  ~9 miles across Mobile with multiple McDonald's locations; the source (themobmom.com) doesn't
  give a street address, and the only hit I found (a stale, discontinued Foursquare listing for
  9900 Airport Blvd) isn't reliable enough to commit to. Recommend checking themobmom's post or
  the McDonald's store locator for the exact address, then:
  `venue mcdonalds-airport-blvd "McDonald's – Airport Boulevard" Mobile`
- **`#1209` City Fest (Fall Family Festival), Oct 25 — no venue given.** themobmom.com's own
  listing is the only source and I couldn't reach it this run (my fetch tool couldn't resolve
  the domain — may be a transient network issue, worth a retry) or find it independently via
  search; the Mobile County calendar doesn't carry it either. Recommend checking
  https://themobmom.com/event/city-fest-fall-family-festival/ directly, then:
  `venue <slug> "<Venue Name>" Mobile`
- **`#1222` Taste of Christmas Festival, Dec 6 — "Piggly Wiggly."** Mobile County's listing
  confirms the event but just says "Piggly Wiggly in Mobile" with no address, and there's more
  than one Piggly Wiggly in the area, so I can't tell which store without guessing. The linked
  Facebook event (facebook.com/events/1629458681932851) would likely confirm it; recommend
  checking that or calling Mobile County, then:
  `venue <slug> "Piggly Wiggly - <location>" Mobile`
- **`#1148` Young Professionals of Mobile December 2026 Social — no venue given.** Source is
  the Mobile Chamber's event calendar (my.mobilechamber.com); I couldn't reach the page this run
  (same fetch issue as above) and didn't find the venue independently. Recommend checking the
  chamber listing directly or YPofMOB.com, then:
  `venue <slug> "<Venue Name>" Mobile`
- **`#627` / `#632` / `#646` / `#1067` Eastern Shore Art Center classes ("We're Dye-ing Over
  Here," "Hollywood in Your Pocket," "Sculpting the Figure" x2) — possibly cancelled.** ESAC is
  the sole source for all four and its event portal (esartcenter.app.neoncrm.com) didn't load
  for me this run. Two consecutive misses triggered the flag per the freshness rule; I can't
  confirm either way without seeing the current class calendar. Recommend checking
  esartcenter.org's class schedule or calling (251) 928-2228, then:
  `not-cancelled 627 632 646 1067` (if still offered) or `cancel 627 632 646 1067` (if dropped).
- **`#794` Historical Lecture Series: "A Taste of Mobile," Dec 13 — possibly cancelled.** Mixed
  signal: Mobile County's calendar lists it for Dec 13 at the Cox-Deasy Cottage, but HMPS's own
  registration page for the identical title (historicmobile.org/event-details-registration/
  lecture-series-a-taste-of-mobile) shows **Sep 20, 2026** — already past — which suggests either
  a stale HMPS page or that this lecture already happened under a different date and the Dec 13
  slot belongs to a different talk. (Note: `#794` is already correctly kept distinct from
  "Clotilda Survivors, Living Legacy," a separate Dec 13 talk at the same cottage, via an existing
  `never_merge` entry.) Recommend calling HMPS at (251) 432-1281 to confirm the real date, then:
  `not-cancelled 794` or `cancel 794`.

## Not touched

Nothing in the collectors or review gates was changed — only `data/venues.yaml` and
`data/overrides.yaml`.
