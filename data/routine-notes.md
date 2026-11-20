# Review routine notes — 2026-11-20

This pass re-checked issue #26 after yesterday's two routine runs (comments on
the issue, commits `7b017ccf` and `a3fda24f`) already resolved 14 venues/aliases
and 7 ambiguous matches. No new venue or match information turned up this time —
fresh web searches on the remaining unknowns (Piggly Wiggly, The Swamp Lily,
Mason Hills Park, Alvin's Island/Elf Academy, Mobile Mystery Dinners) returned
the same ambiguity already reported, so nothing new was added to `venues.yaml`
or `overrides.yaml`. Direct fetches to the source domains (mobilemuseumofart.com,
business.eschamber.com, etc.) are still blocked by this session's network
allowlist, same as prior runs.

## Resolved automatically
Nothing new this pass — see issue #26's two existing bot comments for what's
already resolved, and the "Still open" list below for what remains.

## Needs Brooks

Everything below was already reported on issue #26 (both earlier comments);
listing it again here just so it's in one place. Ready-to-send commands:

- `ignore 1786 1792 1794 1795 1801 1802 1803 1805` — TrainTastic Model Railroad
  Museum (8 occurrences) is real but in Gulfport, MS — outside both site regions.
  Or tell me which region tag to use and I'll add it.
- `ignore 1818` or an address — The Swamp Lily (`#1818`), can't find this business.
- `venue mason-hills-park "Mason Hills Park" "Grand Bay" <address>` or `ignore 1812`
  — two candidate addresses found, can't tell which is right.
- `venue piggly-wiggly-<location> "Piggly Wiggly" Mobile` or `ignore 1222` —
  11+ Piggly Wiggly stores in the county, source doesn't say which one.
- `ignore 1789` or name the building — University of South Alabama (`#1789`) is
  too generic to alias to one spot on campus.
- `ignore 1682` or tell me the venue for this date — Mobile Mystery Dinners
  (`#1682`) tours between venues; found a pattern of using the Renaissance
  Riverview Plaza Hotel for past shows but nothing confirming this one.
- `ignore 1870` or tell me the location — Alvin's Island has stores in Gulf
  Shores, Orange Beach, and Perdido Key; can't tell which hosts Elf Academy.
- `ignore 1798` or the host's name — 8108 Morris Hill Rd is vacant land per
  property records; possibly a private residence running a seasonal display.
- `ignore 1647 1657 1663` or `force_publish` — Home Depot / Lowe's multi-location
  programs, no single venue by design (same pattern as the existing Lowe's entry).
- `ignore 1527 1148 1634` or send each one's actual venue — blank venue field
  at the source, nothing to alias.
- `merge 1015 1837` or `never-merge 1015 1837` — Central Midtown Holiday Market
  (`#1837`, Dec 12) vs. Central Midtown's regular Second Saturday Market
  (`#1015`) — Dec 12 is the second Saturday, so this could be the same market
  with holiday theming, or a separate event.
- 14 "possibly cancelled" items unverified both ways (network-blocked sources):
  `#542 #1174 #1060 #549 #554 #961 #567 #463 #572 #646 #1532 #657 #1067 #1125`.
- Source alerts (no action, flagging only): 92ZEW under-delivered; City of Gulf
  Shores under-delivered; Mobile Chamber 403-blocked 3+ weeks running; Mobile
  SPCA now 401-Unauthorized (new).

## A bigger problem than any one issue: 10 older review issues are stuck open

While checking issue #26 I looked at the other open `review` issues and found
a real backlog: **11 are open right now, oldest from 2026-10-08 (issue #8,
6+ weeks)**. The cause looks structural, not something a data-file edit can
fix: `apply-config.yml`'s "Update the open review issue" step only ever
touches `gh issue list --label review --state open --limit 1` — the single
*most recent* open issue. The moment a new weekly issue opens, every earlier
one stops getting comments or getting closed, even if everything in it later
gets resolved in `venues.yaml`.

Concretely, this means real, ready-to-action items have been sitting
unseen for weeks:

- **Issue #8** (2026-10-08, open 6+ weeks) still has 7 untouched items from
  the 2026-10-09 follow-up comment: `ignore 932 965` (Moonlight Chasse' Ballroom
  Dance Society — confirmed real, blank venue field), `ignore 937 964` (BILL-E's
  Bacon, Burgers & Bikes — same blank-field issue), a `venue` call or `ignore 941`
  for the Schreiber Water Treatment Facility dedication, `ignore 682` for the
  Lowe's multi-location workshop, and a cancellation call (`not-cancelled 192` /
  `cancel 192`) for the Adult Talent Show.
- The **same unresolved items** — Piggly Wiggly (`#1222`), the blank-venue
  Lyle Lovett + Hayes Carll show (`#1634`), blank-venue items (`#1148`, `#1527`)
  — have now been independently re-researched from scratch in issues #20, #21,
  #22, #24, *and* #26, each time reaching the same "can't confirm" conclusion,
  because none of those replies ever reached you in a way that stuck.

Recommend one of: (1) reply directly on the old issues with their ready
commands — `review-commands.yml` fires on a comment to *any* open `review`
issue, not just the latest, so this works today without any code change; or
(2) ask for `apply-config.yml` to loop over all open `review` issues instead
of just the newest one. Either way, worth triaging the old issues (#8, #9,
#12, #13, #14, #20, #21, #22, #23, #24) so they don't just keep accumulating
unseen.
