# Routine notes — issue #21 (2026-11-05, follow-up pass)

The prior run of this routine already resolved 28 of 33 items from issue #21
(13 new venues, 6 aliases, 1 not_cancelled, 1 never_merge — see the issue's
existing comment for that list). This pass picked up the "Still open" items
left behind. Note for context: this session's network could not reach any of
the primary-source domains directly (mobilemuseumofart.com, esartcenter.org,
ticketweb.com, mobilecountyal.gov, mobile.org all failed DNS resolution from
here), so "checking the organizer's site" below means web-search research,
not a direct page fetch — weaker evidence than usual, which is why most of
this list stayed with Brooks rather than being resolved automatically.

## Resolved automatically

- **#1509 "Eastern Shore Children's Clinic - Open House celebrating 50 years"** (blank raw venue, eastern-shore-chamber) — added **Eastern Shore Children's Clinic**, 150 S Ingleside St, Fairhope, AL 36532, to `data/venues.yaml` and force-published #1509 onto it (blank `venue_name_raw` can't match an alias). Confidence: the clinic's Spanish Fort office only opened around 2021 per a 2021 Bay Business News ribbon-cutting piece, so a 50th-anniversary open house has to be about the original Fairhope practice. Address corroborated independently by the NPI registry, WebMD, and cortico.health. Sources: [Bay Business News](https://baybusinessnews.com/healthcare-wellness/eastern-shore-childrens-clinic-opens-in-spanish-fort/), NPI registry (1831151331).

Ran `pytest` (69 passed), validated both YAML files, and re-ran `pipeline process`/`queue`/`publish` — #1509 dropped out of the queue (`auto_resolved: 1`) with no errors.

## Needs Brooks

Genuinely couldn't confirm from this session, or confirmed just enough to flag a specific question — left out of `venues.yaml`/`overrides.yaml` rather than guessed.

**Likely a collector/source problem, not real cancellations:**

- **#534, #542, #549, #554, #561, #567, #572 "Tuesday Teen Art Club" (Mobile Museum of Art, weekly Tue Nov 11 → Dec 23)** — all 7 upcoming occurrences hit the two-miss cancellation flag simultaneously, which is itself a strong tell. Mobile Museum of Art pulls via their Events Calendar API (not flagged as unhealthy this run), but web search turns up the museum currently posting teen sessions under *instructor-specific* titles ("Tuesday Art for Teens with Stephanie Bromley," "Clay for Teens with Angie King") rather than a generic recurring "Tuesday Teen Art Club" series, and there's a live "Teen Art Class Registration" page on mobilemuseumofart.com. My read: the museum likely renamed/restructured this recurring series on their end, which would explain the collector suddenly missing it site-wide rather than one date at a time — but I can't confirm the class itself stopped. `not-cancelled 534 542 549 554 561 567 572` if you'd rather treat it as a false alarm, or `cancel 534 542 549 554 561 567 572` if you know the generic club format is gone — either way, worth a look at whether the mobile-museum-of-art collector needs updating for the new instructor-named format (that part's a dev task, not something I should touch).
- **#1174 "Crescent Comedy Workshop" (Crescent Theater, Wed Nov 18)** — this is a real recurring Wednesday series (TicketWeb/Crescent Theater), but every listing I found only runs through late October 2026; I found no evidence either way for a Nov 18 date. `not-cancelled 1174` or `cancel 1174`.

**No new evidence beyond last week's (unchanged from the prior routine-notes, carried forward since not yet handled):**

- **#632 "Hollywood in Your Pocket - The Art of Iphone Photography"** (ESAC, today — Fri Nov 6) — no trace of this specific class found. `not-cancelled 632` or `cancel 632`.
- **#1060 "Corks Casks and Canvas Sponsors"** (ESAC, Nov 20) — only a confirmed 2025 (Oct 25) date exists online; no 2026 date to check against. `not-cancelled 1060` or `cancel 1060`.
- **#646 / #1067 "Sculpting the Figure"** (ESAC, Jan 1 & Jan 8 2027) — no listing found either way. `not-cancelled 646 1067` or `cancel 646 1067`.
- **#657 "Painting with Pan Patels"** (ESAC via Downtown Fairhope, Jan 6 2027) — still can't match "Pan Patels" to an instructor; may be a source-side title typo rather than a real event. `not-cancelled 657` or `cancel 657`.

**New this run — researched, still can't confirm:**

- **#1306 "Mobile County Parks Fall Festival"** (Irvington Landfill, Sat Nov 14) — Mobile County's actual fall calendar (per their own news releases) is four Operation Clean Sweep dump days at Irvington/Axis/Mobile, none on Nov 14, and last year's "fall festival" event was at Bayfront Park/Escatawpa Hollow, not Irvington. This raw listing may be a parser mismatch (Clean Sweep event picked up with the wrong name/date) rather than a real festival. `cancel 1306` if you agree it looks like bad source data, or `not-cancelled 1306` if you know otherwise — worth a look either way.

**Unknown venues — still can't confirm what/where:**

- **#1512 "The Taste of The Ruff"** — raw venue "1317 Johnson Road; Daphne, Alabama 36526." No business indexed at that exact address. `venue new-slug "Name" Daphne` once known, or `ignore 1512`.
- **#1441 "Midtown Vintage Market"** — raw venue "156 S. Florida Street," Mobile. No business matches that exact address (note: this is a different address/event from the already-resolved "Merry Midtown Market" at 217 S. Sage Ave). `venue new-slug "Name" Mobile` or `ignore 1441`.
- **#1222 "Taste of Christmas Festival"** — raw venue just "Piggly Wiggly." Several Piggly Wiggly stores host similar events (University Blvd, Saraland); can't tell which one. `venue new-slug "Piggly Wiggly (___)" ___` with the right store, or `ignore 1222`.
- **#1527 "Christmas Tour of Homes"** (eastern-shore-chamber, Dec 5) — blank raw venue; tour-of-homes events typically span multiple private homes with no single starting venue. Probably just `ignore 1527`.
- **#1148 "Young Professionals of Mobile December 2026 Social"** — blank raw venue, source is my.mobilechamber.com, which is the same host that's 403-Forbidden-blocked in this week's source alerts — nothing to check there, and no December listing turned up elsewhere. `ignore 1148` until Mobile Chamber source access is sorted.

**Source alerts (not investigated — out of scope for this routine):**

- 92ZEW returned 39 events vs. an expected 40 (same as last week, likely noise).
- Mobile Chamber's calendar pull is still 403 Forbidden — this is also why #1148 above can't be checked.
- The 14 "Beer, BBQ & Bingo" (Moe's Original BBQ) occurrences and "2nd Annual Jacob Hall Memorial Jam" flagged `source_underdelivered` this run are a 92ZEW side effect of the above — no action taken, per routine scope.
