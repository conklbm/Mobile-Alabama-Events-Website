# PRD — Gulf Coast Events Pipeline, V1

**Owner:** Brooks Conkle
**Date:** 2026-09-14
**Build target:** Claude Code
**Companion doc:** `EVENT-SOURCE-REGISTRY.md` (verified source list — read it first)

---

## 1. What this is

A weekly automated pipeline that collects local events from structured sources,
deduplicates them into canonical records, and publishes them to one or more
static sites.

**V1 scope:** the pipeline + one publisher (mobilebayevents.com, Mobile metro).
**Phase 2:** a second publisher (coastal events section on gulfcoastbeachvibes.com).

## 2. Why

Brooks wants one place to check what's happening locally. The old manual process
(~15 sources checked by hand weekly) was the most valuable part of a previous
local media brand and is now automatable.

Secondary: the domain ages and accumulates SEO equity while the tool is useful.

## 3. Explicit non-goals for V1

Do **not** build any of the following. They have no customer yet and each one
turns a two-weekend project into a month:

- Public API, API keys, rate limiting, usage metering, billing
- Embeddable widgets or iframes
- User accounts, saved events, email digests, notifications
- Event submission forms
- Mobile app
- Browser automation (Tier 3 sources) — deferred until coverage gaps justify it
- Facebook scraping — manual weekly process instead (see §11)

## 4. Architecture

**Hard rule: storage and publishing are separate.** The SQLite store is the
single source of truth. Publishers are read-only consumers. A third consumer
(CSV export, second site) must be addable without touching the pipeline.

```
collectors/ ──▶ raw_pulls (append-only) ──▶ normalize ──▶ dedup ──▶ canonical
                                                                      │
                                                            review queue (human)
                                                                      │
                                                    ┌─────────────────┴──────┐
                                              publisher:mobile      publisher:coastal
                                              (V1)                  (phase 2)
```

**Stack**

- Python 3.12
- SQLite, single `.db` file committed to the repo
- `rapidfuzz` for fuzzy matching (not fuzzywuzzy)
- `icalendar` for ICS parsing
- GitHub Actions, weekly cron (Thursday AM)
- Publisher output: static site. Framework is the builder's call for V1;
  phase 2 must integrate with GCBV's existing Next.js.

## 5. Data model

### `sources`
| field | notes |
|---|---|
| `id`, `name`, `url` | |
| `collector_type` | `tribe_api` \| `ics` \| `rss` \| `jsonld` \| `html` \| `ticketmaster` |
| `tier` | `A` (venue/organizer's own) \| `B` (ticketing platform) \| `C` (aggregator) |
| `regions` | **list** — `["mobile"]`, `["coastal"]`, or both |
| `brand_tokens` | list of strings for self-promo detection (§8) |
| `license_notes` | free text — terms, attribution requirements |
| `redistributable` | bool — can this data go in a feed sold or given to a third party |
| `expected_min_events` | int — floor for the silent-breakage alarm (§10) |
| `last_successful_pull` | timestamp |

> `license_notes` and `redistributable` are **required from day one.** Backfilling
> them across 30 sources later, after promising someone a feed, is painful.
> Ticketmaster requires attribution + link-back — record that.

### `venues`
| field | notes |
|---|---|
| `id`, `canonical_name`, `address`, `city`, `lat`, `lng` | |
| `regions` | **list, not enum.** Dauphin Island is `["mobile","coastal"]` |

Aliases live in a separate hand-edited `venues.yaml`, loaded at runtime.
Do not put the alias map in the database — it's the file Brooks edits most and
a text editor beats any DB UI.

### `series`
The durable entity. **URLs point here, not at occurrences.**

| field | notes |
|---|---|
| `id`, `slug`, `canonical_title`, `venue_id`, `description` | |
| `cadence` | `annual` \| `weekly` \| `monthly` \| `one_off` |
| `category` | music, family, food, arts, sports, community, nightlife |

### `occurrences`
| field | notes |
|---|---|
| `id`, `series_id` | |
| `start_utc`, `end_utc`, `timezone` | **always store UTC + explicit tz** |
| `all_day` | bool |
| `price`, `ticket_url`, `info_url` | two link fields, never collapsed |
| `status` | `active` \| `flagged_cancelled` \| `cancelled` |
| `independent_source_count`, `curation_score` | see §8 |
| `image_url`, `image_source_url`, `image_credit`, `image_ok` | see §9 |

### `occurrence_sources`
Many rows per occurrence. **This is what makes attribution work.**

| field | notes |
|---|---|
| `occurrence_id`, `source_id`, `source_url` | |
| `first_seen`, `last_seen`, `consecutive_misses` | |
| `self_promoted` | bool (§8) |
| `raw_pull_id` | FK into the archive |

Primary source is **computed at render time** from tier ranking — never stored
as a fixed fact. When the ranking turns out to be wrong, change one function
and re-derive rather than re-scraping history.

### `raw_pulls`
Append-only. Every record, every run, exactly as received. **Never delete.**
Disk is free; this is the only thing you cannot regenerate later.

## 6. Collectors

Build in this order — highest output per line of code first.

1. **`tribe_api`** — ONE collector, N domains. Hits
   `/wp-json/tribe/events/v1/events`. Covers 92zew.net (239 events),
   innovation-portal.com (97), themobmom.com, mobilesymphony.org,
   joejeffersonplayers.com, mobilespca.org.
   **Extract the `website` field** — it's the one-hop origin link (§7).
2. **`ticketmaster`** — Discovery API v2, free key. Sweeps Saenger, Civic
   Center, Wharf Amphitheater. Read and comply with their attribution terms.
3. **`rss` / `ics`** — CivicPlus city calendars (Gulf Shores, Orange Beach).
4. **`jsonld`** — Playhouse in the Park, Soul Kitchen, and the Tier 2 sites
   that carry `Event` markup.
5. **`html`** — custom parsers, one at a time, ordered by event volume.

**Before writing any custom parser, test the Tribe endpoint on that domain.**
It's public, needs no auth, and a surprising number of local sites run it.

## 7. Attribution

Tier ranking: **A** (venue/organizer's own site) > **B** (ticketing platform) >
**C** (aggregator).

Aggregators almost always link out. **Extract outbound links from every listing
and follow one hop.** A Tier C listing linking to a venue domain has just handed
you the Tier A source. ~20 lines, resolves most cases.

Every event page displays: primary source link ("More info"), and separately
the ticket link ("Get tickets") where one exists.

## 8. Scoring — two fields, not one

Manually-curated sources are a genuine quality signal: a human decided each
event was worth typing. But those same sources also list **their own** events,
which is not an independent vote.

**Self-promo detector:** flag `self_promoted = true` when the event's organizer,
venue, or title matches any of the source's `brand_tokens`. ~12 lines.

- **`independent_source_count`** — distinct parties, self-promo excluded.
  Signal for "is this real / is this a big deal."
- **`curation_score`** — count of human-curated sources that picked it up.
  Signal for "is this worth featuring." **This drives the top-10 selection.**

Self-promoted events still appear in listings normally. They just don't vote
for themselves when deciding what gets featured.

## 9. Images

Gate on **source tier**, not on human judgment about the act.

- Arriving via Ticketmaster → **no image**. Touring-act promo art is the most
  actively policed and usually belongs to the artist or label, not the venue.
- Arriving from a local venue's own site or a community calendar → keep the
  image, **with credit**.
- `image_ok` is computed from this rule; false → render a category default so
  the page is never empty.

Always store `image_source_url` and `image_credit` so anything can be attributed
or pulled instantly.

## 10. Freshness, expiry, and breakage

### Cancellation detection
Each run, successfully-pulled sources stamp `last_seen` on the rows they confirm.
Flag an occurrence when its Tier A source has gone stale but a lower tier hasn't.

Two mandatory guards:

1. **Never run the check for a source whose pull failed or returned zero** —
   one broken parser would otherwise flag fifty events as cancelled.
2. **Require two consecutive misses**, not one. Sites paginate; an event can
   fall off page one while still being live.

Flagged items go to the review queue as "possibly cancelled." Never auto-remove.

### Expiry
- **Series URLs never expire.** Next occurrence on top, past ones below.
  Annual festivals accumulate authority year over year.
- **One-off events → 301 to the venue page,** but not for **7 days** after the
  event. People search the morning after.
- `Event` JSON-LD must carry an accurate `endDate` — Google drops expired
  events from rich results on its own.
- Never leave indexed "this event has passed" pages.

### Silent breakage
The `last_seen` + `expected_min_events` fields give this for free. Alert when a
source returns suspiciously few events or hasn't stamped anything in 3 weeks.
**This is the #1 killer of scraper projects** — failure is silent, and you
notice in March that the site has been half-empty since November.

## 11. Manual inputs

**Review queue — confidence-gated, not blanket.**

Most events publish automatically. Only genuinely uncertain ones wait for a human.

**Auto-publish when ALL gates pass:**
- `source_tier` is A or B
- `venue_resolved` — venue matched a known entry in `venues.yaml`
- `date_confident` — parsed cleanly, explicit year and time
- `match_unambiguous` — either a clear series hit (≥0.82) or clearly new (<0.70)

**Queue for review when ANY of these:**
- `venue_unknown` — unrecognized venue name. **The most common case**, and a
  real human decision: the alias map needs a new entry.
- `match_ambiguous` — fuzzy score in the 0.70–0.82 band
- `cancellation_flagged` — see §10
- `source_underdelivered` — source returned suspiciously few events

> **Store these as named booleans, never a blended numeric score.** When
> something wrong gets published, `venue_unknown = true` tells you what failed.
> A composite `0.74` tells you nothing and cannot be debugged.

Expected volume: ~2–5 items per week, not hundreds.

**Delivery:** the GitHub Action opens an issue titled "N items need review" with
details inline. Email notification, click through, resolve. No UI to build.

**Rollout: queue everything for the first 2–3 runs.** You cannot calibrate a
threshold you have never watched fail. Loosen the gates only after seeing where
the parsers actually break. Going straight to full auto means the first bad
parse sits live for a week and you learn about it from the site.

**Facebook (weekly, ~10 min, manual).** No API path exists; automating the
logged-in Events tab violates Meta's terms and risks the account the business
pages hang off. Provide a simple CSV or YAML drop-in so hand-entered events join
the same pipeline. Sources to scan: personal Events tab, VisitMobile, Downtown
Mobile Alliance, Lagniappe, City of Mobile, Mobile Parks & Rec.

## 12. Dedup

**Runs across the entire canonical set, not just between sources.** Manual entry
produces duplicates *within* a single source — verified live on 92ZEW, where
"Beer, BBQ & Bingo" at Moe's was entered twice by two different authors as two
separate series.

Algorithm:
1. Normalize date to a day; resolve venue via the alias map.
2. Bucket by day + venue.
3. `rapidfuzz.token_set_ratio` on titles within each bucket. Start at 82,
   tune against real data.
4. **Series matching** for recurring events: title similarity + same venue +
   roughly same time of year → attach to the existing series slug rather than
   creating a new one. Must have a manual override path.
5. Source priority decides which record's fields win.

Low-confidence matches go to the review queue rather than auto-merging.

## 13. Publishing

### V1 — mobilebayevents.com
Public and fully indexed. No active marketing, but technically a real site:
JSON-LD, sitemaps, proper titles and meta descriptions.

**Page types:**
- `/` — this week, curated, grouped by category
- `/events/<series-slug>` — the durable event page
- `/venues/<venue-slug>` — all upcoming + history at that venue
- `/this-weekend` — evergreen URL, rotating content
- **Satellite city pages — first-class from day one, not an expansion phase:**
  `/daphne-al-events`, `/fairhope-events`, `/saraland-events`,
  `/spanish-fort-events`, etc.
- Category pages: `/live-music-mobile-al`, `/free-things-to-do-mobile-al`

> SERP research showed the incumbents on satellite-city queries (Eventbrite,
> AmericanTowns) rank on domain authority with stale, badly-geolocated filler —
> Eventbrite's Saraland page returns virtual PMP training at a Regus office.
> A current, correctly-geolocated page has very little to beat. This is the
> highest-opportunity surface on the site.

**Every page needs original value beyond the scraped listing** — category
judgment, a parking note, a "good for kids under 6" flag, a short blurb.
Thin programmatic pages built purely from scraped data are exactly what
Google's helpful-content updates target.

### Phase 2 — GCBV coastal section
Same store, different consumer. Routing by `venue.regions`.

**Blurbs must be generated separately per site.** Same underlying record,
different audience: GCBV writes for someone planning a trip; the Mobile site
writes for someone who already lives here. Identical text across two domains
means Google picks one as canonical and filters the other — you get one listing
and one wasted page, not two shots at ranking.

## 14. Known-hard bits — budget real time

- **Recurrence expansion.** Some sources (Mobile County `/community_events/`)
  list multi-month recurring programming — "every Wednesday, Jul 1 to Dec 30" —
  rather than discrete events. Parser must expand these; curation must **not**
  surface a weekly resume clinic as a featured thing to do this weekend. Good
  for the `community` category, weak for the featured list.
- **Date parsing.** "Fri 7pm" with no year, multi-day festivals, all-day vs.
  timed, doors vs. showtime, the DST weekend. Least glamorous, most common
  source of wrong output. **Write tests.**
- **Cold start.** A site with 14 events looks abandoned. First run should pull
  forward 90 days, not 7. Consider manually backfilling recurring annual events
  so series pages have history on launch day.
- **The venue alias map.** One hand-built afternoon, ~40-60 Mobile venues.
  No shortcut exists.

## 15. Definition of done for V1

- [ ] Tier 1 collectors running weekly via GitHub Actions
- [ ] SQLite store with `raw_pulls` archiving every run
- [ ] Dedup across the full canonical set, including intra-source
- [ ] Series URLs live, one-off expiry rule implemented
- [ ] Confidence gates implemented; review queue receiving only flagged items
- [ ] First 2-3 runs reviewed manually before gates are loosened
- [ ] Silent-breakage alerting on every source
- [ ] mobilebayevents.com publishing weekly with satellite city pages
- [ ] Brooks has personally used it three weeks running

## 16. Scheduled review — set before build, not after

> **Review date: October 1, 2027** (12 months from launch).
>
> **This is a forced look, not an automatic kill.** On that date, open the
> project and make an actual decision. Any of these is a good reason to keep it:
>
> - Brooks is personally using it
> - It's ranking — real Search Console impressions, some page-one placements
> - It's feeding other properties (GCBV seasonal pages, etc.)
> - Something unanticipated grew out of it
>
> **Default if none of the above: let the domain lapse.** Keep the venue alias
> map, the `raw_pulls` history, and the matcher module (§17).

The point is not the killing — cheap, durable assets that accumulate optionality
are a legitimate strategy, and you cannot see the future of a maybe. The point is
that a decision gets **made** rather than the project simply never surfacing.

This thing is cheap to build, cheap to run, and — with confidence-gated
auto-publish (§11) — refreshes itself without human input. It will never generate
enough friction to prompt a review on its own. **A site that updates itself
forever is exactly the failure mode where a dead project looks alive.**

**Put the review date in a calendar now.** A trigger nobody is reminded of is
not a trigger.

## 17. Build the matcher as a standalone module

Entity resolution with source-priority merge — collapse N messy records
describing one real-world thing, decide which source wins per field — is a
pattern that recurs across the portfolio (license records vs. websites,
vendor SKUs across suppliers, duplicate CRM contacts).

Build it with the event schema **passed in**, not baked in. Same weekend either
way. The difference is whether the next project imports it or rewrites it.
