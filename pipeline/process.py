"""normalize -> dedup (whole canonical set, incl. intra-source) -> series -> scoring -> images
-> freshness -> gates. Runs against raw_pulls for one run_id; idempotent per (source, external_id)."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from collections import defaultdict
from datetime import date

from . import config, db, freshness, review, scoring
from .categories import classify_all
from .collect import load_run_with_ids
from .dates import default_end, iso_utc
from .matcher import Matcher, MatchSchema
from .models import RawEvent
from .scoring import TIER_RANK
from .text import clean_title, norm_key, slugify, title_key
from .venues import VenueResolver

log = logging.getLogger("process")


# ---------- normalization ----------

def normalize(ev: RawEvent, source: dict, resolver: VenueResolver) -> dict | None:
    title = clean_title(ev.title)
    if not title or ev.start_local is None:
        return None
    start = ev.start_local
    end = ev.end_local
    time_tba = bool(getattr(ev, "time_tba", False))
    if end is None or end <= start:
        end = default_end(start, ev.all_day or time_tba)
    # one-hop origin: a listing linking to a venue's own domain hands us the Tier A source
    origin_url, origin_tier, origin_venue = "", None, None
    for candidate in (ev.website, ev.ticket_url, ev.info_url if source["tier"] != "A" else ""):
        ov = resolver.origin_for_url(candidate)
        if ov:
            origin_url, origin_tier, origin_venue = candidate, "A", ov
            break
    vm = resolver.resolve(ev.venue_name, ev.venue_address, ev.info_url if source["tier"] == "A" else None)
    if vm is None and origin_venue is not None and not ev.venue_name:
        vm = resolver.resolve(origin_venue["name"])
    default_venue = (source.get("config") or {}).get("default_venue")
    if vm is None and not ev.venue_name and default_venue:
        dv = next((v for v in config.venues() if v["slug"] == default_venue), None)
        vm = resolver.resolve(dv["name"]) if dv else None
    venue_key = f"k:{norm_key(ev.venue_name) or norm_key(ev.venue_address) or ''}"
    if vm:
        venue_key = f"v:{vm.slug}"
    regions = (vm.regions if vm else None) or ev.regions or source.get("regions") or []
    return {
        "title": title,
        "title_key": title_key(title),
        "start_utc": iso_utc(start),
        "end_utc": iso_utc(end),
        "timezone": ev.timezone,
        "local_day": start.date().isoformat(),
        "all_day": int(ev.all_day),
        "time_tba": int(time_tba),
        "date_confident": int(ev.date_confident),
        "venue_slug": vm.slug if vm else None,
        "venue_name_raw": ev.venue_name or ev.venue_address,
        "venue_key": venue_key,
        "city": (vm.city if vm else ev.city) or "",
        "description": ev.description or "",
        "price": ev.price or "",
        "ticket_url": ev.ticket_url or "",
        "info_url": ev.info_url or "",
        "category": classify_all(title, ev.categories, ev.description)[0],
        "categories": classify_all(title, ev.categories, ev.description),
        "regions": list(regions),
        "origin_url": origin_url,
        "origin_tier": origin_tier,
        "image_url": ev.image_url or "",
        "image_credit": (ev.raw.get("image_credit") if isinstance(ev.raw, dict) else None) or source["name"],
        "cancelled": bool(getattr(ev, "cancelled", False)),
        "rank": (TIER_RANK.get(source["tier"], 9), 0 if source.get("curated") else 1),
    }


# ---------- the run ----------

def process(conn: sqlite3.Connection, run_id: int, source_results: dict[str, dict]) -> dict:
    s = config.settings()
    dd = s.get("dedup", {})
    run = conn.execute("SELECT started_at FROM runs WHERE id=?", (run_id,)).fetchone()
    run_started = run["started_at"]
    sources = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM sources")}
    for src in sources.values():
        src["config"] = db.uj(src["config"], {})
        src["regions"] = db.uj(src["regions"])
    resolver = VenueResolver()
    venue_ids = {r["slug"]: r["id"] for r in conn.execute("SELECT id, slug FROM venues")}

    occ_matcher = Matcher(MatchSchema(
        text_of=lambda r: r["title_key"],
        bucket_of=lambda r: (r["local_day"], r["venue_key"]),
        match_threshold=float(dd.get("match_threshold", 82)),
        ambiguous_floor=float(dd.get("ambiguous_floor", 70)),
        rank_of=lambda r: r.get("rank", (9, 9)),
        field_rules={"description": "longest", "price": "first_nonempty", "ticket_url": "first_nonempty",
                     "image_url": "first_nonempty"},
    ))
    series_matcher = Matcher(MatchSchema(
        text_of=lambda r: r["title_key"],
        bucket_of=lambda r: r["venue_key"],
        match_threshold=float(dd.get("match_threshold", 82)),
        ambiguous_floor=101,  # series: match or new, overrides handle the rest
    ))

    items = load_run_with_ids(conn, run_id)
    # best sources first, so canonical records are born from the best data
    items.sort(key=lambda t: (TIER_RANK.get(sources[t[1].source_id]["tier"], 9), 0 if sources[t[1].source_id]["curated"] else 1, t[0]))

    created: set[int] = set()
    touched: set[int] = set()
    now = db.now_iso()
    stats = defaultdict(int)

    with db.tx(conn):
        for raw_pull_id, ev in items:
            src = sources.get(ev.source_id)
            if not src:
                continue
            n = normalize(ev, src, resolver)
            if n is None:
                stats["unparseable"] += 1
                continue
            venue_id = venue_ids.get(n["venue_slug"]) if n["venue_slug"] else None
            existing = conn.execute(
                "SELECT * FROM occurrence_sources WHERE source_id=? AND external_id=?", (ev.source_id, ev.external_id)
            ).fetchone()
            if existing:
                _refresh(conn, existing, n, venue_id, raw_pull_id, now, sources)
                touched.add(existing["occurrence_id"])
                stats["refreshed"] += 1
                continue

            cands = [dict(r) for r in conn.execute(
                "SELECT id, title_key, local_day, venue_key FROM occurrences WHERE local_day=? AND venue_key=?",
                (n["local_day"], n["venue_key"]),
            )]
            res = occ_matcher.best(n, cands)
            if res.decision == "match":
                oid = res.candidate["id"]
                _merge_into(conn, oid, n, occ_matcher, now)
                stats["merged"] += 1
            else:
                series_id = _find_or_create_series(conn, n, venue_id, series_matcher, now)
                oid = _create_occurrence(conn, n, venue_id, series_id, res, now)
                created.add(oid)
                stats["created"] += 1
                if res.decision == "ambiguous":
                    stats["ambiguous"] += 1
            conn.execute(
                """INSERT INTO occurrence_sources (occurrence_id, source_id, external_id, source_url, origin_url, origin_tier,
                   image_url, first_seen, last_seen, consecutive_misses, self_promoted, raw_pull_id)
                   VALUES (?,?,?,?,?,?,?,?,?,0,0,?)""",
                (oid, ev.source_id, ev.external_id, n["info_url"], n["origin_url"] or None, n["origin_tier"],
                 n["image_url"] or None, now, now, raw_pull_id),
            )
            if n["cancelled"]:
                conn.execute("UPDATE occurrences SET status='cancelled', updated_at=? WHERE id=? AND status IN ('active','flagged_cancelled')", (now, oid))
                stats["source_cancelled"] += 1
            touched.add(oid)

        stats["re_resolved"] = _reresolve_unknown_venues(conn, resolver, venue_ids, now)
        _apply_overrides(conn, series_matcher, now)
        scoring.rescore(conn)
        _assign_images(conn, sources)
        _detect_cadence(conn)
        flagged = freshness.mark_misses(conn, run_id, run_started, source_results)
        stats["flagged_cancelled"] = len(flagged)
        strict = db.run_count(conn) <= int(s.get("review", {}).get("strict_until_run", 3))
        summary = review.evaluate(conn, run_id, source_results, strict, created)

    alerts = freshness.breakage_alerts(conn, run_id, source_results)
    return {"stats": dict(stats), "summary": summary, "alerts": alerts, "strict": strict}


# ---------- helpers ----------

def _refresh(conn, existing, n, venue_id, raw_pull_id, now, sources) -> None:
    conn.execute(
        """UPDATE occurrence_sources SET last_seen=?, consecutive_misses=0, source_url=?, origin_url=?, origin_tier=?,
           image_url=?, raw_pull_id=? WHERE id=?""",
        (now, n["info_url"], n["origin_url"] or None, n["origin_tier"], n["image_url"] or None, raw_pull_id, existing["id"]),
    )
    occ = conn.execute("SELECT * FROM occurrences WHERE id=?", (existing["occurrence_id"],)).fetchone()
    if not occ:
        return
    primary = scoring.primary_source(conn, occ["id"])
    if primary and primary["source_id"] == existing["source_id"]:
        # the best source's dates win; a moved event moves
        if occ["category"] != n["category"] or db.uj(occ["categories"]) != n["categories"]:
            conn.execute("UPDATE occurrences SET category=?, categories=? WHERE id=?", (n["category"], db.j(n["categories"]), occ["id"]))
        if (occ["start_utc"], occ["end_utc"], occ["time_tba"], occ["date_confident"]) != (n["start_utc"], n["end_utc"], n["time_tba"], n["date_confident"]) or occ["title_raw"] != n["title"]:
            conn.execute(
                """UPDATE occurrences SET start_utc=?, end_utc=?, local_day=?, all_day=?, time_tba=?, date_confident=?, title_raw=?, title_key=?, updated_at=?
                   WHERE id=?""",
                (n["start_utc"], n["end_utc"], n["local_day"], n["all_day"], n["time_tba"], n["date_confident"], n["title"], n["title_key"], now, occ["id"]),
            )
    if occ["venue_id"] is None and venue_id is not None:
        conn.execute("UPDATE occurrences SET venue_id=?, venue_key=?, city=?, regions=?, updated_at=? WHERE id=?",
                     (venue_id, n["venue_key"], n["city"], db.j(n["regions"]), now, occ["id"]))
    if n["description"] and (not occ["description"] or (primary and primary["source_id"] == existing["source_id"] and occ["description"] != n["description"])):
        conn.execute("UPDATE occurrences SET description=? WHERE id=?", (n["description"], occ["id"]))
    if n["cancelled"] and occ["status"] in ("active", "flagged_cancelled"):
        conn.execute("UPDATE occurrences SET status='cancelled', updated_at=? WHERE id=?", (now, occ["id"]))


def _merge_into(conn, oid, n, matcher: Matcher, now) -> None:
    occ = dict(conn.execute("SELECT description, price, ticket_url, image_url FROM occurrences WHERE id=?", (oid,)).fetchone())
    occ["rank"] = (-1, -1)  # the existing canonical record was born from the best source seen so far
    merged = matcher.merge([occ, {k: n[k] for k in ("description", "price", "ticket_url", "image_url", "rank")}])
    conn.execute(
        "UPDATE occurrences SET description=?, price=?, ticket_url=?, updated_at=? WHERE id=?",
        (merged["description"] or "", merged["price"] or "", merged["ticket_url"] or "", now, oid),
    )


def _create_occurrence(conn, n, venue_id, series_id, res, now) -> int:
    cur = conn.execute(
        """INSERT INTO occurrences (series_id, title_raw, title_key, start_utc, end_utc, timezone, local_day, all_day, time_tba, date_confident,
           venue_id, venue_name_raw, venue_key, city, regions, description, price, ticket_url, info_url, category, categories, status,
           match_ambiguous, match_candidate_id, publish_state, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'active',?,?,'held',?,?)""",
        (series_id, n["title"], n["title_key"], n["start_utc"], n["end_utc"], n["timezone"], n["local_day"], n["all_day"], n["time_tba"],
         n["date_confident"], venue_id, n["venue_name_raw"], n["venue_key"], n["city"], db.j(n["regions"]), n["description"], n["price"],
         n["ticket_url"], n["info_url"], n["category"], db.j(n["categories"]), int(res.decision == "ambiguous"),
         res.candidate["id"] if res.decision == "ambiguous" and res.candidate else None, now, now),
    )
    return cur.lastrowid


def _find_or_create_series(conn, n, venue_id, matcher: Matcher, now) -> int:
    cands = [dict(r) for r in conn.execute(
        "SELECT id, title_key, venue_key FROM series WHERE venue_key=?", (n["venue_key"],)
    )]
    res = matcher.best(n, cands)
    if res.decision == "match":
        return res.candidate["id"]
    base = slugify(n["title"])
    slug = base
    if conn.execute("SELECT 1 FROM series WHERE slug=?", (slug,)).fetchone():
        vs = n["venue_slug"] or norm_key(n["venue_name_raw"]).replace(" ", "-")[:30]
        slug = f"{base}-{vs}" if vs else base
    if conn.execute("SELECT 1 FROM series WHERE slug=?", (slug,)).fetchone():
        slug = f"{slug}-{hashlib.sha1((slug + n['local_day']).encode()).hexdigest()[:6]}"
    cur = conn.execute(
        """INSERT INTO series (slug, canonical_title, title_key, venue_id, venue_name_raw, venue_key, description, cadence, category, created_at)
           VALUES (?,?,?,?,?,?,?,'one_off',?,?)""",
        (slug, n["title"], n["title_key"], venue_id, n["venue_name_raw"], n["venue_key"], n["description"], n["category"], now),
    )
    return cur.lastrowid


def _reresolve_unknown_venues(conn, resolver: VenueResolver, venue_ids: dict, now) -> int:
    """The alias map grew since last run; unknown venues get another shot."""
    n = 0
    for occ in conn.execute("SELECT id, venue_name_raw, series_id FROM occurrences WHERE venue_id IS NULL AND start_utc >= datetime('now','-1 day')").fetchall():
        vm = resolver.resolve(occ["venue_name_raw"], occ["venue_name_raw"])
        if not vm:
            continue
        vid = venue_ids.get(vm.slug)
        if vid is None:
            continue
        conn.execute("UPDATE occurrences SET venue_id=?, venue_key=?, city=?, regions=?, updated_at=? WHERE id=?",
                     (vid, f"v:{vm.slug}", vm.city, db.j(vm.regions), now, occ["id"]))
        conn.execute("UPDATE series SET venue_id=?, venue_key=? WHERE id=? AND venue_id IS NULL", (vid, f"v:{vm.slug}", occ["series_id"]))
        n += 1
    return n


def _apply_overrides(conn, series_matcher: Matcher, now) -> None:
    ov = config.overrides()
    for pair in ov.get("merge", []):
        if not pair or len(pair) != 2:
            continue
        keep, drop = int(pair[0]), int(pair[1])
        if keep == drop or not conn.execute("SELECT 1 FROM occurrences WHERE id=?", (drop,)).fetchone():
            continue
        if not conn.execute("SELECT 1 FROM occurrences WHERE id=?", (keep,)).fetchone():
            continue
        conn.execute("UPDATE OR IGNORE occurrence_sources SET occurrence_id=? WHERE occurrence_id=?", (keep, drop))
        conn.execute("DELETE FROM occurrence_sources WHERE occurrence_id=?", (drop,))
        conn.execute("UPDATE review_queue SET resolved_at=? WHERE occurrence_id=? AND resolved_at IS NULL", (now, drop))
        conn.execute("DELETE FROM review_queue WHERE occurrence_id=?", (drop,))
        conn.execute("DELETE FROM occurrences WHERE id=?", (drop,))
        conn.execute("UPDATE occurrences SET match_ambiguous=0, match_candidate_id=NULL, updated_at=? WHERE id=?", (now, keep))
    for oid, slug in (ov.get("attach_to_series") or {}).items():
        srow = conn.execute("SELECT id FROM series WHERE slug=?", (slug,)).fetchone()
        if srow:
            conn.execute("UPDATE occurrences SET series_id=?, updated_at=? WHERE id=?", (srow["id"], now, int(oid)))
    for oid in ov.get("cancelled", []):
        conn.execute("UPDATE occurrences SET status='cancelled', updated_at=? WHERE id=?", (now, int(oid)))
    for oid in ov.get("not_cancelled", []):
        conn.execute("UPDATE occurrences SET status='active', updated_at=? WHERE id=? AND status IN ('flagged_cancelled','cancelled')", (now, int(oid)))
        conn.execute("UPDATE occurrence_sources SET consecutive_misses=0 WHERE occurrence_id=?", (int(oid),))
    for pair in ov.get("never_merge", []):
        if pair and len(pair) == 2:
            conn.execute("UPDATE occurrences SET match_ambiguous=0, match_candidate_id=NULL WHERE id IN (?,?)", (int(pair[0]), int(pair[1])))
    # series with no occurrences left (after merges) are noise
    conn.execute("DELETE FROM series WHERE id NOT IN (SELECT DISTINCT series_id FROM occurrences)")


def _assign_images(conn, sources: dict) -> None:
    """Gate on source tier, not on judgment about the act. Ticketmaster images are never used."""
    for occ in conn.execute("SELECT id FROM occurrences WHERE start_utc >= datetime('now','-1 day')").fetchall():
        rows = conn.execute(
            """SELECT os.image_url, os.source_url, os.source_id, os.origin_tier, s.tier, s.curated, s.name, s.collector_type
               FROM occurrence_sources os JOIN sources s ON s.id=os.source_id WHERE os.occurrence_id=? AND os.image_url IS NOT NULL AND os.image_url != ''""",
            (occ["id"],),
        ).fetchall()
        rows = [r for r in rows if r["collector_type"] != "ticketmaster"]
        if not rows:
            conn.execute("UPDATE occurrences SET image_ok=0, image_url=NULL, image_source_url=NULL, image_credit=NULL WHERE id=?", (occ["id"],))
            continue
        best = min(rows, key=lambda r: (TIER_RANK.get("A" if r["origin_tier"] == "A" else r["tier"], 9), 0 if r["curated"] else 1))
        conn.execute(
            "UPDATE occurrences SET image_ok=1, image_url=?, image_source_url=?, image_credit=? WHERE id=?",
            (best["image_url"], best["source_url"], best["name"], occ["id"]),
        )


def _detect_cadence(conn) -> None:
    """annual | weekly | monthly | one_off | irregular, from the spacing of a series' occurrences."""
    notes = config.series_notes()
    for srow in conn.execute("SELECT id, slug FROM series").fetchall():
        override = (notes.get(srow["slug"]) or {}).get("cadence")
        if override:
            conn.execute("UPDATE series SET cadence=? WHERE id=?", (override, srow["id"]))
            continue
        days = sorted({date.fromisoformat(r[0]) for r in conn.execute("SELECT local_day FROM occurrences WHERE series_id=?", (srow["id"],))})
        gaps = [(b - a).days for a, b in zip(days, days[1:]) if (b - a).days > 1]  # consecutive days = one multi-day event
        if not gaps:
            cadence = "one_off"
        elif any(340 <= g <= 390 for g in gaps):
            cadence = "annual"
        elif len(gaps) >= 2 and all(g <= 8 for g in gaps):
            cadence = "weekly"   # includes Tue/Thu style patterns
        elif len(gaps) >= 2 and all(26 <= g <= 35 for g in gaps):
            cadence = "monthly"
        elif len(gaps) >= 2 and all(12 <= g <= 16 for g in gaps):
            cadence = "monthly"  # every-other-week reads as "monthly-ish" on the page
        else:
            cadence = "irregular"
        top = conn.execute("SELECT category FROM occurrences WHERE series_id=? GROUP BY category ORDER BY COUNT(*) DESC, MAX(start_utc) DESC LIMIT 1", (srow["id"],)).fetchone()
        conn.execute("UPDATE series SET cadence=?, category=COALESCE(?, category) WHERE id=?", (cadence, top[0] if top else None, srow["id"]))
