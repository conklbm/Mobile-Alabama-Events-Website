"""Cancellation detection, silent-breakage alarms.

Guards (both mandatory):
1. Never run the miss check for a source whose pull failed, was skipped, returned
   zero, or underdelivered — one broken parser would flag fifty events as canceled.
2. Two consecutive misses, not one. Sites paginate.

Flagged items go to the review queue as "possibly canceled." Never auto-remove.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from . import config, db
from .scoring import TIER_RANK


def mark_misses(conn: sqlite3.Connection, run_id: int, run_started_at: str, source_results: dict[str, dict]) -> list[int]:
    """Increment consecutive_misses for future events a healthy source stopped listing.
    Returns occurrence ids newly flagged as possibly canceled."""
    need = int(config.settings().get("freshness", {}).get("consecutive_misses_to_flag", 2))
    flagged: list[int] = []
    now = db.now_iso()
    for sid, res in source_results.items():
        if res["status"] != "ok" or res["count"] == 0 or res.get("underdelivered"):
            continue  # guard 1
        rows = conn.execute(
            """SELECT os.id, os.occurrence_id, os.consecutive_misses, s.tier
               FROM occurrence_sources os
               JOIN occurrences o ON o.id = os.occurrence_id
               JOIN sources s ON s.id = os.source_id
               WHERE os.source_id=? AND o.start_utc > ? AND o.status='active'
                 AND (os.raw_pull_id IS NULL OR os.raw_pull_id NOT IN (SELECT id FROM raw_pulls WHERE run_id=?))""",
            (sid, now, run_id),
        ).fetchall()
        for r in rows:
            misses = r["consecutive_misses"] + 1
            conn.execute("UPDATE occurrence_sources SET consecutive_misses=? WHERE id=?", (misses, r["id"]))
            if misses < need:
                continue  # guard 2
            if _should_flag(conn, r["occurrence_id"], sid, run_id):
                conn.execute("UPDATE occurrences SET status='flagged_cancelled', updated_at=? WHERE id=? AND status='active'", (now, r["occurrence_id"]))
                flagged.append(r["occurrence_id"])
    return flagged


def _should_flag(conn: sqlite3.Connection, occurrence_id: int, missing_source: str, run_id: int) -> bool:
    """Flag when the missing source is the best-ranked one (or the only one) and
    nothing of equal or higher rank still confirms the event this run."""
    rows = conn.execute(
        """SELECT os.source_id, os.origin_tier, s.tier,
                  (os.raw_pull_id IN (SELECT id FROM raw_pulls WHERE run_id=?)) AS seen_now
           FROM occurrence_sources os JOIN sources s ON s.id = os.source_id WHERE os.occurrence_id=?""",
        (run_id, occurrence_id),
    ).fetchall()

    def rank(r):
        t = "A" if r["origin_tier"] == "A" else r["tier"]
        return TIER_RANK.get(t, 9)

    missing = [r for r in rows if r["source_id"] == missing_source]
    if not missing:
        return False
    mrank = rank(missing[0])
    for r in rows:
        if r["source_id"] == missing_source:
            continue
        if r["seen_now"] and rank(r) <= mrank:
            return False  # a source at least as good still sees it
    return True


def breakage_alerts(conn: sqlite3.Connection, run_id: int, source_results: dict[str, dict]) -> list[str]:
    """Human-readable alerts: failed pulls, underdelivery, sources gone stale."""
    weeks = int(config.settings().get("freshness", {}).get("stale_source_weeks", 3))
    cutoff = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).strftime("%Y-%m-%dT%H:%M:%SZ")
    alerts: list[str] = []
    for s in conn.execute("SELECT * FROM sources ORDER BY id"):
        sid = s["id"]
        res = source_results.get(sid)
        if res is None:
            continue
        if res["status"] == "failed":
            alerts.append(f"**{s['name']}** (`{sid}`): pull FAILED — {res.get('error')}")
        elif res["status"] == "skipped":
            alerts.append(f"**{s['name']}** (`{sid}`): skipped — {res.get('error')}")
        elif res.get("underdelivered"):
            alerts.append(f"**{s['name']}** (`{sid}`): returned {res['count']} events, expected at least {s['expected_min_events']}")
        last = s["last_successful_pull"]
        if last and last < cutoff:
            alerts.append(f"**{s['name']}** (`{sid}`): no successful pull since {last[:10]} (> {weeks} weeks)")
    return alerts
