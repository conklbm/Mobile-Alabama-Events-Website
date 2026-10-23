# Review routine notes — 2026-10-23 (issue #13)

## Resolved automatically

- **Daphne City Hall** → added as new venue (`daphne-city-hall`), 1705 Main St, Daphne, AL 36526.
  Confirmed by Atlas Alabama's municipal directory and by local coverage of the 18th Annual Prodisee
  Pantry Turkey Trot, which starts on Main Street at City Hall.
  Source: [Atlas Alabama — Daphne](https://atlasalabama.gov/municipalities/daphne), [FOX10 — 18th Annual Prodisee Pantry Turkey Trot](https://www.fox10tv.com/2026/10/16/18th-annual-prodisee-pantry-turkey-trot/)
  → resolves `#1254` (Prodisee Pantry Turkey Trot).

- **Seville Square** → added as new venue (`seville-square-pensacola`), S Alcaniz St & E Government St,
  Pensacola, FL 32502. Regions `[coastal]` (Pensacola). Confirmed by Visit Pensacola's own event page
  for the Pensacola Hippie Fest and the historic square's NPS-documented location.
  Source: [Visit Pensacola — Pensacola Hippie Festival](https://www.visitpensacola.com/events/pensacola-hippie-festival-peace-love-art-music-food-community/), [Visit Pensacola — Seville Square](https://visitpensacola.com/directory/seville-square)
  → resolves `#1256` (Pensacola Hippie Fest).

- **`#794` Historical Lecture Series: A Taste of Mobile (Dec 13)** → added to `not_cancelled:` in
  `overrides.yaml`. Still listed on the organizer's own site (Historic Mobile Preservation Society),
  presented by Chris Andrews of Bienville Bites Food Tour at Cox-Deasy Cottage.
  Source: [Historic Mobile Preservation Society — A Taste of Mobile](https://www.historicmobile.org/event-details-registration/lecture-series-a-taste-of-mobile)

Queue went from 12 items to 9 after re-processing.

## Needs Brooks

- **`#627`/`#632`/`#646`/`#1067` — Eastern Shore Art Center classes flagged "possibly cancelled."**
  ESAC runs its calendar through a JS-rendered NeonCRM portal (per `sources.yaml` notes) that isn't
  indexed by search engines, so I couldn't confirm or deny any of these four from the web: "We're
  Dye-ing Over Here (Dye Processes)" Oct 24, "Hollywood in Your Pocket" Nov 6, and "Sculpting the
  Figure" Jan 1 + Jan 8. Recommend checking esartcenter.org's class calendar directly (or calling).
  - If still listed: `not-cancelled 627`, `not-cancelled 632`, `not-cancelled 646`, `not-cancelled 1067`
  - If actually gone: `cancel 627`, `cancel 632`, `cancel 646`, `cancel 1067`

- **`#1207` McDonald's Harvest Party — "McDonald's – Airport Boulevard."** Two McDonald's locations
  sit on Airport Blvd in Mobile: 3213 Airport Blvd (36606) and 9900 Airport Blvd near Snow Rd (36608).
  themobmom.com's own event page would say which, but its domain didn't resolve for me this run — I
  couldn't fetch it to check. Recommend you (or next run) check themobmom.com/event/mcdonalds-harvest-party/
  directly.
  - If it's the Airport/Snow location: `venue mcdonalds-airport-blvd-mobile-9900 "McDonald's" Mobile` then `alias "McDonald's – Airport Boulevard" = mcdonalds-airport-blvd-mobile-9900`
  - If it's the 3213 location: `venue mcdonalds-airport-blvd-mobile-3213 "McDonald's" Mobile` then `alias "McDonald's – Airport Boulevard" = mcdonalds-airport-blvd-mobile-3213`

- **`#1222` Taste of Christmas Festival — "Piggly Wiggly."** Mobile has multiple Piggly Wiggly
  locations (e.g. 306 S University Blvd hosts the unrelated "Taste of the Bay" tasting event each
  June); I found no source confirming which store hosts this December festival. The mobile-county
  source link didn't resolve for me this run to check directly.
  - `venue piggly-wiggly-<location> "Piggly Wiggly (<Street>)" <City>` then
    `alias "Piggly Wiggly" = piggly-wiggly-<location>` once you confirm the store, or `ignore 1222` if
    it turns out not to be real.

- **`#1148` Young Professionals of Mobile December 2026 Social — blank venue.** The Mobile Chamber's
  own calendar link didn't resolve for me this run, and search turned up no December 2026 YP social
  (only a May 2026 joint social at the Original Oyster House, Spanish Fort). Recommend checking
  my.mobilechamber.com directly or emailing the chamber (ascioneaux@mobilechamber.com, listed on their
  YP page) for the venue.
  - `venue <slug> "<Venue>" <City>` once confirmed, or `ignore 1148` if it's members-only/not a public event.

- **`#1209` City Fest (Fall Family Festival) — blank venue.** A themobmom.com roundup page (indexed
  copy) suggested 907 Shelton Beach Rd, Saraland — but I couldn't independently verify that street
  number (only 908 shows in property records) and couldn't fetch themobmom's own event page to confirm,
  since the domain didn't resolve for me this run. Recommend checking
  themobmom.com/event/city-fest-fall-family-festival/ directly before adding — don't want to guess an
  address.
  - `venue <slug> "<Venue>" Saraland` once confirmed, or `ignore 1209` if it can't be pinned down.

- **`#1267` Sweet Dreams Haunted Attraction — raw venue field is "weekends through Nov 1)."** This
  looks like a 92zew-rundown parsing bug (a schedule fragment landed in the venue field) rather than an
  actual venue name — the real haunted attraction is well-documented at 811 Saint Francis St, Mobile
  (cityofmobile.gov, Mobile County, The Scare Factor all agree). I didn't add an alias for the literal
  string "weekends through Nov 1)" because that garbled text could reappear attached to a *different*
  event from the same source and wrongly resolve to this venue. This is a source alert, not a venue
  question — flagging the 92zew-rundown collector for a look, not fixing it myself per the rules.
  - If you're comfortable it's a one-off: `venue sweet-dreams-haunted-attraction "Sweet Dreams Haunted Attraction" Mobile` then `alias "weekends through Nov 1)" = sweet-dreams-haunted-attraction`
  - Otherwise: `ignore 1267` and keep an eye on 92zew-rundown's parsing.

**A note on this run:** WebFetch couldn't resolve any external domain for me this session (DNS lookups
failed even for google.com), so everything above relied on WebSearch summaries rather than reading the
source pages directly. That's why several of the "Unknown venues" items above are flagged for you to
verify firsthand rather than resolved — worth a look if this recurs next week.
