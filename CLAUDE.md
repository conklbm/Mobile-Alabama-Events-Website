# CLAUDE.md — Mobile Bay Events

## Project
- **Name:** Mobile Bay Events (mobilebayevents.com) — Gulf Coast events pipeline, V1 publisher.
- **Purpose:** Weekly automated collection of local events → dedup → static site. Brooks wants one place to see what's on; the domain accumulates SEO equity meanwhile.
- **Audience:** People who live in Mobile / Eastern Shore / Dauphin Island. (Phase 2: coastal section on gulfcoastbeachvibes.com for trip planners — separate blurbs, same store.)
- **Status:** Built 2026-09-14. Not yet deployed. Spec: `docs/PRD-events-pipeline-v1.md`, sources: `docs/EVENT-SOURCE-REGISTRY.md`.
- **Scheduled review:** October 1, 2027 — forced decision, not auto-kill (PRD §16).

## Stack
- Python 3.12, `uv`. SQLite (`data/events.db`, committed). rapidfuzz, icalendar, requests, Jinja2, PyYAML.
- Static site rendered to `site/`; Vercel serves it with no build (`vercel.json` → `outputDirectory: site`).
- GitHub Actions weekly cron (Thu 11:00 UTC) commits store + site, opens a review issue.
- No JS framework, no backend, no accounts. The global CLAUDE.md phases about auth/API/Sentry mostly don't apply.

## Hard rules (from the PRD — don't relitigate)
- **Storage and publishing are separate.** Publishers read the DB; a new consumer must not touch `pipeline/process.py`.
- `raw_pulls` is append-only. Never delete.
- Store UTC + explicit tz. `local_day` is the dedup bucket key.
- Primary source is computed at render time from tier rank (A venue > B ticketing > C aggregator, one-hop origin links count as A). Never stored.
- Review gates are **named booleans**, never a blended score.
- Venue aliases live in `data/venues.yaml`, not the DB.
- Ticketmaster: attribution + link-back on every listing; never reuse their images (`image_ok=0`).
- Series URLs (`/events/<slug>/`) never expire. One-offs 301 to the venue page 7 days after the event.
- Cancellation detection needs a healthy source pull AND two consecutive misses. Never auto-remove.
- Every page needs original value beyond scraped data (`series_notes.yaml`, `pages.yaml`, venue `notes`).

## Commands
```bash
uv run pytest -q
uv run python -m pipeline run            # full weekly job locally
uv run python -m pipeline queue          # open review items
uv run python -m pipeline approve --strict
uv run python -m pipeline publish
python -m http.server -d site 8000       # preview
```

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-09-14 | Static site via Jinja2 in Python, not Next.js | Same language as pipeline, zero build; phase 2 GCBV reads `site/api/coastal.json` or the DB directly. |
| 2026-09-14 | `tier_c_only` recorded but does NOT block publish by default | 92ZEW (tier C) is the biggest source; gating on tier A/B would queue hundreds/week vs. the PRD's 2–5. Flip `settings.review.gate_on_tier_c_only`. |
| 2026-09-14 | Gulf Shores / Orange Beach / Foley venues tagged `coastal` only | PRD routes coastal to GCBV. Flip a venue's `regions` to show it on the Mobile site. |
| 2026-09-14 | Registry corrections | Playhouse in the Park has no Event JSON-LD; EventKeeper (library) is now a JS app; Soul Kitchen has no Event JSON-LD but is covered by Ticketmaster. All noted in `sources.yaml`. |
| 2026-09-14 | Canonical host `www.mobilebayevents.com` | House standard. Set `SITE_URL` from what Vercel actually serves at cutover. |

## Git workflow
Ask before pulling on first touch of the repo and before any push (direct to `main` vs. dev branch + PR). See global CLAUDE.md.
