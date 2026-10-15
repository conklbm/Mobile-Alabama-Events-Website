# Review routine notes — 2026-10-15 (issue #10, run #15)

28 items were queued. 21 resolved automatically below; 7 remain for Brooks.

## Resolved automatically

**New venues added to `venues.yaml`**
- **Sweet Dreams Haunted Attraction** (`sweet-dreams-haunted-attraction`) — 811 St. Francis St., Mobile, AL 36602 (`#1094`/`#1095`/`#1096`). Seasonal haunted house in a downtown warehouse behind Moe's BBQ. Source: [Mobile County event listing](https://www.mobilecountyal.gov/community_events/sweet-dreams-haunted-attraction-2022-10-01/) + [WKRG coverage](https://digital-release.wkrg.com/whats-working/new-haunted-house-terrifies-guests-in-downtown-mobile/).
- **Richards-DAR House Museum** (`richards-dar-house`) — 256 N. Joachim St., Mobile, AL 36603 (`#1101`). Source: [Wikipedia / Library of Congress record](https://en.wikipedia.org/wiki/Richards_DAR_House), [Encyclopedia of Alabama](https://encyclopediaofalabama.org/article/richards-dar-house-museum/).
- **Manci's Antique Club** (`mancis-antique-club`) — 1715 Main St., Daphne, AL 36526 (`#1113`). Source: [iExit directory listing](https://www.iexitapp.com/guide/Alabama/1/Daphne/484) + Eastern Shore Chamber item on the building's centennial.
- **The Bull** (`the-bull-spanish-fort`) — 30500 State Highway 181, Suite 134, Spanish Fort, AL 36527 (`#1114`). Source: three independent [Eastern Shore Chamber "Networking at Noon" listings](https://business.eschamber.com/events/details/networking-at-noon-the-bull-40627) at this exact address across 2024–2026.
- **Whataburger (Daphne)** (`whataburger-daphne`) — 7280 Lavender Lane, Daphne, AL 36526 (`#1116`). Source: Eastern Shore Chamber's own ribbon-cutting announcement for this store.
- **Stanky Field** (`stanky-field`) — 307 N. University Blvd., Mobile, AL 36608 (`#1048`/`#1049`/`#1051`/`#1052`/`#1053`). USA's baseball stadium. Source: [Wikipedia](https://en.wikipedia.org/wiki/Eddie_Stanky_Field) + [Mobile Sports Authority](https://mobilesportsauthority.com/facilities/stanky-field-university-of-south-alabama). Note: USA's own athletics site gives a different address (Old Shell Road) for driving directions — worth a look if a ticket/map link ever surfaces, but two independent sources agree on 307 N. University Blvd. for mail/record purposes.

**Aliases added to existing venues**
- `"Mobile Symphony Orchestra"` → `saenger-theatre` (`#1100`/`#1102`). MSO's Nov 7 "Beethoven & Blue Jeans" and Dec 12 "Swing into the Holidays" both confirmed at the Saenger Theatre (257 Dauphin St is MSO's office, not the concert hall — same correction the routine made for a longer raw string two weeks ago).
- `"Oct 10-Nov 14"` → `cathedral-square` (`#1098`, Fall Market in the Park). The raw venue field is a mis-scraped date range; the market itself runs Saturdays at Cathedral Square. Source: [FOX10 City of Mobile October events](https://www.fox10tv.com/2026/10/01/city-mobile-october-events/), [TheCraftMap listing](https://www.thecraftmap.com/fair/fall-market-in-the-park-mobile-al).
- `"City of Mobile Special Events Department"` → `downtown-mobile` (`#1107`, LoDa ArtWalk celebrates Halloween). Confirmed in downtown Mobile / LoDa (Dauphin St, Cathedral Square) via [FOX10](https://www.fox10tv.com/2026/09/24/celebrate-halloween-loda-artwalk/) and cityofmobile.gov.
- `"Opening reception at ArtWalk"` → `downtown-mobile` (`#1111`, Coastal Curated). Couldn't independently confirm the specific gallery, but the raw text itself places it at the same monthly downtown ArtWalk.

**Blank-venue items force-published** (`overrides.yaml` → `force_publish`) — `venue_name_raw` is empty at the source for these, so no alias can match (same collector gap the routine flagged on 2026-10-09/10-08, still unfixed upstream):
- `#932` / `#965` — The Moonlight Chasse' Ballroom Dance Society. Confirmed via business.eschamber.com (multiple years) at Hot Wheels Skating Rink, Daphne — already in `venues.yaml`.
- `#937` / `#964` — BILL-E's Bacon, Burgers, & Bikes. Confirmed real event at Bill-E's, Fairhope — already in `venues.yaml`.
- `#1083` — Fall Break & Halloween Celebration at Maxim Tokyo Claw Village (themobmom). Confirmed real business ("Maxim Tokyo Claw," a claw-machine arcade on Cottage Hill Rd, Mobile — [FOX10](https://www.fox10tv.com/2026/06/25/maxim-tokyo-claw/)), but I couldn't independently confirm the exact street number/zip, so no `venues.yaml` entry yet — just force-published so the event isn't held on a venue I can't verify.

**Merge / never-merge calls** (`overrides.yaml`)
- `merge: [1086, 835]` — 6th Annual Mobile Latin Fest. The Oct 10 date was postponed to Oct 18 (Tropical Storm Isaias) per [FOX10](https://www.fox10tv.com/2026/10/07/mobile-latin-fest-postponed-until-oct-18/); `#835`'s "RESCHEDULED" copy is the same event at the same Mardi Gras Park.
- `never_merge: [1055, 615]` — South Alabama Men's Basketball vs. Old Dominion and Women's Basketball vs. Marshall are different teams playing different opponents.

## Needs Brooks

- **`#192` Adult Talent Show, Crescent Theater, Sat Oct 24** — still flagged possibly-cancelled (now a third run in a row; this has been open since issue #9). I could not find the TicketWeb listing or any other current source confirming it one way or the other.
  → `cancel 192` if you know it's off, or `not-cancelled 192` if it's still on.

- **`#1108` Panini Senior Bowl Ticket Launch + Rip Event, Thu Oct 15** — raw venue is just "Senior Bowl." I confirmed Panini America is the Senior Bowl's title sponsor and found a separate jersey-reveal event at Dick's House of Sport, but nothing naming a location for this specific ticket-launch/card-rip event.
  → `venue slug "Venue Name" City` once you know where it's held (or `ignore 1108` if it's not worth a venue page for a one-off).

- **`#1119` Peter Pan Goes Wrong, Wed Nov 11, raw venue "Monte L. Moorer Theatre; 161 Dogwood Lane, Mobile, AL, 36608"** — I could not confirm this venue. 161 Dogwood Lane matches an attorney's office in a business directory, not a theatre. The only "Moorer" connection I found in Mobile is the unrelated Dr. Monte L. Moorer Library branch. This may be a small/private venue not well indexed, or the address in the source listing (mobilearts.org) may itself be wrong.
  → `venue slug "Monte L. Moorer Theatre" Mobile` if you can confirm the address, or `ignore 1119`.

- **`#1085` Trae Crowder (Two Shows) vs. `#1076` Trae Crowder (Early Show)** — same comedian, same venue (Crescent Theater), same night (Fri Jan 8). A county listing describes one booking as 7 PM + 9 PM ("Two Shows"); the other listing may be specifically the 7 PM slot, or may be a duplicate of the same booking. I couldn't tell from available listings whether these are the same ticketed event described two ways, or two distinct showtimes that should stay separate.
  → `merge 1085 1076` if they're the same booking, or `never-merge 1085 1076` if they're genuinely separate shows.

- **Blank-venue collector gap (recurring)** — eastern-shore-chamber listings keep coming through with an empty venue field (Moonlight Chasse', BILL-E's, and now this week's Maxim Tokyo Claw item). I've been force-publishing each occurrence individually since the venues are known and real, but this will keep recurring every time these series post a new date. Worth a look at the collector itself at some point (not something I can fix from `venues.yaml`/`overrides.yaml`).
