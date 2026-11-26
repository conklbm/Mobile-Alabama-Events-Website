# Routine notes — 2026-11-26 (issue #29)

## Resolved automatically

**New venues added to `data/venues.yaml`:**

- **Gulf Shores Public Library** — 221 W 19th Ave, Gulf Shores, AL 36542. Officially Thomas B. Norton Public Library. Source: [gulfshoresal.gov](https://gulfshoresal.gov/1551/About-the-Library), city library directory listings.
- **Tillman's Corner Community Center** — 5055 Carol Plantation Rd, Mobile, AL 36619. Source: MapQuest/coparking.ch business listings (no single official county page found, but two independent directories agree).
- **Eastern Shore Lanes** — 10460 Eastern Shore Blvd, Spanish Fort, AL 36527. Source: eslanes.com, BMO branch directory, bowling-alley listings.
- **Mobile Government Plaza** — 205 Government St, Mobile, AL 36602. Source: Wikipedia, mobilecountyal.gov.
- **The Historic Oakleigh House Museum** — 350 Oakleigh Place, Mobile, AL 36604. Source: historicmobile.org, mobile.org listing, AAA. Kept as a separate entry from the existing `cox-deasy-cottage-at-historic-oakleigh` since it's a distinct building (the main house vs. the cottage) on the same historic complex.
- **California Dreaming (Spanish Fort)** — 30500 State Hwy 181, Spanish Fort, AL 36527. Source: AAA TripCanvas, Toast/OpenTable listings.
- **Daphne Middle School** — 1 Jody Davis Cir, Daphne, AL 36526. Source: Baldwin County Board of Education (bcbe.org), SchoolDigger.
- **W.C. Griggs Elementary School** — 6001 Three Notch Rd, Mobile, AL 36619. Source: Mobile County Public Schools directory (via hometownlocator/SchoolDigger).
- **Garrett Park (Robertsdale)** — 18080 Pennsylvania St, Robertsdale, AL 36567. Source: City of Robertsdale parks listing (via MapQuest/Vymaps).
- **Honeybee Park (Robertsdale)** — 22780 State Hwy 59 N, Robertsdale, AL 36567. Source: Gulf Coast Media coverage of the park's renovation/dedication, cross-checked against a dog-park directory giving the same street number.
- **Bishop State Community College** — 351 N Broad St, Mobile, AL 36603 (Downtown Campus). Source: bishop.edu locations page.

**Aliases added to existing entries:**
- `"Spanish Plaza"` → `spanish-plaza-park` (same park, 401 Government St; the raw name just dropped "Park").
- `"Barnes & Noble"` → `barnes-noble-mobile` (same store, 3930 Airport Blvd; raw name just dropped "(Mobile)").

**Overrides applied in `data/overrides.yaml`:**
- `not_cancelled: 1085` — Trae Crowder (Two Shows), Crescent Theater, Jan 8 2027: still listed with active ticket pricing ($44.10–$162.18) on mobilecountyal.gov's own event page as of today.
- `merge: [1085, 1995]` — same Trae Crowder booking: mobile-county's "Two Shows" listing and downtown-mobile-alliance's "Early Show" listing are the same event (matches the pattern of prior weeks' merges for this recurring booking).
- `never_merge: [2009, 2008]` — USA basketball: Men's vs. Louisiana Monroe and Women's vs. Louisiana Lafayette are different teams and different opponents, not a duplicate.

Ran `uv run pytest -q` (69 passed), validated both YAML files, and reprocessed: all items above dropped out of the review queue; nothing else changed.

## Needs Brooks

**Likely out of scope — events outside the Mobile Bay coverage area:**
- `venue "traintastic-interactive-model-railroad-museum" "TrainTastic Interactive Model Railroad Museum" "Gulfport, MS"` — this is the themobmom source pulling in a Mississippi Gulf Coast attraction (615 Pass Road, Gulfport, MS), ~70 miles from Mobile and not in either the core or outer ring. 8 occurrences this run (`#1786, #1792, #1794, #1795, #1801, #1802, #1803, #1805`). Recommend: `ignore 1786 1792 1794 1795 1801 1802 1803 1805`, and consider whether themobmom needs a region filter so this doesn't recur weekly.
- `ignore 1935` — **Extreme Dwarfanator Wrestling** at "Elmer Joseph Grant VFW Post 3373": this VFW post is in **Pascagoula, Mississippi**, not Mobile — Ticketmaster's venue data is misleading here. Same out-of-region question as TrainTastic.

**Unconfirmed addresses (couldn't verify well enough to add):**
- `venue summers-reverie "Summer's Reverie Vintage & Antiques" Mobile` — no web listing found at all for this shop. `#1998`. If you know where it is, send the alias command; otherwise it may be new/very small.
- `venue mason-hills-park "Mason Hills Park" "Grand Bay"` — raw name doesn't match anything I could confirm. The nearest hit is "Mason Hills Farm" at 9560 Grand Bay Wilmer Rd (hosted an unrelated October event), but Mobile County's own listings for past "Grand Bay Country Christmas" editions place that event at Grand Bay Community Church, 12575 US-90 instead. `#1812`. Worth a look before adding either address.
- `venue main-street-daphne "Main Street Daphne" Daphne` — couldn't confirm this is a real organization distinct from the City of Daphne itself; one aggregator gives 1705 Main St but I couldn't verify it independently. `#2015` (City of Daphne Christmas Parade).
- `venue sweet-meltdown-loxley "Sweet Meltdown" Loxley` — confirmed the Elberta location (25054 State St) but the Loxley location was only "planned for Feb 2026" as of the last news I found; no address yet. `#1973`.
- `venue steele-creek-satsuma "Steele Creek" Satsuma` — no address found for a Steele Creek boat-parade site; note Satsuma actually *cancelled* its boat parade in at least one recent year. Don't confuse with the existing `steele-creek-lodge` entry (368 Juniper Ave), which appears to be a different place. `#1988`.
- `ignore 1222` or `venue ... "Piggly Wiggly" ...` — "Taste of Christmas Festival" at a bare "Piggly Wiggly": there are several Piggly Wiggly stores in the area (University Blvd, Saraland Blvd) and I couldn't confirm which one hosts this. `#1222`.
- `venue alvins-island-santas-workshop "Alvin's Island (Santa's Workshop)" ???` — raw text is "Location: Santa's Workshop, Alvin's Island." Alvin's Island has stores in both Gulf Shores (100 W Beach Blvd) and Orange Beach (24949 Perdido Beach Blvd); couldn't tell which hosts the seasonal "Santa's Workshop" display. `#1870` (Elf Academy, Dec 12).
- `#1789, #1527, #1148` — "University of South Alabama" (generic, no building), and two blank-venue items (Christmas Tour of Homes; Young Professionals of Mobile Social). Too broad/empty to guess a specific building or venue; may be `force_publish` candidates like past blank-raw-field cases if you know the real venue.

**Ambiguous match — genuine judgment call:**
- `merge 1966 1965` or leave separate — **"First Fairhope's Breakfast With Santa"** (themobmom) vs. **"Breakfast at the Manger"** (Dec 5/6, Downtown Fairhope). Fairhope United Methodist Church runs an annual "Breakfast at the Manger" pancake-and-Santa event each December. "First Fairhope" plausibly refers to the same church, but it could also mean a different congregation (e.g. First Baptist Fairhope) running its own separate event. I couldn't find a primary source confirming either way for 2026.

**Possibly-cancelled items left unresolved (recurring series, no clear confirmation either way):**
These are all weekly/monthly recurring programs where the primary source simply doesn't list that far out yet — I couldn't find independent confirmation either way via search (direct site fetches were blocked by this session's network policy):
- `not-cancelled 549 554 561 567 572` — Tuesday Teen Art Club, Mobile Museum of Art (weekly).
- `not-cancelled 961 1532` — Fairhope First Friday Art Walk (monthly).
- `not-cancelled 463 1125` — Women Powered by AI, Innovation Portal (recurring).
- `not-cancelled 646 1067` — Sculpting the Figure, Eastern Shore Art Center (recurring class).
- `not-cancelled 657` — Painting with Pan Patels, Eastern Shore Art Center.
- `cancel 1293` or `not-cancelled 1293` — LAREDO at The Merry Widow, Nov 29: couldn't find this specific show listed anywhere; the venue's calendar shows other November/December shows but not this one.

**Source alerts (no action taken, per instructions):**
- 92ZEW: 33 events vs. expected 40+.
- City of Gulf Shores: 1 event vs. expected 2+.
- Mobile Chamber: pull failing with 403 Forbidden, no successful pull since 2026-10-22 (now over a month).
- Mobile SPCA: pull failing with 401 Unauthorized.
