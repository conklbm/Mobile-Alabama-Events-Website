# Review routine notes — 2026-10-30 (issue #20)

## Resolved automatically

Added 15 new venues to `data/venues.yaml` (aliases include the exact raw spelling from the issue):

- **Perdido Queen Dinner Cruises** — 1 S Water St, Berth B, Mobile, AL 36602 — https://www.fox10tv.com/2025/03/12/perdido-queen-offers-up-close-tour-featuring-ss-united-states/ (domain perdidoqueen.com)
- **RTJ Golf Trail at Magnolia Grove** — 7001 Magnolia Grove Pkwy, Mobile, AL 36618 — https://rtjgolf.com/magnoliagrove
- **Soul Caffeine** (Daphne) — 2004 US Highway 98, Daphne, AL 36526 — https://www.fox10tv.com/2026/10/19/fall-coffee-week-soul-caffeine/ (domain soulcaffeine.net)
- **Church Street Graveyard** — 359 Church St, Mobile, AL 36602 — https://www.downtownmobile.org/church-street-graveyard/
- **Mobile County Animal Shelter** — 7665 Howells Ferry Rd, Mobile, AL 36618 — https://www.mobilecountyal.gov/government/departments/animal-control/animal-shelter-contact-and-directions/
- **Via! Health, Fitness and Enrichment Center** — 1717 Dauphin St, Mobile, AL 36604 — https://www.govserv.org/US/Mobile/146150992071319/Via-Health%2C-Fitness-%26-Enrichment-Center (domain viamobile.org)
- **American Legion Post 250** — 10950 Dauphin Island Pkwy, Theodore, AL 36582 — news coverage of this exact event (Keep Mobile Beautiful / America Recycles Day, Nov 14) plus a MapQuest post listing both point here. Moderate confidence: a separate "250 Fowl River Post" IRS filing lists only a PO Box in a different zip (36605), and I could not re-fetch the original news story to double-check in this session (host not reachable). Worth a second look if this ever flags again.
- **Boys & Girls Clubs of South Alabama (Semmes)** — 3810 Wulff Rd E, Semmes, AL 36575 — https://www.mobilepubliclibrary.org/community-resources/kiwanis-boys-girls-club-south-alabama (domain bgcsouthal.org)
- **Resurrection Church** (Daphne) — 2401 Main St, Daphne, AL 36526 — https://business.eschamber.com/events/details/eggs-and-issues-state-of-the-cities-january-2023-26562 (formerly Daphne United Methodist Church)
- **Dauphin Way Baptist Church** — 3661 Dauphin St, Mobile, AL 36608 — multiple real-estate/directory listings agree (church has listed this campus for sale and may relocate)
- **Africatown Heritage House** — 2465 Winbush St, Mobile, AL 36610 — https://www.mobilecountyal.gov/africatown-heritage-house-2/
- **Satsuma City Hall** — 5464 Old Highway 43, Satsuma, AL 36572 — https://cityofsatsuma.com/wordpress/address-the-council/ (domain cityofsatsuma.com)
- **Town Center Park** (Saraland) — 712A Saraland Blvd S, Saraland, AL 36571 — https://www.mobilecountyal.gov/community_events/events/9th-annual-mistletoe-market-2025-12-13
- **The Admiral Hotel** — 251 Government St, Mobile, AL 36602 — https://www.theadmiralhotel.com/ (domain theadmiralhotel.com)
- **G & D Farms** (Wilmer) — 14170 Tanner Williams Rd, Wilmer, AL 36587 — corroborated by both a MapQuest listing and ATF/FFL federal firearms license directories (business holds an FFL at this address)

Also resolved two ambiguous matches in `overrides.yaml` (`never_merge`):
- `#1270`/`#544` — Mobile Museum of Art's "Creative Night For Two" (evening, 18+, themed) and "Family Art" (afternoon, family) are two different recurring program lines, confirmed by their different standing time slots.
- `#1284`/`#1283` — USA Men's Basketball vs. Southern Miss and USA Women's Basketball vs. Arkansas State are different teams playing different opponents.

Note: direct fetches to `mobilecountyal.gov`, `esartcenter.org`/`neoncrm.com`, `downtownmobile.org`, and several other venue/organizer sites were blocked by this session's network allowlist (DNS didn't resolve). All research above relied on WebSearch snippets and secondary sources instead of fetching those pages directly — worth knowing if a future routine run hits the same wall.

## Needs Brooks

- **`venue new-slug "Shiloh Baptist Church" ???`** — Harvest Fest 2026 (`#1317`, mobilecountyal.gov). At least three distinct "Shiloh Baptist"-named congregations exist in the Mobile area (609 S Warren St, Mobile; 717 Cleveland Rd, Saraland; "New Shiloh Missionary Baptist" at 2756 Old Shell Rd, Mobile) and I couldn't tie the event to any one of them — the county's own event page wasn't reachable from this session. If you know which one, reply: `venue shiloh-baptist-church "Shiloh Baptist Church" <City>`.

- **`venue new-slug "Piggly Wiggly" ???`** — Taste of Christmas Festival (`#1222`, Dec 6, mobilecountyal.gov). Mobile County has 11+ Piggly Wiggly stores and recurring "Taste of..." events at several of them (University Blvd, Saraland, etc.). One third-party aggregator guessed 306 South University Blvd but I couldn't independently confirm it's this festival's store, so I left it out rather than guess. If you know the store: `venue piggly-wiggly-<location> "Piggly Wiggly" <City>`.

- **`ignore 1148`** — Young Professionals of Mobile December 2026 Social has no venue name at all (source: mobilechamber.com). Nothing to research; either `ignore 1148` to drop it from the queue, or `force_publish 1148` if you want it on the site without a venue.

- **`not-cancelled 632`** / **`cancel 632`** — Hollywood in Your Pocket (iPhone Photography), Eastern Shore Art Center, Fri Nov 6. The center's registration system (esartcenter.org / neoncrm.com) was unreachable from this session (DNS blocked), so I couldn't check directly. A web search found an "ESAC: iPhone Photography" session listed for March 7–8, 2026 (different dates), but nothing tying "Hollywood in Your Pocket" specifically to this venue for Nov 6.

- **`not-cancelled 646 1067`** / **`cancel 646 1067`** — Sculpting the Figure, Eastern Shore Art Center, Fri Jan 1 and Jan 8. Same access problem. A search did surface a current-looking class listing (Kim Bernadas, Fridays 9:30am–12:30pm, $250–275, esartcenter.org product pages) that's consistent with the class still running, but I couldn't load the live page to confirm these specific January dates are still on the calendar.

If `esartcenter.org`/`*.neoncrm.com` and `mobilecountyal.gov` could be added to this session's network allowlist, the three Eastern Shore Art Center items and the two "needs Brooks" venues above would likely resolve without you.
