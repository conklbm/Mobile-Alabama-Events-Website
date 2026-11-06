# Review routine notes — 2026-11-06 (issue #22)

**Note on this run:** WebFetch (direct page retrieval) was unavailable for the entire session —
every external host failed to resolve, including non-project test hosts like google.com. Only
web search (snippets/indexed summaries, not live page content) worked. That's enough to confirm
a venue's existence and address from independent coverage, but not enough to reliably check
"is this still listed on the organizer's site right now" for cancellation flags. Flag this to
whoever runs the cloud routine infra — if it recurs next week, the "possibly cancelled" category
will keep piling up unresolved.

## Resolved automatically

- **Ruff Wilson Youth Organization** (slug `ruff-wilson-youth-organization`) — added as a new
  venue. 1317 Johnson Rd, Daphne, AL 36526. Raw venue string from the issue (`1317 Johnson Road;
  Daphne, Alabama 36526`) added as an alias, along with "Ruff Wilson Field" and "Ralph Wilson
  Youth Center" (same address, used interchangeably in local directories). Source: WKRG,
  ["Great food, meaningful connections, and supporting the youth: The Taste of the Ruff
  returns"](https://www.wkrg.com/red-couch-interviews/great-food-meaningful-connections-and-supporting-the-youth-the-taste-of-the-ruff-returns/)
  (confirms the Nov 10, 2026 fundraiser at this address), corroborated by the org's own site
  (rwyo.org) and Daphne Parks & Rec's listing for "Ruff Wilson Multi-purpose Sports Field" at
  the same address. Resolves `#1512` (The Taste of The Ruff).

## Needs Brooks

**Possibly cancelled — could not verify (WebFetch was down, see note above; I wasn't willing to
guess from search snippets alone):**
- `#632` Hollywood in Your Pocket (iPhone Photography), Eastern Shore Art Center, Nov 6 — `approve 632` if you've seen it still listed, else `cancel 632`
- `#534` `#542` `#549` `#554` `#561` `#567` `#572` Tuesday Teen Art Club, Mobile Museum of Art (weekly, Nov 11 – Dec 23) — this is a long-running recurring program; a single-source miss for a weekly class is usually noise, but I couldn't confirm it's still running this term. If it's still on the museum's calendar: `approve 534 542 549 554 561 567 572`
- `#1306` Mobile County Parks Fall Festival, Irvington Landfill, Nov 14 — search turned up a *different* county fall festival this year (Bayfront Park / Escatawpa Hollow, not Irvington) and nothing at Irvington for this date. Possibly a stale/wrong listing rather than a cancellation — worth a look before approving. `approve 1306` or `cancel 1306`
- `#1174` Crescent Comedy Workshop, Crescent Theater, Nov 18 — `approve 1174` or `cancel 1174`
- `#1060` Corks Casks and Canvas Sponsors, Eastern Shore Art Center, Nov 21 — the main "Corks, Casks & Canvas" gala is a real annual ESAC event (confirmed past editions), but I couldn't find a 2026 date or confirm this "Sponsors" occurrence specifically. `approve 1060` or `cancel 1060`
- `#646` `#1067` Sculpting the Figure, Eastern Shore Art Center, Jan 1 & Jan 8 2027 — `approve 646 1067` or `cancel 646 1067`
- `#657` Painting with Pan Patels, Downtown Fairhope, Jan 6 2027 — `approve 657` or `cancel 657`

**Unknown venues — found real context but not confident enough to add to venues.yaml:**
- `#1566` Roper Romp with a Reason, "various locations," Nov 7 — this is real and correctly has no
  single venue: FOX10 confirms it's a Helen-Roper-costumed sip-and-stroll through downtown
  Fairhope with stops at Visit Fairhope Social Club, Market by the Bay Fairhope, Monkey Bar, and
  Cactus Cantina, benefiting American Cancer Society's Shuck Cancer South Alabama. No single
  address to add. Recommend: `ignore 1566` (or if you want it on the site anyway, I'd need you to
  add a `force_publish` line yourself — that's outside what I'm set up to touch).
- `#1441` Midtown Vintage Market, "156 S. Florida Street," Nov 15 — couldn't confirm a business at
  that exact address. (A business called "Midtown Vintage Market" does exist, but it's in Little
  Rock, AR — unrelated.) Nearby addresses on S. Florida St in Mobile are commercial properties
  (153, 161, 170 S Florida St) but I couldn't pin down 156 specifically. Needs a human check —
  maybe themobmom's listing itself. `venue <slug> "<Name>" Mobile` once you know what's there, or `ignore 1441`
- `#1222` Taste of Christmas Festival, "Piggly Wiggly," Dec 6 — Mobile has 7–11+ Piggly Wiggly
  locations; the mobile-county source listing gives no street address. Couldn't determine which
  store. Candidates if you know which one: 2306 Saint Stephens Rd, 5651 Moffett Rd, 1360 Navco Rd,
  2601 Dauphin Island Pkwy (all Mobile). `venue <slug> "Piggly Wiggly (<location>)" Mobile` once confirmed, or `ignore 1222`
- `#1527` Christmas Tour of Homes, no venue given, Dec 5 — venue_name_raw is blank at the source
  (eastern-shore-chamber). Couldn't find a 2026 Eastern Shore Chamber "Christmas Tour of Homes" in
  search (found similarly-named events elsewhere in the country, and a Hope Blooms Fairhope
  Christmas home tour from 2025 that may be the same event under a different name/year — worth
  checking). `ignore 1527` or tell me the venue/organizer and I can add it next run.
- `#1148` Young Professionals of Mobile December 2026 Social, no venue given, Dec 10 — blank raw
  field at source (mobilechamber). Found a matching "5th Annual YP Tacky Holiday Sweater Party"
  on the Mobile Chamber calendar for 12/10/26, but its location field is blank/TBD there too.
  `ignore 1148` or tell me the venue and I can add it next run.

Everything else on issue #22 ("Cancelled by the source") was already auto-resolved by the
pipeline — no action needed there.
