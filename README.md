# Mobile Bay Events

Weekly automated pipeline that collects local events from structured sources, dedups them into
canonical records, and publishes a static site (mobilebayevents.com). SQLite is the single source
of truth; publishers are read-only consumers.

```
collectors/ ──▶ raw_pulls (append-only) ──▶ normalize ──▶ dedup ──▶ canonical ──▶ review gates ──▶ site/
```

## Run it

```bash
uv sync
cp .env.example .env            # add TICKETMASTER_API_KEY (optional; collector skips without it)
uv run pytest -q
uv run python -m pipeline run   # collect -> process -> publish -> prints the review issue
uv run python -m pipeline queue # open review items
uv run python -m pipeline approve --strict   # release strict-mode holds after eyeballing them
uv run python -m pipeline publish            # re-render site/ after approving or editing YAML
```

Preview the site: `python -m http.server -d site 8000`.

## What you edit (all in `data/`)

| file | what |
|---|---|
| `venues.yaml` | **The alias map.** Unknown venue in the review issue → add an alias here. Next run resolves it. |
| `sources.yaml` | Source registry: collector type, tier, regions, license notes, brand tokens, expected minimum. |
| `series_notes.yaml` | Original per-event content: blurb, parking, kids flag, cadence/category overrides, feature pins. |
| `pages.yaml` | Intros for city and category pages, About/Contact copy. |
| `overrides.yaml` | Force merges, series attachment, cancel / un-cancel, force-publish. |
| `manual/events.csv` | The weekly Facebook scan (hand-entered rows). |
| `settings.yaml` | Thresholds, strict-mode run count, window, site URL. |
| `categories.yaml` | Keyword rules for the seven categories. |

`data/events.db` is committed by the weekly job. Don't hand-edit it.

## Review loop

The GitHub Action runs Thursdays 6 AM Central, commits the store + site, and opens an issue
titled "N items need review" when anything needs a human. Named booleans, never a score:

- `venue_unknown` — add an alias to `venues.yaml` (most common)
- `match_ambiguous` — `overrides.yaml` → `merge: [[keep, drop]]` or `never_merge`
- `cancellation_flagged` — primary source stopped listing it two runs running; confirm or clear
- `source_underdelivered` / source alerts — a parser probably broke; check the source
- `date_uncertain` — parser guessed a year or time

**Automatic first pass.** A cloud routine ("Mobile Bay Events: resolve review queue",
https://claude.ai/code/routines) runs Thursdays 7 AM Central, an hour after the pipeline. It reads the
review issue, researches each unknown venue on the web, adds confident venues/aliases to `venues.yaml`,
pushes, and writes `data/routine-notes.md`. The `apply-config` workflow then re-processes, republishes,
posts the notes to the issue, and closes it if nothing remains. Brooks only hears about judgment calls,
each with a ready-to-send reply command.

**Reply by email.** Reply to the issue email (or comment on the issue) with one command per line:

```
approve 73 79
cancel 151
alias "Raw venue name" = venue-slug
venue new-slug "Venue Name" Mobile
merge 271 269   |   never-merge 271 269   |   not-cancelled 222   |   ignore 73
```

The `review-commands` Action applies them, re-processes, republishes, replies on the thread, and
closes the issue when nothing is left. Events a source itself marks cancelled are removed
automatically and listed as FYI only.

**Strict mode** (`settings.review.strict_until_run`, default 3): every new event is held and listed
in the issue. Skim, run `approve --strict`, republish. After run 3, gated events auto-publish.

## Deploy

Vercel, static, no build: `vercel.json` sets `outputDirectory: site`. The weekly job commits `site/`;
Vercel's git integration deploys it. Canonical host is `www.mobilebayevents.com` (apex redirects to www).
`*.vercel.app` gets `X-Robots-Tag: noindex` from `vercel.json`.

Go-live gate (from the house checklist): attach the domain, confirm which host Vercel actually serves,
set `SITE_URL` to match, then `bash ~/.claude/scripts/check-domain.sh mobilebayevents.com /events/ <project>.vercel.app`,
then submit the sitemap.

## Layout

```
pipeline/
  collectors/     tribe (WP Events Calendar), ticketmaster, civicplus_rss, ics, jsonld, manual
  matcher/        standalone entity-resolution module (schema passed in) — reusable
  collect.py      run collectors, archive to raw_pulls
  process.py      normalize → dedup → series → scoring → images → freshness → gates
  review.py       gates, queue, issue markdown, approve
  freshness.py    two-miss cancellation detection with guards, silent-breakage alerts
  scoring.py      self-promo detector, independent_source_count, curation_score
  publish/        mobile.py (site), export_json.py (JSON feed per region), templates/, static/
data/             everything human-edited + events.db
site/             build output (committed)
tests/            dates, matcher, venues/text, collectors, end-to-end
```

## Scheduled review

**October 1, 2027.** Open the project and decide: using it, ranking, feeding other properties, or
something grew out of it → keep. Otherwise let the domain lapse; keep `venues.yaml`, `raw_pulls`,
and `pipeline/matcher`. Put it in the calendar.
