# Review routine notes — 2026-10-22 (issue #12, run #17)

## Resolved automatically

- **Carol Hodgson Arena** (Bay Minette) — 43420 Pine Grove Road, Bay Minette, AL 36507. City-owned equestrian arena. Source: https://cityofbayminetteal.gov/recreation/carol-hodgson-arena (third-party sites give 43421; the city's own page is the tiebreaker).
- **Honor Park** (`City of Semmes Honor Park`, `Honor Park`) — 4100 Wulff Road East, Semmes, AL 36575. Source: cityofsemmesal.gov.
- **Saraland Municipal Complex** — Saraland Blvd S, Saraland, AL 36571 (no street number added — the city's own site gives two conflicting numbers, 943 and 727; didn't want to guess between them). Source: saraland.org/government, saraland.org/contact, FOX10 (opened June 2025).
- **Tricentennial Park** — Frederick D. Richardson Jr. Tricentennial Park, 2121 Bragg Ave, Mobile, AL 36617. Source: cityofmobile.gov/parks-rec.
- **Corpus Christi Catholic School** — 6300 McKenna Dr, Mobile, AL 36608. Source: FOX10 (Oct 2026), GCatholic parish directory.
- **Grand Bay Library** — 10329 Freeland Ave, Grand Bay, AL 36541. Source: mobilepubliclibrary.org.
- **National Museum of Naval Aviation** — 1750 Radford Blvd, Suite C, NAS Pensacola, FL 32508. Source: navalaviationmuseum.org.
- **Virginia Dillard Smith/Toulminville Branch Library** — 601 Stanton Rd, Mobile, AL 36617. Source: mobilepubliclibrary.org.
- **First Baptist Church of Mobile** (aliases `First Baptist Church of Mobile` and `First Baptist Church Mobile`, both referring to the same Octubafest listing) — 806 Government St, Mobile, AL 36602. Source: downtownmobile.org, GCatholic-style directory listing. Distinct from "First Baptist Church North Mobile" in Saraland.
- **Baldwin County Commission Central Annex Auditorium** — the raw venue string already carried the full address (22251 Palmer St, Robertsdale, AL 36567); confirmed as a real county meeting auditorium via baldwincountyal.legistar.com.
- **Azalea City Golf Course** — 1000 Gaillard Dr, Mobile, AL 36608. Source: cityofmobile.gov/parks-rec.
- **St. Mary's Catholic Church** (raw: `St. Mary's Parish`) — 1453 Old Shell Rd, Mobile, AL 36604. Source: parish-directory listings (catholicclocks.com, gcatholic.org).
- **254 St. Anthony Street** → added as an alias of the existing `flambeaux-hall` entry (same address already on file as "254 St. Anthony St., Mobile").

12 venue entries added/aliased; re-processing dropped the queue from 27 items to 15.

## Needs Brooks

- **`approve/alias` — Ina Pullen Smallwood Memorial Library** (#1228, Book Character Costume Contest, mobile-county). Couldn't find this library anywhere — not in Mobile County's library system, not elsewhere. Might be a typo, a defunct name, or a source error. Recommend: call Mobile County or check the source page directly for a physical address, then `venue <slug> "Correct Name" City` — or `ignore 1228` if it can't be pinned down.
- **`alias "McDonald's – Airport Boulevard" = <slug>`** (#1207, McDonald's Harvest Party, themobmom). There are multiple McDonald's on Airport Blvd in Mobile; couldn't determine which one from the listing. Recommend checking themobmom.com's event page for a specific address, then `venue mcdonalds-airport-blvd "McDonald's (Airport Blvd)" Mobile`.
- **`venue <slug> "Empanola Mobile" Mobile`** (#1225, Coffee & Chat, mobile-county). Empanola (an empanada chain based in New Orleans) does appear to have opened a Mobile location — it's listed on Uber Eats under Mobile, AL — but I couldn't find a street address from any source. Recommend: `venue empanola-mobile "Empanola" Mobile` once you have the address, or `ignore 1225`.
- **`venue <slug> "Piggly Wiggly ___" ___`** (#1222, Taste of Christmas Festival, mobile-county). "Piggly Wiggly" alone is ambiguous — there are several in the area (e.g. 306 S University Blvd in Mobile, and one in Saraland) and neither is confirmed as this one. Recommend checking the mobilecountyal.gov listing directly, then `venue <slug> "Piggly Wiggly (___)" ___`, or `ignore 1222`.
- **`ignore 1209` or `force-publish 1209`** — City Fest (Fall Family Festival), Oct 25, blank venue (themobmom). I suspected this is Saraland's annual CITYFEST, hosted at Saraland Church (already in venues.yaml) — but couldn't confirm it from any source. If you know it's the same event, `force-publish 1209` is the right move (same pattern as the other blank-venue Eastern Shore Chamber items already in overrides.yaml); otherwise `ignore 1209`.
- **`ignore 1148`** — Young Professionals of Mobile December 2026 Social, blank venue (mobilechamber.com). Couldn't confirm this event is even on the Chamber's calendar yet (searches only turned up a May 2026 YP joint social at a different venue) — may not be fully scheduled. Suggest leaving it held until the Chamber's page fills in a venue, or `ignore 1148` for now.
- **`merge [1171, 997]` or `never-merge 1171 997` (and same for 1174/1004, 1176/1009, 1179/1016)** — Crescent Comedy Workshop (ticketweb, Wed 5:30 PM) vs. Crescent Theater: Crescent Comedy Chaos (mobile-arts-council, Wed 7:00 PM), both recurring on the same four Wednesdays (Nov 4, Nov 18, Dec 2, Dec 16) at Crescent Theater. Could be one program double-listed with a time error on one side, or two genuinely separate offerings (a comedy workshop/class followed by the evening show). I couldn't settle it from the web — recommend checking crescenttheater.com's own calendar or calling the theater.

## FYI (not a queue item, no action taken)

- #1208 **Boo Bash 2026** at Corpus Christi Catholic School is listed for Oct 25, but FOX10 (Oct 5, 2026) reported the school's actual Boo Bash/trunk-or-treat happened **Oct 10, 2026**. The themobmom listing may be stale. Not a pipeline-flagged item (venue only), so I resolved the venue but didn't touch the date/listing. If you want it pulled: `ignore 1208`.
