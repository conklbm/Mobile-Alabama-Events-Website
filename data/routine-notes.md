# Review routine notes — 2026-10-16

Ran against issue #11 ("20 items need review — 2026-10-16", run #16). 1 of 20 items
resolved automatically; 19 remain for Brooks.

**Tooling note:** WebFetch was unavailable this run (DNS resolution failed for every
domain, including sites unrelated to this project — an environment issue, not a
site-specific block). All research below used WebSearch only, which cannot directly
browse a venue's live calendar page. Where that mattered, I left the item for Brooks
rather than guess.

## Resolved automatically

- **Monte L. Moorer Theatre** — added as `monte-l-moorer-theatre`, 161 Dogwood Lane,
  Mobile, AL 36608 (`regions: [mobile]`). It's the performing-arts venue on the campus
  of St. Paul's Episcopal School. Confirmed via St. Paul's own event listing
  (stpaulsmobile.net) and the Mobile Arts Council's venue page
  (mobilearts.org/locations/monte-moorer-theatre-st-pauls-episcopal-school/), both
  giving the same address as the raw source string. Resolves `#1119` (Peter Pan Goes
  Wrong).

## Needs Brooks

### Unknown venue — could not confirm
- **`Senior Bowl`** (`#1108`, Panini Senior Bowl Ticket Launch + Rip Event, Oct 15) —
  "Senior Bowl" is the organization (produced by the Mobile Arts & Sports Association),
  not a single street address, and a ticket-launch/retail "rip event" wouldn't be at
  the stadium (500 Stadium Dr / Hancock Whitney Stadium). The only street address I
  found tied to Senior Bowl ticketing was a 2012 news mention of a box office at 151
  Dauphin St, too old to trust. I didn't add a venue rather than guess.
  Recommend: `ignore 1108` for now, or if you know where this event is actually held,
  reply `venue senior-bowl-office "Senior Bowl" Mobile` with the address and I'll wire
  up the alias next run.

### Possibly cancelled — likely a source-side issue, not real cancellations
11 of the 19 flagged items are a single recurring TicketWeb/Crescent Theater listing
going dark two runs in a row, not 11 independent cancellations:
- `#187` `#193` `#204` `#209` `#211` `#212` `#216` `#224` `#366` `#416` `#677` —
  **Black and Gold on the Movie Screen** (every Saints game, Oct 18 – Jan 3), and
  `#192` **Adult Talent Show** (Oct 24) — both at Crescent Theater via ticketweb.com.
  It's very unlikely all ten weekly screenings plus the talent show were pulled at
  once; more likely the ticketweb.com collector itself is breaking on this venue's
  page (URL/markup change, rate limit, etc.). I couldn't verify directly since
  WebFetch is down this run.
  Recommend: check the `ticketmaster`/`civicplus_rss`(?) collector against
  ticketweb.com for Crescent Theater before touching any of these ids — if the
  listings are still live on ticketweb.com, this is a collector fix, not 11
  `not_cancelled` overrides. If you'd rather just clear them now: `not-cancelled 187
  193 204 209 211 212 216 224 366 416 677`.

### Possibly cancelled — one-offs, unverified
- `#1024` **Book Launch: The Nurse at Baker Hospital** (Oct 15, USA Student Center) —
  found a Skylark Books (Columbia, SC) listing for the author's launch event on Oct 8,
  not the USA date; couldn't confirm a separate USA Student Center listing either way.
  Recommend: `ignore 1024` unless you can check mobilearts.org's calendar directly.
- `#987` **Mobile Botanical Gardens: Sketch Club** (Oct 16) — this is a recurring
  Friday session (2–4pm, led by Derek Norman); couldn't confirm this specific Oct 16
  date is still on. Recommend: `ignore 987`, or `not-cancelled 987` if you know the
  Friday series is still running.
- `#988` **Administrator** (Oct 17, Historic Avenue Cultural Center) — title is too
  generic to search (likely a mis-scraped/placeholder title from the source).
  Recommend: `ignore 988`.
- `#989` **Moonlight on Dauphin (AKA a BOO on Dauphin) Paint & Sip** (Oct 18, Love and
  Adventure Studios) — found a Sept 20 paint-and-sip at this studio but nothing for
  the Oct 18 Halloween-themed one. Recommend: `ignore 989`.
- `#697` **Haunted Hollow-Een Movie Night: Hotel Transylvania** (Oct 23, Escatawpa
  Hollow Park & Campground) — found last year's (2024) Halloween event at this park
  but no 2026 Halloween listing; the park did have a weather closure earlier this
  year. Recommend: `ignore 697`, or `not-cancelled 697` if you know Mobile County
  Parks' Halloween night is still happening.
- `#475` **2026 Board of Directors/Board of Advisors Winter Meeting** (Nov 12, Mobile
  Chamber) — member-only board meeting, not really a public calendar item either way;
  nothing to confirm externally. Recommend: `ignore 475`.

No ambiguous matches, uncertain dates, or source alerts in this issue.
