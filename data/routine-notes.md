# Routine notes — 2026-11-27

**Network note (read this first):** this run's cloud sandbox blocked outbound DNS to every one
of the actual source domains — `mobilecountyal.gov`, `themobmom.com`, `business.eschamber.com`,
`mobile.org`, `my.mobilechamber.com`, `mobilesaenger.com`, `pensacolasaenger.com`,
`mobilemuseumofart.com`, `esartcenter.org`, `innovation-portal.com`, `exploreum.com`,
`richardsdarhouse.com`, `cityofsemmesal.gov` all failed with DNS resolution errors (confirmed
directly, not just by the research agents). Everything below came from WebSearch snippets of
secondary sources (news, ticket aggregators, directories) instead of the primary pages the
routine normally reads. That's why so much more than usual landed in "Needs Brooks" this run —
if this session's network allowlist is fixed, most of these are worth a quick re-check straight
against the source page rather than treated as settled by this write-up.

## Resolved automatically

No new venues were added to `data/venues.yaml` this run — every "unknown venue" below came back
uncertain once the primary source was unreachable, and the standing rule is not to guess.

17 "possibly cancelled" occurrences were confirmed **still happening** via independent
corroborating sources (news coverage, official ticketing pages, race-registration sites, or
multiple ticket resellers agreeing) and added to `not_cancelled` in `data/overrides.yaml`:
215, 217, 218, 220, 368, 779, 780, 799, 214, 773, 743, 767, 1223, 784, 1473, 1087, and one marked
**cancelled** (no trace anywhere on its venue's otherwise well-indexed calendar): 1293 (LAREDO,
The Merry Widow, Nov 29).

| id | event | venue | evidence |
|---|---|---|---|
| 215 | Get the Led Out | Saenger Theatre (Mobile) | still listed 7:30pm Dec 5 on multiple ticket resale sites |
| 217 | Jodeci 35th Anniversary Tour | Saenger Theatre (Mobile) | still listed 7:30pm Dec 6, TickPick/Live Nation/Stereoboard agree |
| 218 | A Celtic Christmas by a Taste of Ireland | Saenger Theatre (Mobile) | still listed 7:30pm Dec 9, gametime.co/eventticketscenter agree |
| 220 | Bill Gaither and the Gaither Vocal Band | Cottage Hill Baptist Church | still listed there — StubHub/happeningnext/vividseats/concerts50 agree |
| 368 | Motown Christmas | Saenger Theatre (Pensacola) | still listed 7pm Nov 28 on HelloTickets (marked Sold Out) |
| 779 | 'Cinderella' | Saenger Theatre (Mobile) | still listed 7pm Jan 6 '27 on mobilecountyal.gov (via search cache) |
| 1077 | Eddie B tour | Saenger Theatre (Mobile) | still listed 8pm Jan 9 '27 on mobilecountyal.gov (via search cache) |
| 780 | Biggest Little Holiday Party | Mobile Convention Center | still listed 5-9pm Dec 4 on mobilecountyal.gov (via search cache) |
| 799 | Wheels and Reels Drive-In Movies | Mobile Flea Market | still listed on City of Mobile's own events page, Dec 4, 6-10pm |
| 214 | Hunter Flynn: Back to My Roots Tour | Soul Kitchen Music Hall | tour press release (Shore Fire Media) + Rate Your Seats agree, Dec 4 |
| 773 | South Mobile County Operation Clean Sweep | Irvington | Mobile County's own fall-schedule press release, Dec 5 |
| 743 | A Walk to Remember in December | Semmes Walking Trail | active RunSignUp registration + Nov 16 '26 Fox10 article |
| 767 | Winter Craft Fair | Providence Presbyterian Church | mobilecountyal.gov listing (via search cache) + TheCraftMap, Dec 5 |
| 1223 | Lighting Up Midtown Festival | St. Mary's Catholic Church | St. Mary's own Zeffy ticketing page, Dec 5 |
| 784 | Historical Lecture Series: Clotilda Survivors | Cox-Deasy Cottage | mobilecountyal.gov + historicmobile.org both list it, Dec 13 |
| 1473 | Project Homeless Connect 2027 | The Grounds | named in a Nov 19 '26 Fox10 article on the event, Jan 29 '27 |
| 1087 | Walters Controls Mobile Marathon | Mardi Gras Park | mobilecountyal.gov + mobilesportsauthority.com + RunSignUp, Jan 10 '27 (current listings brand it "2027") |
| 1293 | LAREDO | The Merry Widow | **cancelled** — venue's full Nov/Dec calendar is well-indexed across ticket aggregators with no gap for this act/date; appears pulled |

## Needs Brooks

### Unknown venues
- `#1998` **Annual Christmas Sip n' Shop**, Dec 3 — raw venue "Summer's Reverie Vintage & Antiques". No business by that name turns up anywhere in search (Google/directories/BBB). Could be home-based or a pop-up only named on mobile.org's own page (unreachable this run). → `ignore 1998` for now, or re-check https://www.mobile.org/event/annual-christmas-sip-n-shop/24484/ directly.
- `#1786 #1792 #1794 #1795 #1801 #1802 #1803 #1805` **Holiday Lights at TrainTastic / The Polar Experience at TrainTastic** (recurring, themobmom source) — confirmed real: TrainTastic Interactive Model Railroad Museum, 615 Pass Road, **Gulfport, MS** 39501. This is outside every region bucket in the rules (not Alabama) — a scope call, not a data problem. → if these belong on the site: `venue traintastic-gulfport "TrainTastic Interactive Model Railroad Museum" Gulfport` (you'll need to say which regions list to give it, since "coastal" per the PRD means Alabama/Pensacola coast); if not: `ignore` all eight.
- `#1812` **Grand Bay Country Christmas**, Dec 4 — raw venue "Mason Hills Park". Two candidates, neither confirmed for this event: Mason Hills Farm (9560 Grand Bay Wilmer Rd, Grand Bay AL 36541) or Grand Bay Community Church (12575 US-90, Grand Bay AL 36541, used for a same-named 2024 event). → `venue mason-hills-farm "Mason Hills Farm" "Grand Bay"` if (a) is right, otherwise tell me and I'll use the church.
- `#1789` **Pancakes & PJ's with SantaPaws and Miss Pawla**, Dec 5 — raw venue "University of South Alabama", no specific building confirmed (a 2023 USA press release confirms the event exists annually but names no venue). Don't want to guess among the site's existing Mitchell Center / Student Center / Marx Library / SGA Pavilion / Archaeology Museum entries. → check themobmom's page directly, then `alias "University of South Alabama" = <correct-existing-slug>`.
- `#1527` **Christmas Tour of Homes**, Dec 5 — blank venue at source; a "tour of homes" is almost certainly multi-stop with no single address. → `ignore 1527`, or if you know the ticket-pickup location I'll add it.
- `#2015` **City of Daphne Christmas Parade - 2026**, Dec 5 — raw venue "Main Street Daphne"; it's a parade route, not a venue. Best staging-area candidate from past years is Daphne Civic Center (2603 US-98, Daphne AL 36526) but not confirmed for 2026. → `venue daphne-civic-center "Daphne Civic Center" Daphne` if that's right, or tell me the actual start point.
- `#1973` **Pictures With Santa**, Dec 5 — raw venue "Sweet Meltdown Loxley". Sweet Meltdown is a real ice-cream/candy chain based in Elberta, AL, with a second Loxley location reportedly opened/opening ~early 2026 — street address for the Loxley store not found. → `ignore 1973` until the Loxley address is confirmable, or give me the address if you know it.
- `#1988` **Satsuma Christmas Boat Parade**, Dec 5 — raw venue "Steele Creek Satsuma". Steele Creek Park boat ramp on Bayou Sara is real but directories disagree on the street number (368 vs. 499 Juniper Ave, Satsuma AL 36572); one 2025-season report also said Satsuma's boat parade was cancelled that year. → confirm both the address and that it's actually running this year before I add it.
- `#1222` **Taste of Christmas Festival**, Dec 6 — raw venue "Piggly Wiggly". Several Piggly Wiggly stores in the Mobile area; couldn't tell which one. → tell me the store/address and I'll add it.
- `#1935` **Extreme Dwarfanator Wrestling**, Dec 8/9 — raw venue "Elmer Joseph Grant VFW Post 3373". That post is real but registered in **Pascagoula, MS**, not Alabama — worth double-checking the Ticketmaster listing isn't actually for a similarly-numbered Alabama post before treating this as out-of-area. → check Ticketmaster directly, then either `ignore 1935` (out of area) or give me the correct AL address.
- `#1148` **Young Professionals of Mobile December 2026 Social**, Dec 10 — blank venue at source; Mobile Chamber's own calendar page is unreachable from here (and already flagged elsewhere as a broken pull — see Source alerts). Best guess, unconfirmed: the Chamber's own building (451 Government St, Mobile AL 36602). → `venue mobile-chamber "Mobile Chamber" Mobile` if that's right, or check the Chamber's calendar directly.
- `#1870` **Elf Academy**, Dec 11/12 — raw venue "Santa's Workshop, Alvin's Island". Alvin's Island has three AL stores (Gulf Shores, Orange Beach, Foley) and I couldn't tell which one hosts this. → tell me which store and I'll add it, e.g. `venue alvins-island-gulf-shores "Alvin's Island" "Gulf Shores"`.

### Possibly cancelled (couldn't confirm either way — primary sources unreachable this run)
- `#554 #561 #567 #572` **Tuesday Teen Art Club**, Mobile Museum of Art, Dec 2/9/16/23 — no corroborating listing found anywhere for this specific class name; museum's own site unreachable. → `not-cancelled 554 561 567 572` if you know it's still running, else `cancel`.
- `#1218` **Gilded Age Christmas Tours of Richards-Dar House**, Dec 4 — the museum's Zeffy page shows a recurring Dec 3-6 Christmas tour window but doesn't confirm the year. → `not-cancelled 1218` or `cancel 1218`.
- `#961 #1532` **Fairhope First Friday Art Walk**, Dec 4 '26 / Jan 1 '27 — long-running monthly series, but no Dec-specific listing found, and last December it was reportedly skipped for the Fairhope Christmas parade; Jan 1 is New Year's Day. → check with the Chamber/downtown Fairhope directly, then `not-cancelled` or `cancel` each.
- `#1224` **'A Christmas Story' in the Park**, Azalea City Golf Course, Dec 4 — zero trace found anywhere (only an unrelated 2025 Saenger event with a similar name). Absence is suggestive but not a confirmed cancellation. → `cancel 1224` if you agree it looks gone, else `not-cancelled 1224`.
- `#642 #646 #1067` **December Woodfire / Sculpting the Figure (x2)**, Eastern Shore Art Center — no corroborating source found; ESAC's own site unreachable this run. → `not-cancelled` or `cancel` each once you check esartcenter.org.
- `#657` **Painting with Pan Patels**, Eastern Shore Art Center, Jan 6 '27 — instructor name doesn't turn up anywhere in search. → same, check ESAC's site directly.
- `#1221` **7th Annual Port City Volley Jolley Christmas Volleyball Tournament**, Mobile Convention Center, Dec 11 — 6th annual ran Dec 12-14 2025; no 7th-annual page found yet (likely just not posted). → `not-cancelled 1221` if you think it's just not up yet, else `cancel 1221`.
- `#1210` **Semmes Christmas Parade**, Dec 12 — no 2026-dated page found (editions 2021-2025 are indexed). → check cityofsemmesal.gov directly.
- `#463 #1125` **Women Powered by AI**, Innovation Portal, Dec 10 '26 / Jan 14 '27 — couldn't confirm this specific event name exists; only found the general (not gender-specific) monthly "Lower Alabama AI Meetup" at the same venue. → check innovation-portal.com directly before deciding.
- `#1229` **9th Annual King Cake-Off**, Mobile Convention Center, Jan 15 '27 — well-established annual fixture (8th annual ran Jan 23 2026) but no 2027 announcement found yet. → `not-cancelled 1229` if just not posted yet, else `cancel 1229`.
- `#1322` **Semmes Camellia Festival 2027**, Jan 23 '27 — the most recent confirmed edition ran a month later (Feb 7 2026), so this date may be off rather than cancelled. → check with the Semmes Boys & Girls Club before deciding.
- `#1853` **STEM Wonderland**, Gulf Coast Exploreum, Jan 29/30 '27 — no current listing found; the clearest historical match is a 2019-2020 edition. → check exploreum.com directly.
- `#1770` **Black Jacket Symphony 'Thriller'**, Saenger Theatre, Feb 13 '27 — a Black Jacket Symphony show at that venue/date is confirmed, but other "Thriller" dates that week are at different cities, so the Mobile show's program isn't confirmed. → `not-cancelled 1770` (the show itself is real) unless you want the specific program confirmed first.
- `#1230` **'STEEL MAGNOLIAS' (Multiple Performances)**, Joe Jefferson Playhouse, Jan 16 '27 — newly flagged this run, not yet researched. → check joejeffersonplayhouse.org or mobilecountyal.gov.

### Ambiguous match
- `#1966` **First Fairhope's Breakfast With Santa** (raw venue "First Fairhope") vs `#1965` **Breakfast at the Manger** (Fairhope United Methodist Church) — both Dec 5, 9am local. I confirmed "Breakfast at the Manger" is a real, dated Fairhope UMC event, but could not confirm "First Fairhope" refers to the same church (no "First United Methodist" or "First Baptist" Fairhope event by that name turned up in search) — so I can't tell if these are the same event scraped twice or two different church breakfasts on the same morning. → `merge 1966 1965` if you know they're the same, else `never-merge 1966 1965`.

### Source alerts (just FYI — not something to fix here)
- **92ZEW** (`92zew`) is the source behind essentially all 22 `source_underdelivered` holds this run — mostly the recurring weekly "Beer, BBQ & Bingo" at Moe's Original BBQ (Downtown Mobile), plus one one-off ("2nd Annual Jacob Hall Memorial Jam"). Same pattern as last week's issue (#29): 92ZEW returned 33 events, expected at least 40.
- **City of Gulf Shores** (`gulfshores-city`): returned 1 event, expected at least 2.
- **Mobile Chamber** (`mobilechamber`): pull still failing with 403 Forbidden; no successful pull since 2026-10-22 (now over a month).
- **Mobile SPCA** (`mobilespca`): pull failing with 401 Unauthorized.
