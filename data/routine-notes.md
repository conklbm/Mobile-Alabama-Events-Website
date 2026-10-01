# Routine notes — 2026-10-01

## Heads up: weekly pipeline did not run this week

Issue #5 ("8 items need review — 2026-09-24", run #11) is still open — its three
leftover items (below) are unchanged from last Thursday. That's because the
**Weekly events pipeline** Action (cron `17 9 * * 4`, Thu ~09:17 UTC) has not run
today: the last successful run was 2026-09-24 (run #9); there is no run at all for
2026-10-01 in the Actions history, over three hours past its scheduled time as this
routine runs. No new events were collected this week. This is outside the three
files this routine is allowed to touch and isn't a collector problem, so I did not
try to fix or re-trigger it — flagging for Brooks to check the Action (may just need
a manual `workflow_dispatch` re-run, or there's a scheduling/GitHub issue worth a
look).

## Resolved automatically

None. No new "Unknown venues," "Ambiguous matches," or "Uncertain dates" sections
appeared this run (consistent with the weekly job not having run). The three items
below were already reported unresolved last week (2026-09-24 notes) and nothing
new was found.

## Needs Brooks

- **`#385` Fall Brawl Festival** — Sat Oct 10, 2700 Newman Road – Mobile, AL —
  `venue_unknown`. Re-checked this week: that address is still a cluster of
  auto-salvage/junkyards (Newman Auto Recyclers, Heritage Used Car & Truck Parts);
  I found no "Fall Brawl Festival" anywhere in Mobile, AL in web search, Eventbrite,
  or elsewhere. The source page (themobmom.com) is egress-blocked from this session
  again, so I can't check the listing directly. Likely a mistyped address upstream.
  Ready-to-send once confirmed: `venue fall-brawl-venue-slug "Venue Name" Mobile`.
  Otherwise: `ignore 385`.

- **`#167` Corey O'Brien** — Fri Oct 02, Downtown Mobile (Crescent Theater, via
  Ticketmaster/TicketWeb) — `cancellation_flagged` (inferred, not source-confirmed).
  Both ticketweb.com and crescenttheater.com are unreachable from this session
  (egress-blocked / DNS). Web search found no cancellation notice, but also no
  independent confirmation it's still on. Recommend checking ticketweb.com or
  Crescent Theater's site/socials directly: `not-cancelled 167` if still listed,
  `cancel 167` if pulled.

- **`#333` Coffee with the Chamber: Calagaz Printing** — Wed Oct 28, 90 Springdale
  Blvd (Mobile Chamber) — `cancellation_flagged` (inferred). mobilechamber.com and
  my.mobilechamber.com are both egress-blocked from this session. No cancellation
  found via web search. Recommend checking the Chamber's event calendar directly:
  `not-cancelled 333` if still listed, `cancel 333` if pulled.

No action taken on `data/venues.yaml` or `data/overrides.yaml` this run.
