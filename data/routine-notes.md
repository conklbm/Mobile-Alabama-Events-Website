# Review routine notes — 2026-11-13 (issue #24)

**Network note:** As in issues #21 and #22, WebFetch (direct page retrieval) could not reach any
external host this session (every lookup failed DNS resolution, including the chamber, county,
and 92ZEW source sites). Only web search (indexed snippets, not live pages) worked. That's enough
to confirm a venue's existence and address from independent coverage, but not enough to reliably
check "is this still listed on the organizer's site right now" — so, as before, nothing in
"Possibly cancelled" below was touched. Worth escalating if it's still happening in week 4.

## Resolved automatically

Added to `data/venues.yaml`, confirmed by web search, pipeline re-run cleared all 4 occurrences:

- **Fountain Park** (slug `fountain-park-pensacola`) — 300 E Zaragoza St, Pensacola, FL 32502.
  Small downtown-Pensacola park just south of Seville Square; regular host of Festa Italiana.
  Source: [Historic Pensacola](https://historicpensacola.org/plan-your-visit/museums-properties/fountain-park/),
  corroborated by [Visit Pensacola](https://www.visitpensacola.com/directory/fountain-park).
  Resolves `#1711`, `#1712`.
- **DeTonti Square** (slug `detonti-square`) — Mobile, AL 36602 (no single address; it's a
  9-block NRHP historic district bounded by Adams, St. Anthony, Claiborne, and Conception Sts).
  Arti Gras is its annual fundraiser for the neighborhood's community garden. Source:
  [Wikipedia / NRHP listing 72000169](https://en.wikipedia.org/wiki/De_Tonti_Square_Historic_District),
  corroborated by Mobile County's community-events listing for Arti Gras. Resolves `#1709`.
- **Dots & Dragons Mahjong** (slug `dots-and-dragons-mahjong`) — 2724 Old Shell Rd, Ste G,
  Mobile, AL 36607. 4,000-sq-ft mahjong parlor; opened with a public open house Nov 7–8, 2026.
  Source: [WKRG](https://www.wkrg.com/mobile-county/4000-square-foot-mahjong-parlor-opens-in-mobile/),
  corroborated by a LoopNet property record for the same address. Resolves `#1670`.

## Needs Brooks

**Unknown venues — couldn't confirm, left out of venues.yaml:**

- `#1527` **Christmas Tour of Homes** (no venue, eastern-shore-chamber) — unconfirmed for a third
  week running (also unresolved in issues #21, #22). Tour-of-homes events typically span several
  private homes with no single venue. `ignore 1527`, or tell me the organizer/starting point and
  I'll add it.
- `#1148` **Young Professionals of Mobile December 2026 Social** (no venue, mobilechamber) —
  unconfirmed for a third week; this source (my.mobilechamber.com) has been 403-blocked in past
  source alerts, which may be why nothing turns up. `ignore 1148` until Mobile Chamber access is
  sorted, or tell me the venue.
- `#1634` **Lyle Lovett + Hayes Carll** (no venue, 92zew, Feb 2 2027) — new this week. Search
  found no Mobile, AL date for this pairing (closest hit: Philadelphia, *Mississippi*, Jan 29
  2027). Since 92ZEW is the source and I couldn't fetch their page directly, this may be genuine
  and just not indexed yet — worth a direct check of 92zew.net/calendar/lyle-lovett-hayes-carll/.
  `venue slug "Name" Mobile` once you know the venue (my guess would be Saenger Theatre, given
  past bookings of this size), or `ignore 1634`.
- `#1671` **2026 Sardine Pass Cup Fishing Tournament** ("Sardine Pass") — Sardine Pass is a real
  fishing spot near Daphne, but I found no tournament page or weigh-in location to confirm an
  address. `venue slug "Name" Daphne` or `ignore 1671`.
- `#1441` **Midtown Vintage Market** ("156 S. Florida Street") — unconfirmed for a third week
  running (also unresolved in issues #21, #22); no business indexed at that exact address.
  `venue slug "Name" Mobile` or `ignore 1441`.
- `#1222` **Taste of Christmas Festival** ("Piggly Wiggly") — unconfirmed for a third week
  running; Mobile has 7+ Piggly Wiggly locations and the source gives no address. Candidates
  raised in past runs: 2306 Saint Stephens Rd, 5651 Moffett Rd, 1360 Navco Rd, 2601 Dauphin
  Island Pkwy. `venue slug "Piggly Wiggly (<location>)" Mobile` once confirmed, or `ignore 1222`.
- `#1658` **Daphne's Christmas Parade 2026** ("2000 Main Street Daphne Alabama") — no business
  or landmark confirmed at that exact address; past parades have started near the Daphne Civic
  Center / Olde Towne area instead. `venue slug "Name" Daphne` or `ignore 1658`.
- `#1682` **The Turkey's Done Mystery Dinner** ("Mobile Mystery Dinners") — Mobile Mystery
  Dinners is a touring dinner-theater company, not a fixed venue (confirmed office at 1858 Old
  Government St, but past shows have run at the Renaissance Riverview Plaza Hotel and elsewhere).
  For this specific occurrence, mobile.org's listing points to **Iron Hand Brewing, 206 State
  St, Mobile, AL 36603** (confirmed real business, multiple independent sources). I didn't alias
  "Mobile Mystery Dinners" to Iron Hand Brewing because that would wrongly map this organizer's
  future shows at other venues too. If you want this one published: `venue iron-hand-brewing
  "Iron Hand Brewing" Mobile`, then I can force-publish `#1682` onto it next run — or `ignore 1682`.
- `#1719` **Palafox Market** ("two locations: Martin Luther King Jr Plaza and Plaza Ferdinand") —
  both are real, confirmed plazas on Palafox St in downtown Pensacola, but the market runs at
  both simultaneously, so there's no single venue to alias this raw name to. `ignore 1719`, or
  if you want it on the site, I'd need a `force_publish` line from you (outside what I touch).
- `#1640` `#1663` **Lowes Home Improvement (Locations Vary)** and `#1647` `#1657` **Home Depot
  (Locations Vary)** — national in-store programs run at many locations simultaneously; no
  single venue to alias, matching the precedent already in `overrides.yaml` for the same kind of
  event (`#682` Lowes Kid Workshops). `ignore` these four, or send `force_publish` lines yourself.

**Possibly cancelled — couldn't verify either way (see network note above):**

- `#462` `#463` `#1125` **Women Powered by AI**, Innovation Portal — recurring monthly program;
  no 2026/2027 session list found to check against.
- `#637` **Mess Makers Society**, ESAC, Nov 14 — found program listings for a fall teen session
  and a Jan 2026 paid session, but nothing confirming or ruling out this specific Nov 14 date.
- `#1306` **Mobile County Parks Fall Festival**, Irvington Landfill, Nov 14 — flagged as likely
  bad source data in issues #21/#22 (the county's actual fall calendar shows Clean Sweep dump
  days, not a "fall festival," at Irvington on this date). Still unresolved; `cancel 1306` if you
  agree, or `not-cancelled 1306`.
- `#542` `#549` `#554` `#561` `#567` `#572` **Tuesday Teen Art Club**, Mobile Museum of Art
  (weekly) — same open question as issues #21/#22: the museum may have renamed this series to
  instructor-specific classes rather than discontinuing it. `not-cancelled` or `cancel` all six.
- `#1174` **Crescent Comedy Workshop**, Crescent Theater, Nov 18 — real recurring series, but no
  evidence found either way for this date (same as issues #21/#22).
- `#1060` **Corks Casks and Canvas Sponsors**, ESAC, Nov 20 — only a confirmed 2025 (Oct 25) date
  exists online; no 2026 date to check against (same as issues #21/#22).
- `#961` `#1532` **Fairhope First Friday Art Walk**, Downtown Fairhope, Dec 5 & Jan 2 — this is a
  long-running monthly institution with no sign of discontinuation, but I couldn't independently
  confirm these two specific dates are still on (Jan 2 is close to a holiday, which could affect
  scheduling). Leaning `not-cancelled` but flagging rather than guessing.
- `#646` `#1067` **Sculpting the Figure**, ESAC, Jan 1 & Jan 8 2027 — no listing found either way
  (same as issues #21/#22).
- `#657` **Painting with Pan Patels**, Downtown Fairhope (ESAC), Jan 6 2027 — still can't match
  "Pan Patels" to an instructor; may be a source-side title issue rather than a real cancellation
  (same as issues #21/#22).

No ambiguous matches, uncertain dates, or source alerts in this issue.
