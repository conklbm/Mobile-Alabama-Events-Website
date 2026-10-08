# Review routine notes — 2026-10-08 (issue #8, run #13)

## Resolved automatically

**Venue aliases added to existing entries**
- `Midtown Mobile` → `central-midtown` (1260 Dauphin St, Mobile) — same event series as the existing "Central Midtown" entry (Central Midtown: Second Saturday Market).
- `701 Government Street Mobile, AL 36602` → `ben-may-main-library` — exact address match for the existing Ben May Main Library entry.
- `Mobile Symphony Orchestra 257 Dauphin Street Mobile, AL 36602` → `saenger-theatre` — 257 Dauphin St is MSO's box-office/office address (Larkins Music Center), but MSO actually performs at the Saenger Theatre, 6 S Joachim St. Source: mobilesymphony.org/plan-your-visit (via search), Wikipedia "Mobile Symphony Orchestra".

**New venues added**
- `foley-parks-and-recreation` — Foley Parks & Recreation Activity Center, 315 E Jessamine Ave, Foley, AL 36535. Source: cityoffoley.org/library-big-rigs/, fox10tv.com coverage of the Foley library's Big Rigs event.
- `the-farm-elberta` — The Farm (wedding/event venue), 24025 Miflin Rd, Elberta, AL 36530 (raw listing had a typo: "Mifflin St"). Source: Alignable/Yelp business listings; annual Fall Festival matches.
- `tractor-supply-daphne` — Tractor Supply Co. (Store #2408), 851 US Hwy 98, Daphne, AL 36526. Source: Tractor Supply's own store locator.
- `hubert-pierce-road-dirt-pit` — Hubert Pierce Road Dirt Pit (Mobile County), 1113 Hubert Pierce Rd, Mobile. Source: mobilecountyal.gov Operation Clean Sweep listings + local news coverage.
- `north-mobile-industrial-park` — North Mobile Industrial Park (old Acordis site), 12740 US Hwy 43 N, Axis, AL 36505. Source: mobilecountyal.gov Operation Clean Sweep listings (consistent across multiple years).
- `irvington-landfill` — Irvington Landfill (Mobile County), 7195 Half Mile Rd, Irvington, AL 36544. Source: mobilecountyal.gov Operation Clean Sweep listings + local news coverage.
- `lupercalia-art-gallery` — Lupercalia Art Society Gallery & Speakeasy, 358 Dauphin St, Mobile, AL 36602. Source: downtownmobile.org arts-organization listing, University of South Alabama library galleries page.
- `the-shoulder-womens-facility` — The Shoulder (Women's Facility), 6801 Three Notch Rd, Mobile, AL 36619. Source: Alabama Dept. of Mental Health provider directory, corroborated by multiple independent directories.
- `bayou-sara-baptist-church` — Bayou Sara Baptist Church, 12 Bayou Sara Ave, Saraland, AL 36571. Source: feedam.org food-pantry directory, University of South Alabama community-engagement food distribution calendar.
- `flambeaux-hall` — Flambeaux Hall, 254 St Anthony St, Mobile, AL 36603 (historic event hall tied to the Order of Myths). Source: mobilearts.org/locations/flambeaux-hall/.
- `coastal-alabama-farmers-and-fishermens-market` — 781 Farmers' Market Ln, Foley, AL 36535. Source: Alabama Dept. of Agriculture & Industries' official statewide farmers-market redemption site list (2026).
- `visionary-health-career-training-institute` — Visionary Health Career Training Institute LLC ("The V"), 101 B Villa Dr, Suite 118, Daphne, AL 36526. Source: Eastern Shore Chamber's own member listing and event page (address matches exactly).

**Ambiguous matches resolved**
- Merged (same event, duplicate source copies): `[109, 981]`, `[130, 1000]`, `[142, 1012]` — the three LoDa ArtWalk pairs are downtownmobile.org's themed names (ArtWalk: Halloween / Picture Book Month / Celebrate Christmas) duplicated by mobile-arts-council's generic "LoDa ArtWalk" feed entry, same date each time.
- Merged `[833, 798]` — "Melton Health And Faith 11th Annual..." and "11th Annual Healthy Lifestyle 5K..." are the same race; the Eastern Shore Chamber's own listing gives the full combined title. Source: business.eschamber.com event #40167, mobilecountyal.gov, fox10tv.com/wkrg.com coverage.
- Merged `[843, 496]` — "Publix Battleship 12K" and "Keesler Federal Battleship 12K" are the same annual race at USS Alabama Battleship Park with varying sponsor-title branding by source/year. Source: endurancesportswire.com, va.alabama.gov, letsdothis.com.
- Never-merge `[794, 784]` — different monthly Historical Lecture Series talks ("A Taste of Mobile" vs. "Clotilda Survivors, Living Legacy").
- Never-merge `[652, 650]`, `[656, 654]`, `[658, 654]` — different Eastern Shore Art Center classes (pottery/handbuilding/watercolors vs. acrylics), not duplicates.
- Never-merge `[495, 494]` — USS Alabama's Veterans Day Concert (evening, Mobile Pops) and Veterans Day Celebration and Parade of Flags (afternoon ceremony) are two distinct program components on the same day, confirmed consistent across multiple years of mobilecountyal.gov listings.

## Needs Brooks

- **`#932` / `#965` — The Moonlight Chasse' Ballroom Dance Society** (eastern-shore-chamber, no venue on the occurrence). This recurring series appears elsewhere to be held at Hot Wheels Skating Rink in Daphne (616 Whispering Pines Rd), but I couldn't fetch the exact Nov/Dec 2026 event pages to confirm the venue on-page (proxy blocked direct access to business.eschamber.com). Recommend: check the chamber listing yourself, then either
  `alias "The Moonlight Chasse' Ballroom Dance Society" = hot-wheels-skating-rink` (if confirmed), or let me know the right venue.

- **`#937` / `#964` — BILL-E's BACON, BURGERS, & BIKES** (eastern-shore-chamber, no venue). Couldn't confirm a specific venue — search turned up only "a monthly gathering in Fairhope" with no address, and a same-named bacon business at 19992 State Hwy 181, Fairhope, that may or may not be where this event is held. Recommend: check `https://business.eschamber.com/events/details/bill-e-s-bacon-burgers-bikes-11-06-2026-40373` directly, then
  `venue bille-s-fairhope "Bill-E's" Fairhope` (or similar) once you know the real venue.

- **`#682` — Lowes Kid Workshops- Firefighting Plane**, venue listed as "Lowes Home Improvement (Locations Vary)". Can't resolve to one address since the listing itself says locations vary. Recommend: `ignore 682` (or pick the specific Mobile-area Lowe's you want listed and I'll add it as a venue next time).

- **`#941` — Dedication & Commissioning Ceremony for The Schreiber Water Treatment Facility**, raw venue "120-B CO RD 20, Foley, AL 36535". Could not confirm a facility by this name exists at this address — no ADEM/EPA/news source found. Best guess: it may be a new Riviera Utilities water plant named for former Foley councilman Bob Schreiber (a Riviera Utilities board member through April 2024), but this is unverified. Recommend: call Riviera Utilities (251-943-5001) to confirm, then
  `venue schreiber-water-treatment-facility "Schreiber Water Treatment Facility" Foley` once confirmed, or `ignore 941` if you'd rather skip it.

Everything else in issue #8 is resolved and will re-publish automatically.
