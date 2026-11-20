# Review routine notes — issue #28 (2026-11-20)

A note on this run: **WebFetch to every source domain I tried (mobilecountyal.gov,
mobile.org, business.eschamber.com, themobmom.com, mobilemuseumofart.com,
ticketweb.com, facebook.com) failed with DNS/network errors** — this cloud
session's network policy doesn't allow fetching those hosts directly. I could
still use web search, so venue research below relies on search snippets,
county/chamber listings as indexed, and secondary sources rather than reading
the primary listing pages myself. That's also why none of the "Possibly
cancelled" items below got resolved this run — I can't load the specific
listing URLs the issue links to confirm or deny them.

## Resolved automatically

- **Cadillac Square Park** (`#1886`) — real place, confirmed via Mobile County's
  own events calendar and the Alabama Birding Trails site: 661 Bienville Blvd,
  Dauphin Island, AL 36528 (historic live-oak site, picnic tables/restrooms).
  Added as a new venue (`cadillac-square-park`), regions `[mobile, coastal]`.
  Source: https://alabamabirdingtrails.com/sites/cadillac-square/
- **Semmes Municipal Park** (`#1798`, "8108 Morris Hill Road") — the City of
  Semmes's own site gives this address for Semmes Municipal Park / its splash
  pad. Added as a new venue (`semmes-municipal-park`), regions `[mobile]`.
  Source: https://cityofsemmesal.gov/departments/parks-recreation/splash-pad/
- **Mobile Mystery Dinners** (`#1682`) — this is the organizer, not a new venue;
  their own history page and recent Fox10/county listings put their current
  shows at the Renaissance Mobile Riverview Plaza Hotel, 64 S. Water St., which
  was already in venues.yaml as `riverview-plaza`. Added "Mobile Mystery
  Dinners" as an alias there instead of creating a duplicate.
  Source: https://mobilemysterydinners.com/history-of-mobile-mystery-dinners/
- **Home Depot (Locations Vary)** (`#1647`, `#1657`) and **Lowes Home
  Improvement (Locations Vary)** (`#1663`) — confirmed national in-store kids'
  workshops that run at every area location the same day, so there's no single
  venue to alias. Added to `overrides.yaml` `force_publish:`, same reasoning
  already used for the Lowe's workshop at occurrence `#682`.
- **Lyle Lovett + Hayes Carll** (`#1634`) — venue_name_raw was blank at the
  92ZEW source. The date and lineup (Feb 2, 2027, 7pm) match a Pensacola Saenger
  Theatre show listed on eventworld.com; that venue is already in venues.yaml.
  Added to `force_publish` with a note, same blank-raw-field pattern as the
  existing entries there (can't alias a blank raw field).
  Source: https://www.eventworld.com/lyle-lovett-and-hayes-carll-pensacola-tickets-02-02-2027/event/609835
- **Central Midtown Holiday Market and Open House ↔ Second Saturday Market**
  (`#1837` / `#1015`) — Central Midtown's Second Saturday Vendors Market runs
  monthly at 1260 Dauphin St.; Dec 12, 2026 is that month's second Saturday, and
  the Dec 2025 edition of the same market ran under the "Holiday Open House and
  Market" name per the county calendar. Same seasonal-name pattern already used
  for the LoDa ArtWalk merges. Added `merge: [1837, 1015]` (keeping the
  themed/specific title).
  Source: https://www.mobilecountyal.gov/community_events/second-saturday-vendors-market-2026-01-10

## Needs Brooks

- **TrainTastic Interactive Model Railroad Museum** (8 occurrences, `#1786` and
  others) — real place, confirmed address **615 Pass Road, Gulfport, MS
  39501** (per WLOX and the venue's own listings). But Gulfport is in
  Mississippi — it doesn't fit any region in the current rules (not Mobile
  Bay core, not the Baldwin-coast/Pensacola outer ring). This is a scope call,
  not a data problem: is a Mississippi day-trip venue in bounds at all, and if
  so under what region?
  `venue traintastic-gulfport "TrainTastic Interactive Model Railroad Museum" "Gulfport"` — holding until you say which region (or `ignore` each id if it's out of scope).
- **The Swamp Lily** (`#1818`, November Vendor Market, Grand Bay area) — no
  business, market, or social presence found anywhere under this name. Left
  out per the "don't guess" rule.
  `ignore 1818` (or send me the business's real name/location if you have it).
- **Mason Hills Park** (`#1812`, Grand Bay Country Christmas, Dec 4) — can't
  pin down a single confirmed address. The event's own sponsor page names
  "Mason Hills Farm" as a sponsor, but the farm's listed addresses conflict
  across sources (one directory gives 9560 Grand Bay Wilmer Rd, the farm's own
  contact page gives a different Wheatcroft Rd address), and I'm not confident
  "Mason Hills Park" and "Mason Hills Farm" are even the same property.
  Recommend checking the organizer's site (thegbcac.com) or calling the farm.
  `venue mason-hills-park "Mason Hills Park" "Grand Bay"` once you have a confirmed address.
- **Piggly Wiggly** (`#1222`, Taste of Christmas Festival, Dec 6) — two Piggly
  Wiggly locations turn up in county event listings (306 S University Blvd,
  Mobile; 719 Saraland Blvd, Saraland) and I can't tell which one is hosting
  this one.
  `alias "Piggly Wiggly" = <slug>` once you know which store.
- **University of South Alabama** (`#1789`, Pancakes & PJ's with SantaPaws,
  Dec 5) — the raw venue is just the campus name; venues.yaml already has
  several specific USA buildings (Mitchell Center, Student Center, etc.) but I
  couldn't confirm which one hosts this particular event.
  `alias "University of South Alabama" = <slug>` once you know the building.
- **Young Professionals of Mobile December 2026 Social** (`#1148`, blank
  venue, Dec 10) — couldn't find a December 2026 listing at all (the chamber
  calendar may not have posted the location yet).
  `ignore 1148` for now, or check closer to the date.
- **Christmas Tour of Homes** (`#1527`, blank venue, Dec 5) — looks like a
  multi-house tour (Hope Blooms Fairhope runs one most years) rather than a
  single venue, but I couldn't confirm this year's organizer/homes list.
  If you confirm it's the same multi-stop format: `force_publish: 1527`. Otherwise `alias`/`venue` once you have a venue.
- **Elf Academy / "Location: Santa's Workshop, Alvin's Island"** (`#1870`,
  Dec 12) — sourced from the Eastern Shore Chamber, but Alvin's Island only
  has stores in Foley, Gulf Shores, and Orange Beach — none on the Eastern
  Shore — so I can't tell which store this refers to, or whether the raw venue
  name is even right.
  `alias "Location: Santa's Workshop, Alvin's Island" = <slug>` once confirmed.
- **Trae Crowder (Two Shows), Crescent Theater, Jan 9 2027** (`#1085`) — this
  wasn't in issue #28, but it came back `cancellation_flagged` after I
  reprocessed following today's edits. Worth a quick check since it's already
  merged with two other occurrences (see `overrides.yaml`).
  `not-cancelled 1085` if Crescent Theater / Ticketmaster still list it.
- **All 14 "Possibly cancelled" items from the issue** (`#1060`, `#549`,
  `#1293`, `#554`, `#961`, `#561`, `#463`, `#567`, `#572`, `#646`, `#1532`,
  `#657`, `#1067`, `#1125`) — I couldn't check any of these because WebFetch to
  their listing domains (mobilemuseumofart.com, business.eschamber.com,
  ticketweb.com, innovation-portal.com, esartcenter.app.neoncrm.com) is blocked
  in this session (see the note at the top). Nothing in web search confirmed
  or denied any of them. They need a manual look at the links in issue #28, or
  this environment's network allowlist needs those domains added so I can
  check them directly next time.
  `not-cancelled <id>` / `cancel <id>` per what you find.
