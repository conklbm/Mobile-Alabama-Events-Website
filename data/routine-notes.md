# Review routine notes — issue #23 (2026-11-12)

**Network note:** `themobmom.com`, `mobilecountyal.gov`, `mobilemuseumofart.com`, `ticketweb.com`, and
`esartcenter.app.neoncrm.com` were all unreachable from this session (DNS blocked by the sandbox's
network allowlist). That blocked direct verification of several raw venue listings and most of the
"possibly cancelled" checks below — worth allowlisting those domains for this routine if that's easy
to do.

## Resolved automatically

- **St. Paul's Episcopal Church (Daphne)** — new venue, 28788 N Main St, Daphne, AL 36526. Resolves
  #1691, #1693, #1696, #1654. Source: https://www.episcopalassetmap.org/node/1874,
  https://churcheslist.com/saint-pauls-episcopal-church-102/
- **Barnes & Noble (Mobile)** — new venue, 3930 Airport Blvd, Mobile, AL 36608 (McGregor Square;
  reopened Sept 2026). Resolves #1638. Source: https://www.fox10tv.com/2026/09/24/barnes-noble-opens-new-store-mobile/
- **Local History & Genealogy Library** — new venue, 753 Government St, Mobile, AL 36602 (a separate
  Mobile Public Library branch from Ben May Main Library at 701 Government St). Resolves #1672.
  Source: https://www.mobilepubliclibrary.org/locations/localhistory.php
- **Revive Church** — new venue, 601 Zeigler Circle E, Mobile, AL 36608. Resolves #1685. Source:
  https://www.cityofmobile.gov/christian-comedy-revival-live-talk-show/, https://mobilearts.org/locations/revive-church/
- **Prodisee Pantry** — new venue, 9315 Spanish Fort Blvd, Spanish Fort, AL 36527 (the pantry itself —
  separate from Daphne City Hall, which is just its Turkey Trot's start line). Resolves #1687.
  Source: https://mobilepubliclibrary.org/community-resources/prodisee-pantry, https://foodpantries.org/li/prodisee_pantry_36527
- **Loxley Public Library** — new venue, 1001 E Loxley Ave, Loxley, AL 36551 (former St. Patrick's
  Catholic Church building; separate from Loxley Municipal Park). Resolves #1649. Source:
  https://www.cityofloxley.com/venue/loxley-public-library/
- **Al Trione Sports Complex** — new venue, 8600 Whispering Pines Rd, Daphne, AL 36526. Resolves
  #1660. Source: USSSA tournament pages; Alabama.travel.
- **Downtown Silverhill** — new area-wide venue (no single street address, same pattern as the
  existing Downtown Mobile / Downtown Fairhope entries), Silverhill, AL 36576. Resolves #1639, #1655.
  Source: https://www.silverhillalabama.com/?p=722
- **Condé-Charlotte Museum House** — added the raw string "Conde-Charlotte Museum 104 Theatre St.
  Mobile, AL 36602" as an alias to the existing entry (already correctly addressed at 104 Theatre St).
  Resolves #1703.
- **Elberta Town Park** — added "Main st -Elberta AL" as an alias to the existing entry (13052 Main
  St; the town's Christmas parade runs Main St with the tree lighting after in the park). Resolves
  #1637. Source: https://business.southbaldwinchamber.com/events/details/elberta-christmas-parade-31243,
  https://gulfcoastmedia.com/stories/elberta-makes-changes-to-parade-route,81328
- **Merge:** Trae Crowder "Early Show" (#1704, mobile-arts-council) into #1085 ("Two Shows") — both
  are the same 7pm/9pm Jan 8, 2027 booking at Crescent Theater. Source: mobilecountyal.gov's own
  listing title `trae-crowder-two-shows-2027-01-08`, corroborated by Live Nation.

## Needs Brooks

**Unknown venues — couldn't confirm a single address:**
- **Sardine Pass** (#1671, fishing tournament): no source ties this name to a street address — reads
  as a water channel/pass name, not a venue. No clean recommendation; leave held, or `ignore 1671`.
- **156 S. Florida Street** (#1441, Midtown Vintage Market): conflicting signals — one low-authority
  directory names "Florida Street Vintage" at 156 S Florida St, but another source suggests "Vintage
  Verb" is actually next door at 158 S Florida St. Once you know which shop it is:
  `venue florida-street-vintage "Florida Street Vintage" Mobile` (swap in whichever name/address is right).
- **Dots and Dragons Mahjong Parlor** (#1670): two conflicting addresses found — 2724 Old Shell Rd
  (tied to the "Blue Bird Hardware" building per a WKRG story) vs. 4318 Downtowner Loop N, Suite G
  (per a booking-platform listing). Please confirm with the business before I add it:
  `venue dots-and-dragons-mahjong "Dots and Dragons Mahjong Parlor" Mobile`.
- **Lowes Home Improvement (Locations Vary)** (#1640, #1663) and **Home Depot (Locations Vary)**
  (#1647, #1657): confirmed these are simultaneous nationwide kids'-workshop programs with no single
  address — same situation as the existing `force_publish: 682` entry. `ignore 1640 1663 1647 1657`
  to clear them, or tell me to add matching `force_publish` entries if you want them live.
- **Christmas Tour of Homes** (#1527): blank venue at source (eastern-shore-chamber) — it's a
  self-guided tour of several private homes, no single venue. `force_publish 1527` to publish anyway,
  or `ignore 1527`.
- **Young Professionals of Mobile December 2026 Social** (#1148): blank venue at source
  (mobilechamber — whose pull is currently failing, see Source alerts below). Couldn't find this
  specific social's venue anywhere online. `ignore 1148` for now, or it may resolve itself once the
  Chamber pull is fixed.
- **Daphne's Christmas Parade 2026**, raw venue "2000 Main Street Daphne Alabama" (#1658): no
  business/property matches that exact address (real nearby numbers are 2039, 2212, 2401, 2510 Main
  St). Daphne's Christmas parade has historically started/ended at Daphne Civic Center (already in
  venues.yaml) — looks like themobmom.com gave an approximate address rather than a real one.
  `alias "2000 Main Street Daphne Alabama" = daphne-civic-center` if you agree that's the actual point,
  otherwise leave held.
- **Piggly Wiggly** (#1222, Taste of Christmas Festival): multiple Piggly Wiggly stores in the Mobile
  area; couldn't pin down which one hosts this festival. Once you know:
  `venue piggly-wiggly-<location> "Piggly Wiggly (<location>)" <City>`.
- **Lyle Lovett + Hayes Carll** (#1634, blank venue, Feb 2 2027): no Mobile-area show found publicly
  yet for this tour (closest confirmed date found was Philadelphia, MS, Jan 29 2027); note 92ZEW's own
  pull is also short this run (37 vs. 40+ expected events) — this one may just not be fully listed
  yet. Leave held for next run, or `ignore 1634`.
- **Mobile Mystery Dinners** (#1682, "The Turkey's Done Mystery Dinner"): confirmed this is a
  traveling dinner-theater troupe that performs at whatever restaurant/hotel books them (past shows at
  the Riverview Plaza Hotel, Catalina Restaurant, etc.), not a fixed venue. Check the mobile.org
  listing for which restaurant hosts this specific Nov 21 show, then alias it, or `ignore 1682`.

**Possibly cancelled — couldn't verify either way (network-blocked, see note above); all still held:**
- #534, #542, #549, #554, #561, #567, #572 — Tuesday Teen Art Club, Mobile Museum of Art (weekly
  series, Nov 10–Dec 22). `not-cancelled 534 542 549 554 561 567 572` if the museum's calendar still
  shows the series, or `cancel` whichever specific dates are actually gone.
- #1306 — Mobile County Parks Fall Festival, Irvington Landfill, Sat Nov 14. `not-cancelled 1306` or
  `cancel 1306`.
- #1174 — Crescent Comedy Workshop, Wed Nov 18 (TicketWeb). `not-cancelled 1174` or `cancel 1174`.
- #1060 — Corks Casks and Canvas Sponsors, Eastern Shore Art Center, Fri Nov 20. Only a 2025 edition
  (Oct 25, 2025) turned up; no 2026 date confirmed. `not-cancelled 1060` or `cancel 1060`.
- #646, #1067 — Sculpting the Figure, Eastern Shore Art Center, Fri Jan 1 / Jan 8. `not-cancelled 646
  1067` or `cancel`.
- #657 — Painting with Pan Patels, Downtown Fairhope, Wed Jan 6. No record of this instructor/workshop
  found online at all. `not-cancelled 657` or `cancel 657`.

**Source alerts (reporting only, not touching collector code):**
- 92ZEW returned 37 events, expected ≥40 — could be a light week or a developing parser issue worth a
  glance.
- Mobile Chamber's pull has been failing with 403 Forbidden since before 2026-10-22 (now 3+ weeks).
  Likely blocking resolution of #1148 above and probably other Chamber events; may need updated
  auth/headers, or the site changed something on their end.
