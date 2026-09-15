"""Run every collector, archive every record in raw_pulls, record per-source outcome."""

from __future__ import annotations

import json
import logging
import sqlite3
import traceback
from dataclasses import asdict
from datetime import date, datetime, timedelta

from . import config, db
from .collectors import COLLECTORS, CollectorError, make_session
from .models import RawEvent

log = logging.getLogger("collect")


def _serialize(ev: RawEvent) -> str:
    d = asdict(ev)
    for k in ("start_local", "end_local"):
        v = d.get(k)
        d[k] = v.isoformat() if isinstance(v, datetime) else None
    return json.dumps(d, ensure_ascii=False, default=str)


def deserialize(payload: str) -> RawEvent:
    d = json.loads(payload)
    for k in ("start_local", "end_local"):
        if d.get(k):
            d[k] = datetime.fromisoformat(d[k])
    return RawEvent(**d)


def collect(conn: sqlite3.Connection, run_id: int, only: list[str] | None = None) -> dict[str, dict]:
    """Returns {source_id: {status, count, underdelivered, error}}."""
    s = config.settings().get("collect", {})
    today = date.today()
    start, end = today, today + timedelta(days=int(s.get("window_days", 90)))
    session = make_session()
    results: dict[str, dict] = {}
    for src in config.sources():
        sid = src["id"]
        if only and sid not in only:
            continue
        cls = COLLECTORS.get(src["collector_type"])
        if cls is None:
            results[sid] = {"status": "failed", "count": 0, "underdelivered": 0, "error": f"unknown collector_type {src['collector_type']}"}
            _record(conn, run_id, sid, results[sid])
            continue
        log.info("collecting %s (%s)", sid, src["collector_type"])
        try:
            events = cls(src, session).fetch(start, end)
            status, error = "ok", None
        except CollectorError as e:
            events, error = [], str(e)
            status = "skipped" if "skipped" in error else "failed"
            log.warning("%s: %s", sid, error)
        except Exception as e:  # a broken parser must not take the run down
            events, status, error = [], "failed", f"{type(e).__name__}: {e}"
            log.error("%s crashed:\n%s", sid, traceback.format_exc())
        pulled_at = db.now_iso()
        with db.tx(conn):
            for ev in events:
                conn.execute(
                    "INSERT INTO raw_pulls (run_id, source_id, external_id, pulled_at, payload) VALUES (?,?,?,?,?)",
                    (run_id, sid, ev.external_id, pulled_at, _serialize(ev)),
                )
        under = int(status == "ok" and len(events) < int(src.get("expected_min_events", 0)))
        results[sid] = {"status": status, "count": len(events), "underdelivered": under, "error": error}
        _record(conn, run_id, sid, results[sid])
        if status == "ok":
            with db.tx(conn):
                conn.execute("UPDATE sources SET last_successful_pull=?, last_event_count=? WHERE id=?", (pulled_at, len(events), sid))
        log.info("%s: %s, %d events%s", sid, status, len(events), " (UNDERDELIVERED)" if under else "")
    return results


def _record(conn: sqlite3.Connection, run_id: int, sid: str, r: dict) -> None:
    with db.tx(conn):
        conn.execute(
            """INSERT INTO source_runs (run_id, source_id, status, event_count, underdelivered, error) VALUES (?,?,?,?,?,?)
               ON CONFLICT(run_id, source_id) DO UPDATE SET status=excluded.status, event_count=excluded.event_count,
               underdelivered=excluded.underdelivered, error=excluded.error""",
            (run_id, sid, r["status"], r["count"], r["underdelivered"], r["error"]),
        )


def load_run(conn: sqlite3.Connection, run_id: int) -> list[RawEvent]:
    rows = conn.execute("SELECT payload FROM raw_pulls WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
    return [deserialize(r["payload"]) for r in rows]


def load_run_with_ids(conn: sqlite3.Connection, run_id: int) -> list[tuple[int, RawEvent]]:
    rows = conn.execute("SELECT id, payload FROM raw_pulls WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
    return [(r["id"], deserialize(r["payload"])) for r in rows]


def source_results(conn: sqlite3.Connection, run_id: int) -> dict[str, dict]:
    out = {}
    for r in conn.execute("SELECT * FROM source_runs WHERE run_id=?", (run_id,)):
        out[r["source_id"]] = {"status": r["status"], "count": r["event_count"], "underdelivered": r["underdelivered"], "error": r["error"]}
    return out
