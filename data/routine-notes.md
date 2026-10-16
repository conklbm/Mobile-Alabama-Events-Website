# Review routine notes — 2026-10-16

Starting point was issue #10 ("28 items need review — 2026-10-15"), already partly resolved by
last week's run. The live queue had since grown to 23 open items (daily reprocessing re-flagged a
wave of `cancellation_flagged` holds on 2026-10-15 that weren't in the issue's original text). This
run resolved 3 of those 23; 20 remain, nearly all of them are "possibly cancelled" items I could not
confirm either way.

**Note on tooling:** WebFetch could not reach several of the small-site sources this run
(mobilearts.org, mobilecountyal.gov, ticketweb.com, mobile.org, mobilechamber.com all failed —
checked, this is a session network-policy block, not a transient error) — I relied on web search
and on cross-checking sources already recorded in the database instead. That limited how many of
the "possibly cancelled" items I could independently confirm this week.

## Resolved automatically

**Cleared cancellation flags** (`overrides.yaml` → `not_cancelled`) — both had a second,
independent source still listing them fresh as of the 2026-10-15 run, even though
`mobile-arts-council` missed them twice:
- `#819` **British High Tea at the Condé-Charlotte Museum** (Sun Oct 18) — still listed by
  `visit-mobile` (mobile.org), last seen in the same run that flagged the mobile-arts-council copy
  as missing.
- `#856` **USA Faculty Trumpet and Horn Recital** (Thu Oct 15) — same situation; `visit-mobile`'s
  copy is fresh, only the mobile-arts-council copy went stale.

**Merge call** (`overrides.yaml` → `merge`):
- `[1085, 1076]` — **Trae Crowder, Crescent Theater, Fri Jan 8 2027.** Mobile County's listing
  ("Two Shows") describes the same 7pm + 9pm booking that Ticketmaster's own occurrence already
  covers (it had separately merged the early-show and late-show ticket links together before this
  run). Confirmed via a Mobile County community-events page naming both showtimes, the comedian,
  and the venue. Source: county listing surfaced via web search (`trae-crowder-two-shows-2027-01-08`
  on mobilecountyal.gov).

## Needs Brooks

**Likely source/collector issue, not necessarily real cancellations** — worth a look before acting
on any of these one by one:
- **11 Ticketmaster showings of "Black and Gold on the Movie Screen" at Crescent Theater**
  (`#187` Oct 18, `#193` Oct 25, `#204` Nov 8, `#209` Nov 15, `#211` Nov 22, `#212` Nov 29, `#216`
  Dec 6, `#224` Dec 13, `#366` Dec 20, `#416` Dec 27, `#677` Jan 3) — all single-sourced by
  Ticketmaster, all missed the same two pulls at once. Crescent Theater itself is clearly still
  active and ticketing other shows through Ticketmaster/Live Nation right now (a comedy show is
  listed for tonight, Oct 16), so the venue isn't dark — this looks more like the whole recurring
  "Black and Gold" series got pulled, re-posted under new event IDs Ticketmaster hasn't re-matched
  yet, or genuinely cancelled for the season. I couldn't reach ticketweb.com directly this run to
  check.
  → `not-cancelled 187 193 204 209 211 212 216 224 366 416 677` if the series is still running
  (check crescenttheater.com/calendar or Ticketmaster), or `cancel 187 193 204 209 211 212 216 224
  366 416 677` if it's off for the season.
- **4 mobile-arts-council-only items, all missed the same two pulls**: `#987` Mobile Botanical
  Gardens Sketch Club (Fri Oct 16), `#988` "Administrator" at Historic Avenue Cultural Center (Sat
  Oct 17), `#989` Moonlight on Dauphin Paint & Sip at Love and Adventure Studios (Sun Oct 18),
  `#1024` Book Launch: The Nurse at Baker Hospital (Thu Oct 15, USA Student Center). Web search
  found a real launch event for that book but not in Mobile, and nothing confirming or denying the
  other three — I couldn't load mobilearts.org's calendar directly this run. This pattern (one
  source dropping several unrelated events in the same pull) smells like a collector-side glitch
  rather than four real cancellations.
  → Check `mobilearts.org/community-calendar` directly; `not-cancelled 987 988 989 1024` if they're
  still listed, `cancel <id>` for any that aren't.

**Single items, no corroborating or contradicting information found:**
- `#192` **Adult Talent Show**, Crescent Theater, Sat Oct 24 — third run in a row flagged (open
  since issue #9); still no source I could reach to confirm either way.
  → `not-cancelled 192` or `cancel 192`.
- `#475` **2026 Board of Directors/Board of Advisors Winter Meeting**, Thu Nov 12, 4101 Wimbledon
  Drive — source is `mobilechamber`; couldn't reach my.mobilechamber.com this run.
  → `not-cancelled 475` or `cancel 475`.
- `#697` **Haunted Hollow-Een Movie Night: Hotel Transylvania**, Escatawpa Hollow Park &
  Campground, Fri Oct 23 — source is `mobile-county`; found the park's Halloween playground-opening
  event in search results but nothing specifically confirming this movie night.
  → `not-cancelled 697` or `cancel 697`.

**Unknown venues — unchanged from last week, still can't confirm:**
- `#1108` **Panini Senior Bowl Ticket Launch + Rip Event**, Thu Oct 15, raw venue "Senior Bowl" —
  no new information found. Panini is the Senior Bowl's title sponsor but nothing names a venue for
  this specific ticket-launch event.
  → `venue slug "Venue Name" City` once known, or `ignore 1108`.
- `#1119` **Peter Pan Goes Wrong**, Wed Nov 11, raw venue "Monte L. Moorer Theatre; 161 Dogwood
  Lane, Mobile, AL, 36608" — no new information found. The only "Moorer" connection in Mobile is an
  unrelated library branch; 161 Dogwood Lane still doesn't match a known theatre.
  → `venue slug "Monte L. Moorer Theatre" Mobile` if confirmed, or `ignore 1119`.
