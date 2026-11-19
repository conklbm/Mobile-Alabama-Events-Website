# Review routine notes — Issue #26 (81 items, 2026-11-19)

Network note: this run's sandbox could not resolve most source domains directly
(mobilecountyal.gov, themobmom.com, mobile.org, eastern-shore-chamber/eschamber.com,
mobilemuseumofart.com, ticketweb.com, innovation-portal.com, etc.) — only general
web search worked, not direct page fetches. That limited verification on a few
items below; noted where it mattered.

## Resolved automatically

Venues added to `data/venues.yaml`:

- **Live Oak Landing** (Stockton, AL) — 8700 Live Oak Rd, Stockton, AL 36579. Baldwin
  County boat launch/park. Source: [baldwincountyal.gov](https://baldwincountyal.gov/community/parks/live-oak-landing)
- **Baldwin Square** (Satsuma, AL) — Old Highway 43, Satsuma, AL 36572. No street
  number found for the square itself. Source: [MapQuest](https://www.mapquest.com/us/alabama/baldwin-square-442064952),
  corroborated by Mobile County's own "Christmas in Satsuma" listing.
- **Southern Cross Home Care** — 6304 Piccadilly Square Dr, Ste 1, Mobile, AL 36609.
  Source: [NPI registry](https://npifinder.com/1457044786/southern-cross-home-care-of-al-llc)
  + [care.com](https://www.care.com/b/l/southern-cross-home-care-of-al-llc/mobile-al-6304-piccadilly-square-dr-ste-11)
- **Saraland Event Center** — 727 Saraland Blvd S, Saraland, AL 36571. Source:
  [Tagvenue](https://www.tagvenue.com/us/venues/saraland/70865/saraland-event-center),
  corroborated by Mobile County's events calendar.
- **The Happy Flea Market** — 19515 US-43, Mount Vernon, AL 36560 (a different
  flea market from the existing Mobile Flea Market on Schillinger Rd). Source:
  [MapQuest](https://www.mapquest.com/us/alabama/the-happy-flea-market-522208778) /
  [Yelp](https://www.yelp.com/biz/the-happy-flea-market-mount-vernon)
- **Christ United Methodist Church** — 6101 Grelot Rd, Mobile, AL 36609. Source:
  [Mobile Public Library community resources](https://mobilepubliclibrary.org/community-resources/christ-united-methodist)
  + multiple church directories.
- **Keller Williams Mobile** — 1210 Hillcrest Rd, Mobile, AL 36695. Source:
  [Keller Williams' own location directory](https://locations.kw.com/location/461).
  (Two other, older addresses for a Hillcrest Rd KW office turned up too; went with
  KW's own current directory as most authoritative.)
- **South Baldwin Regional Medical Center – Health Education Center** — 1613 N
  McKenzie St, Foley, AL 36535 (the hospital campus). Source: NeighborWho property
  listing placing South Baldwin Regional Medical Center at that address.
- **First US Bank (Daphne)** — 28664 US Hwy 98, Daphne, AL 36526. Source: Eastern
  Shore Chamber ribbon-cutting listing + First US Bank's own branch directory
  (usbanklocations.com).

Aliased to existing venues (same address, confirmed):

- "Central Presbyterian Church" and "1260 Dauphin Street, Mobile" → **Central
  Midtown** (existing entry, 1260 Dauphin St) — multiple directories place Central
  Presbyterian Church at exactly that address; "Central Midtown" is the building's
  current event-space branding.
- "St. Mary Parish, Mobile, Al" → **St. Mary's Catholic Church** (existing entry,
  1453 Old Shell Rd) — confirmed via search that St. Mary's "Lighting Up Midtown"
  festival is held on the parish campus at 1453 Old Shell Rd.
- "Senior Bowl" / "2027 Senior Bowl" → **Hancock Whitney Stadium** — the 2027
  Panini Senior Bowl game is confirmed there (Jan 30, 2027). Source: Fox10,
  Mobile Sports Authority.
- "2000 Main Street Daphne Alabama" → **W.O. Lott Park** — a search result
  explicitly places "Lott Park, 2000 Main Street, Daphne" as the site of Daphne's
  Jubilee Festival.

Ambiguous matches resolved in `data/overrides.yaml`:

- **Merged** (same game/show, one listing themed by the home org, one a generic
  aggregator duplicate): South Alabama Women's Basketball vs Clayton State
  (`[611, 1838]`), South Alabama Football vs App State (`[612, 1835]`), South
  Alabama Women's Basketball vs Marshall (`[615, 1847]`), South Alabama Women's
  Basketball vs Louisiana Tech (`[1756, 1846]`), Tab Benoit with Duane Betts at
  the Saenger (`[1768, 1783]`).
- **Never-merge**: Pensacola Children's Chorus `#1774` vs `#1193` — the
  "Cocoa with Santa ticket add on" is a separate add-on ticket product, not a
  duplicate of the "Christmas on the Coast" program (same pattern as the existing
  Pensacola Invitational override).

## Needs Brooks

- **TrainTastic Interactive Model Railroad Museum** (8 occurrences) — real place,
  confirmed at 615 Pass Road, Gulfport, MS. But that's Mississippi, outside every
  region this site covers (mobile/coastal are Mobile County + Baldwin coast +
  Pensacola). Judgment call on whether it belongs on the site at all and if so
  what region tag to use.
  → `ignore 1786 1792 1794 1795 1801 1802 1803 1805` if it should stay out, or tell
  me the region to use and I'll add it next run.
- **The Swamp Lily** (`#1818`, November Vendor Market) — couldn't find this
  business anywhere online under that name.
  → `ignore 1818`, or send me an address if you know this one.
- **Mason Hills Park** (`#1812`, Grand Bay Country Christmas) — found two
  different candidate addresses for "Mason Hills" in Grand Bay (the farm itself
  on Wheatcroft Rd N, vs. a separate "Smoke at the Park" event at Creekside RV
  Park on Grand Bay Wilmer Rd) and couldn't tell which one this event uses.
  → `venue mason-hills-park "Mason Hills Park" "Grand Bay" <address>` with
  whichever address is right, or `ignore 1812`.
- **Piggly Wiggly** (`#1222`, Taste of Christmas Festival) — Mobile County has
  11+ Piggly Wiggly stores and the source listing doesn't say which one.
  → `ignore 1222`, or tell me the store/address.
- **University of South Alabama** (`#1789`, Pancakes & PJ's with SantaPaws) —
  too generic; couldn't pin down which building on campus hosts it.
  → `ignore 1789`, or name the building (Mitchell Center, Student Center, etc.)
  and I'll alias it.
- **Mobile Mystery Dinners** (`#1682`, The Turkey's Done Mystery Dinner) — this
  is a traveling dinner-theater troupe that performs at different venues
  (Renaissance Riverview Plaza, Catalina Restaurant, and others); couldn't
  confirm which venue hosts this specific show (mobile.org, the source, wasn't
  reachable from this session).
  → `ignore 1682`, or tell me the venue for this date.
- **4100 Wulff Rd East – Semmes** (`#1797`, Semmes Christmas Parade) — nothing at
  exactly that address; nearby Wulff Rd businesses (Liberty Plaza at 4154, Boys &
  Girls Clubs at 3810 Wulff Rd E) don't match the number given.
  → `ignore 1797`, or confirm the business/park name at 4100 Wulff Rd E.
- **Alvin's Island – Santa's Workshop** (`#1870`, Elf Academy) — Alvin's Island
  is a beach-shop chain with several locations (Gulf Shores, Orange Beach,
  Perdido Key); couldn't confirm which store this event is at.
  → `ignore 1870`, or tell me which location.
- **8108 Morris Hill Road** (`#1798`, Christmas Magic in Semmes) — property
  records show this as vacant land (~4.7 acres), no business name found. Possibly
  a private residence running a seasonal display.
  → `ignore 1798`, or tell me the host name and I'll add it as a venue.
- **Home Depot (Locations Vary)** (`#1647`, `#1657`) and **Lowes Home
  Improvement (Locations Vary)** (`#1663`) — national multi-store programs, no
  single venue by design (same pattern as the existing Lowe's override).
  → `ignore 1647 1657 1663` if you want these to stop showing up, or I can add
  them to `force_publish` in `overrides.yaml` like the existing Lowe's entry if
  you'd rather they just publish without a venue page.
- **Blank venue** (`#1527` Christmas Tour of Homes, `#1148` Young Professionals
  of Mobile December Social, `#1634` Lyle Lovett + Hayes Carll) — no venue name
  at the source at all, nothing to alias.
  → `ignore 1527 1148 1634`, or send me each one's actual venue.
- **New ambiguous match, surfaced by this run's Central Midtown alias**: `#1837`
  **Central Midtown Holiday Market and Open House** (Dec 12) vs candidate `#1015`
  **Central Midtown: Second Saturday Market** — Dec 12 is the second Saturday of
  December, so this could be the regular monthly market with holiday theming, or
  a genuinely separate open-house event on the same day. I can't tell which from
  the listings.
  → `merge 1015 1837` if it's the same market, or `never-merge 1015 1837` if
  they're two separate things that day.
- **Possibly cancelled** (14 items) — couldn't verify any of these against the
  primary source because this session's network couldn't reach
  mobilemuseumofart.com, ticketweb.com, esartcenter.app.neoncrm.com,
  business.eschamber.com, or innovation-portal.com directly (only general web
  search worked, and it didn't turn up live status for these recurring/niche
  listings). Left as-is for you to check directly, or re-run me once those hosts
  are reachable: `#542 #1174 #1060 #549 #554 #961 #567 #463 #572 #646 #1532 #657
  #1067 #1125`.
- **Source alerts** (not a venue/match problem — flagging per instructions, not
  touching collector code): 92ZEW under-delivered (36 vs 40+ expected); City of
  Gulf Shores under-delivered (1 vs 2+); Mobile Chamber's calendar pull has been
  403-Forbidden since before 2026-10-22 (3+ weeks down); Mobile SPCA's calendar
  pull is now 401-Unauthorized (new since last run — looks like it may need an
  API key or the feed changed auth).
