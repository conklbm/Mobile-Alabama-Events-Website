# Event Source Registry — Mobile Metro + Gulf Coast Corridor

**Verified: 2026-09-14.** Replaces the Mobile Rundown–era Google Doc.
All statuses below were probed live on this date. Re-verify before build.

**Region tags:** `mobile` (→ mobilebayevents.com) · `coastal` (→ gulfcoastbeachvibes.com) · `both`

---

## Re-probed 2026-10-07 — read this first

Several "hard" sources below turned out to have structured data behind their JavaScript. **Before calling a
source unpullable, read the site's own JS for the URL its calendar loads.** Now built:

| Source | How | Collector |
|---|---|---|
| City of Mobile, Mobile County | `assets/includes/ajax/json.php?type=events` behind their calendars | `govcal_json` |
| 92ZEW Weekend Rundown | WP REST posts, one event per paragraph | `zew_rundown` (+ Friday run) |
| USS Alabama, Mobile Museum of Art, Bellingrath, Exploreum, Downtown Mobile Alliance | The Events Calendar API | `tribe_api` |
| Alabama Contemporary | Events Manager `/events.ics` | `ics` |
| South Alabama athletics | Sidearm `calendar.ashx/calendar.ics`, home games only | `ics` |
| Eastern Shore Chamber | GrowthZone classic layout, month pages | `growthzone` (`layout: classic`) |
| Visit Mobile (mobile.org) | sitemap → event pages with Event JSON-LD (REST API is Akamai-blocked) | `jsonld` (`sitemap:`) |
| Mobile Arts Council, Eastern Shore Art Center | Duda `/rts/collections/public/<alias>/runtime/collection/<name>/data` | `duda_collection` |

**Outer ring, built 2026-10-07/08** (see settings.yaml `outer_ring`): Visit Foley (Tribe, `only_draws`), Flora-Bama
annual events (Tockify `fbevents` ICS; the nightly live-music feed is left out on purpose), gulfshores.com festivals
(`gulfshores_festivals`: the annual-festivals listing cards for dates, each event page's PostalAddress for the town;
Crawl-delay 5).

**Outer ring, not built:** Visit Pensacola — its category filter is ignored, so finding festivals means crawling 80+
listing pages weekly, and the site dropped our connections during testing; event-page JSON-LD dates are wrong for
recurring events. Pensacola's big nights come from Ticketmaster (Bay Center + Saenger only), 92ZEW, the Rundown,
Flora-Bama and gulfshores.com. South Baldwin and Perdido Key chambers, Gulf State Park: mostly local minutiae the
outer-ring rule would drop anyway.

**Skipped on purpose:** Mobile Public Library (LibraryMarket JSON works, but ~350 routine branch programs);
Lagniappe (evvnt widget, mostly re-syndicated Bandsintown, robots 403); Regions Arena RSS (Ticketmaster covers it).

**Still not viable:** WKRG, OWA, City of Fairhope (403 to bots — do not work around); Pensacola Saenger (403);
Dauphin Island and The Grounds (Wix widgets need a signed session); Callaghan's (Elfsight, robots disallows);
The Hangout (no dates); Blue Gill (schedule is a JPG); Playhouse in the Park, History Museum (no calendar);
Mobile Botanical Gardens (Shopify, dates in prose); The Wharf (season over; Ticketmaster covers it).

**Moved/dead:** mobilecivicctr.com and mobilesaenger.com → regionsarena.com; mplonline.org → mobilepubliclibrary.org
(EventKeeper gone); gulfshores.com and visitpensacola.com are no longer Simpleview; visitperdido.com → perdidochamber.com.

## TIER 1 — Structured data, no browser needed

These return machine-readable JSON, ICS, or RSS. Build these first.

| Source | Region | Access method | Verified |
|---|---|---|---|
| **92ZEW** (92zew.net) | mobile | `/wp-json/tribe/events/v1/events` | ✅ **239 events live** |
| **Innovation Portal** | mobile | `/wp-json/tribe/events/v1/events` | ✅ 97 events live |
| **The Mob Mom** | mobile | `/wp-json/tribe/events/v1/events` + `?ical=1` | ✅ confirmed data |
| **Mobile Symphony** | mobile | `/wp-json/tribe/events/v1/events` | ✅ 7 events live |
| **Joe Jefferson Players** | mobile | `/wp-json/tribe/events/v1/events` | ⚠️ API live, 0 upcoming |
| **Mobile SPCA** | mobile | `/wp-json/tribe/events/v1/events` | ⚠️ API live, 0 upcoming |
| **Ticketmaster** | both | Discovery API v2 (free key required) | ✅ endpoint live (401 = needs key) |
| **City of Gulf Shores** | coastal | CivicPlus RSS + JSON-LD `Event` | ✅ RSS 200 |
| **City of Orange Beach** | coastal | CivicPlus iCal + JSON-LD `Event` | ✅ JSON-LD Event present |
| **Playhouse in the Park** | mobile | JSON-LD (3 blocks) | ✅ |
| **Soul Kitchen** | mobile | JSON-LD | ✅ |
| **Ben May Library** | mobile | EventKeeper — stable legacy HTML | ✅ 200 |

> **The Events Calendar (Tribe) is the single biggest unlock.** Any WordPress site
> running it exposes `/wp-json/tribe/events/v1/events` publicly with no auth.
> Write ONE collector, point it at N domains. Also test this pattern on any new
> source before writing a custom parser.

**Ticketmaster note:** their terms require attribution + link-back. They also run an
affiliate program worth evaluating. Covers Saenger, Civic Center, Wharf Amphitheater.

---

## TIER 2 — Server-rendered HTML, parseable without a browser

| Source | Region | Notes |
|---|---|---|
| Mobile Arts Council | mobile | Full HTML, no structured markup |
| Mobile County | mobile | Full HTML |
| Lagniappe | mobile | JSON-LD present but **no Event types** — parse listing HTML |
| The Wharf | both | SEOmatic, 1 LD block |
| Callaghan's | mobile | 1 LD block |
| Blue Gill | mobile | Squarespace, 2 LD blocks |
| The Hangout | coastal | 1 LD block |
| Pensacola Saenger | coastal | 1 LD block |
| Visit South Walton / 30A | coastal | 1 LD block |
| Eastern Shore Chamber | both | 1 LD block |
| Downtown Mobile Alliance | mobile | Small page |
| USA Music | mobile | Full HTML |
| Gulf State Park (alapark) | coastal | Full HTML |

---

## TIER 3 — Requires browser automation, or blocked

| Source | Region | Problem |
|---|---|---|
| WKRG calendar | mobile | **403** — Nexstar blocks non-browser agents |
| City of Mobile `/events/` | mobile | JS-rendered (only 22KB returned) |
| Town of Dauphin Island | both | Wix, JS-rendered |
| The Grounds | mobile | Wix, JS-rendered |
| OWA Foley | coastal | **403** |
| Destin-FWB | coastal | **403** |
| City of Fairhope | both | **403** |
| Visit Pensacola / Visit PCB / gulfshores.com | coastal | **Simpleview DMO.** REST API exists (`/includes/rest_v2/plugins_events_events_by_date/find/`) but returns *"Invalid credentials"* — needs HTML parse or browser |

**gulfshores.com is the highest-value Tier 3 target** — its own facets show Gulf Shores
(550), Foley (256), Theodore (47), Orange Beach (37), Mobile (79). Worth the effort.

---

## BROKEN / STALE in the old doc — fix or drop

| Source | Status |
|---|---|
| `cityofmobile.org/calendar-of-events/` | **404 — dead link** |
| **Mobile Civic Center / Saenger** (`mobilecivicctr.com`) | **Connection failed.** Major venue — needs manual re-check |
| Mobile Chamber (`web.mobilechamber.com`) | 503 |
| Eastern Shore Arts Center | 500 |
| Mobile Convention Center | Returns 114 bytes (empty) |
| `92zew.net/events/` | Page 404s — **but the API works.** Use the API |
| Eventful | Unverified — likely defunct, do not rely on |
| Old suggestions spreadsheet | Struck through in original doc |

---

## NO LONGER VIABLE

**Eventbrite** — public Event Search API removed Dec 2019, all requests denied after
Feb 20, 2020, killed without replacement. Only remaining paths: your own events, or
their distribution partner program. Scraping search pages violates their terms.

**Facebook** — Graph API public Page events access removed years ago. Personal Events
tab requires a logged-in session; automating it violates Meta terms and risks the
account that your business pages hang off. **Recommendation: manual weekly scan**
(~10 min) of the Events tab + VisitMobile, Downtown Mobile Alliance, Lagniappe,
City of Mobile, Mobile Parks & Rec pages.

---

## NEW COASTAL SOURCES TO RESEARCH

Not yet probed — gaps in the corridor east of Orange Beach:

- Flora-Bama (events URL 404'd; find current path)
- Perdido Key tourism
- Pensacola Beach / Santa Rosa Island Authority
- Navarre Beach
- Fort Morgan
- Bon Secour / Elberta
- Foley (high event volume per the gulfshores.com facet counts)

---

## BUILD ORDER

1. **One Tribe collector** → 6 domains. Highest output per line of code.
2. **Ticketmaster** → sweeps the big ticketed venues in one integration.
3. **CivicPlus RSS** → Gulf Shores + Orange Beach city calendars.
4. **JSON-LD parser** → Playhouse, Soul Kitchen, the Tier 2 LD sites.
5. Tier 2 custom parsers, one at a time, by event volume.
6. Tier 3 browser automation — only if coverage gaps justify it.
