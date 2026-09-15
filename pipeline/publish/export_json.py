"""Third consumer: a JSON feed per region at site/api/<region>.json.

Proves the store/publish split — this file touches no pipeline code — and gives the
phase-2 GCBV Next.js site something to read. Only redistributable + attributed fields.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .. import config, db
from ..dates import from_utc
from ..scoring import primary_source


def export(conn: sqlite3.Connection, out: Path | None = None, regions: tuple[str, ...] = ("mobile", "coastal")) -> dict[str, int]:
    out = (out or config.SITE) / "api"
    out.mkdir(parents=True, exist_ok=True)
    venues = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM venues")}
    sources = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM sources")}
    counts: dict[str, int] = {}
    rows = conn.execute(
        """SELECT o.*, s.slug AS series_slug FROM occurrences o JOIN series s ON s.id=o.series_id
           WHERE o.publish_state='published' AND o.status='active' AND o.end_utc >= datetime('now') ORDER BY o.start_utc"""
    ).fetchall()
    for region in regions:
        items = []
        for r in rows:
            if region not in db.uj(r["regions"]):
                continue
            v = venues.get(r["venue_id"]) if r["venue_id"] else None
            p = primary_source(conn, r["id"])
            src = sources.get(p["source_id"]) if p else None
            items.append({
                "id": r["id"], "series_slug": r["series_slug"], "title": r["title_raw"],
                "start": from_utc(r["start_utc"], r["timezone"]).isoformat(),
                "end": from_utc(r["end_utc"], r["timezone"]).isoformat(),
                "all_day": bool(r["all_day"]), "category": r["category"],
                "venue": {"slug": v["slug"], "name": v["canonical_name"], "city": v["city"], "regions": db.uj(v["regions"])} if v else {"name": r["venue_name_raw"]},
                "price": r["price"], "ticket_url": r["ticket_url"],
                "info_url": (p["origin_url"] or p["source_url"]) if p else r["info_url"],
                "source": {"name": src["name"], "tier": src["tier"], "redistributable": bool(src["redistributable"])} if src else None,
                "image": {"url": r["image_url"], "credit": r["image_credit"]} if r["image_ok"] else None,
                "curation_score": r["curation_score"], "independent_source_count": r["independent_source_count"],
            })
        (out / f"{region}.json").write_text(json.dumps({"region": region, "generated": db.now_iso(), "events": items}, ensure_ascii=False, indent=1), encoding="utf-8")
        counts[region] = len(items)
    return counts
