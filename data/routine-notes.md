# Review routine notes — 2026-11-27 (issue #30)

Network note: this session could not reach `mobilecountyal.gov`, `themobmom.com`,
`business.eschamber.com`, `mobilemuseumofart.com`, `innovation-portal.com`, `mobile.org`, or
`esartcenter.app.neoncrm.com` directly (DNS blocked for this cloud session, same as issue #29).
Everything below came from web search and independent secondary sources instead.

## Resolved automatically

- **Electric Piano Parlor** → `electric-piano-parlor`, 310 Dauphin St, Mobile, AL 36602.
  Source: [MapQuest](https://startpage.mapquest.com/us/alabama/the-electric-piano-parlor-424961922)
  and a [Zola wedding vendor page](https://www.zola.com/wedding/krewedewilliams/poi) agree on the
  address; corroborated by this week's 92ZEW rundown, which is itself booking a dueling-pianos
  show there Nov 28.
- **Summer's Reverie Vintage & Antiques** → `summers-reverie-vintage-antiques`, 6710A Old Shell Rd,
  Mobile, AL 36608. Source: the shop's own
  [Facebook page](https://www.facebook.com/p/Estate-Sales-Treasures-61567805353546/) plus a
  directory listing agree on the address.
- **University of South Alabama** (generic campus, raw name had no building) →
  `university-of-south-alabama`, 307 University Blvd N, Mobile, AL 36688. Source: USA's own
  [campus map](https://aesta.southalabama.edu/campusmap/pdf_map/campusmap.pdf).
- **Main Street Daphne** → `main-street-daphne`, area venue, Daphne, AL 36526 (no street number,
  same pattern as `downtown-mobile` / `downtown-fairhope`). Source: City of Daphne's own contact
  address on [atlasalabama.gov](https://atlasalabama.gov/municipalities/daphne), plus several years
  of chamber listings describing the Daphne Christmas Parade's route along Main Street in Olde
  Towne Daphne.
- **Steele Creek Satsuma** → aliased to the existing `steele-creek-lodge` entry (368 Juniper Ave,
  Satsuma, AL 36572). Source: [City of Satsuma](https://cityofsatsuma.com/wordpress/?p=461)
  describes Steele Creek Lodge as the city's waterfront lodge/park with a boat launch — the
  natural staging point for the Satsuma Christmas Boat Parade.
- **Not cancelled #1218** (Gilded Age Christmas Tours of Richards-DAR House, Dec 4): the museum's
  own [Zeffy ticketing page](https://www.zeffy.com/en-US/ticketing/christmas-tour) is still selling
  tickets for "A Gilded Age Christmas: The Golden Gala & Christmas Tours," Dec 3–6; corroborated by
  mobile.org's December happenings blog post.
- **Not cancelled #1770** (Black Jacket Symphony 'Thriller', Saenger Theatre, Feb 13 2027): still
  listed 7:30pm on the [concerts50.com](https://concerts50.com/show/black-jacket-symphony-in-mobile-tickets-feb-13-2027)
  ticket aggregator.

## Needs Brooks

**Out of region — recommend ignoring:**
- `#1786 #1792 #1794 #1795 #1801 #1802 #1803 #1805` **TrainTastic Interactive Model Railroad
  Museum** — real place, but it's in **Gulfport, MS** (615 Pass Road, Gulfport, MS 39501), ~70
  miles west of Mobile and outside both the `mobile` and `coastal` region lists. themobmom.com
  appears to be pulling non-local content. Recommend: `ignore 1786`, `ignore 1792`, `ignore 1794`,
  `ignore 1795`, `ignore 1801`, `ignore 1802`, `ignore 1803`, `ignore 1805` — and worth asking
  themobmom to scope its feed to the Mobile Bay area.
- `#1935` **Elmer Joseph Grant VFW Post 3373** (Extreme Dwarfanator Wrestling, Ticketmaster) — the
  only VFW Post 3373 I can find is in **Pascagoula, MS**, not Alabama. Recommend: `ignore 1935`.

**Unconfirmed venues:**
- `#1812` **Mason Hills Park** (Grand Bay Country Christmas, Dec 4) — found a "Mason Hills Farm" at
  9560 Grand Bay Wilmer Rd, Grand Bay, AL, but a 2024 county listing gives a different address
  (11652 A North Wheatcroft Rd) for the same name, and I can't confirm whether "Park" is the same
  property, a different on-site area, or a different place entirely. Recommend checking
  masonhillsfarm.com, then: `venue mason-hills-park "Mason Hills Park" "Grand Bay"`.
- `#1973` **Sweet Meltdown Loxley** (Pictures With Santa, Dec 5) — Sweet Meltdown is a real ice
  cream/candy shop based in Elberta; a Loxley second location was announced for Feb 2026 but I
  can't confirm it opened or find its address. Recommend checking their Facebook, then:
  `venue sweet-meltdown-loxley "Sweet Meltdown (Loxley)" Loxley`.
- `#1222` **Piggly Wiggly** (Taste of Christmas Festival, Dec 6) — Mobile County has several Piggly
  Wiggly stores; couldn't determine which one without reaching mobilecountyal.gov directly.
  Recommend checking the county listing, then: `venue <slug> "Piggly Wiggly (<location>)" <City>`.
- `#1870` **"Location: Santa's Workshop, Alvin's Island"** (Elf Academy, Dec 12) — Alvin's Island is
  a real beach-shop chain with at least two AL locations (100 W Beach Blvd, Gulf Shores; 24949
  Perdido Beach Blvd, Orange Beach); couldn't tell which store this Eastern Shore Chamber listing
  means without reaching business.eschamber.com directly. Recommend checking the chamber page, then:
  `venue <slug> "Alvin's Island (<location>)" <City>`.

**Blank venue field at source — can't alias:**
- `#1527` **Christmas Tour of Homes** (Dec 5, eastern-shore-chamber) — `venue_name_raw` is blank.
  Closest candidate is Hope Blooms Fairhope's annual Christmas Home Tour (multiple private homes,
  no single venue), but I can't confirm this listing is that tour. If Brooks confirms it's a
  no-single-venue home tour: `force_publish 1527`.
- `#1148` **Young Professionals of Mobile December 2026 Social** (Dec 10, mobilechamber) —
  `venue_name_raw` is blank. YP of MOB socials rotate venues monthly (Mobile Chamber, Spanish Fort,
  Flight Works, etc.); I can't confirm December's location. If Brooks can check
  my.mobilechamber.com for the venue: `venue <slug> "<venue>" <City>`; otherwise `force_publish 1148`.

**Ambiguous match:**
- `#1966` **First Fairhope's Breakfast With Santa** ↔ `#1965` **Breakfast at the Manger** — Fairhope
  United Methodist Church runs an annual "Breakfast at the Manger" (pancakes, crafts, Santa visit,
  nativity story) on a Saturday in early December. "First Fairhope" could be shorthand for that
  church's event, but I couldn't confirm it (vs. a distinct First Baptist Church of Fairhope event
  — I found no evidence one exists). If Brooks knows "First Fairhope" = Fairhope UMC:
  `merge 1966 1965`; otherwise `never-merge 1966 1965`.

**Possibly-cancelled items I couldn't verify** (organizer sites unreachable from this session;
web search didn't surface next year's specific listing). All are recurring annual/weekly/monthly
events that are plausibly still happening — worth a quick glance rather than a deep check:
- `#554 #561 #567 #572` Tuesday Teen Art Club, Mobile Museum of Art (weekly) — `not-cancelled <id>`
  for each if still on mobilemuseumofart.com's class calendar.
- `#961 #1532` Fairhope First Friday Art Walk, Downtown Fairhope (monthly, long-running) —
  `not-cancelled <id>` if still on the chamber calendar.
- `#1224` 'A Christmas Story' in the Park, Azalea City Golf Course, Dec 5.
- `#642` December Woodfire, Eastern Shore Art Center, Dec 5.
- `#1221` 7th Annual Port City Volley Jolley Christmas Volleyball Tournament, Mobile Convention
  Center, Dec 11 — this is an established annual tournament (6 prior years found); likely just not
  posted for 2026 yet.
- `#1210` Semmes Christmas Parade, Dec 12 — found only a 2025 date; no 2026 confirmation.
- `#463 #1125` Women Powered by AI, Innovation Portal — couldn't find this program at all via
  search; worth confirming it's still a going concern.
- `#646 #1067` Sculpting the Figure, Eastern Shore Art Center.
- `#657` Painting with Pan Patels, Eastern Shore Art Center.
- `#1229` 9th Annual King Cake-Off, Mobile Convention Center, Jan 15 2027 — established annual
  event (8 prior years), likely just not posted for 2027 yet.
- `#1230` 'STEEL MAGNOLIAS', Joe Jefferson Playhouse, Jan 15 2027.
- `#1322` Semmes Camellia Festival 2027, Boys & Girls Clubs of South Alabama — established annual
  event; likely just not posted for 2027 yet.
- `#1853` STEM Wonderland, Gulf Coast Exploreum — only a 2021–22 edition turned up; worth confirming
  this is a recurring program before trusting the 2027 date.

**Source alert:** themobmom.com is feeding at least 8 Gulfport, MS events (TrainTastic) into the
queue this run — see "Out of region" above. Not fixing the collector per the rules, just flagging it.
