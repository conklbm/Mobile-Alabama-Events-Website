"""End-to-end against a temp SQLite store: dedup (incl. intra-source), gates, strict mode,
approve, freshness guards, publishing. Uses the real sources.yaml / venues.yaml."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from pipeline import db, review
from pipeline.collect import _serialize
from pipeline.models import RawEvent
from pipeline.process import process
from pipeline.publish.mobile import publish

CT = ZoneInfo("America/Chicago")
SOON = datetime.now(CT).replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(days=10)


def ev(source_id, ext, title, venue, start=SOON, **kw):
    return RawEvent(source_id=source_id, external_id=ext, title=title, start_local=start, venue_name=venue,
                    info_url=f"https://{source_id}.test/{ext}", **kw)


def seed(conn, run_id, events):
    with db.tx(conn):
        for e in events:
            conn.execute("INSERT INTO raw_pulls (run_id, source_id, external_id, pulled_at, payload) VALUES (?,?,?,?,?)",
                         (run_id, e.source_id, e.external_id, db.now_iso(), _serialize(e)))


def ok(**counts):
    return {sid: {"status": "ok", "count": n, "underdelivered": 0, "error": None} for sid, n in counts.items()}


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "t.db")
    with db.tx(c):
        db.sync_sources(c)
        db.sync_venues(c)
    return c


def run(conn, events, results):
    rid = db.start_run(conn)
    seed(conn, rid, events)
    out = process(conn, rid, results)
    db.finish_run(conn, rid)
    return rid, out


def test_dedup_gates_strict_and_approve(conn, tmp_path):
    events = [
        ev("92zew", "a", "Beer, BBQ & Bingo", "Moe's Original BBQ", image_url="https://92zew.net/a.jpg"),
        ev("92zew", "b", "Beer BBQ and Bingo", "Moe's Original BBQ"),           # intra-source duplicate
        ev("92zew", "c", "Mystery Show", "Nowhere Bar"),                         # unknown venue
        ev("mobilesymphony", "s1", "Beethoven 9", "Saenger Theatre", price="$25"),
        ev("themobmom", "m1", "Beethoven's Ninth", "Mobile Saenger"),            # alias + cross-source dup
    ]
    rid, out = run(conn, events, ok(**{"92zew": 3, "mobilesymphony": 1, "themobmom": 1}))
    assert out["stats"]["created"] == 3 and out["stats"]["merged"] == 2
    assert conn.execute("SELECT COUNT(*) FROM occurrences").fetchone()[0] == 3

    bingo = conn.execute("SELECT * FROM occurrences WHERE title_key LIKE '%bingo%'").fetchone()
    assert conn.execute("SELECT COUNT(*) FROM occurrence_sources WHERE occurrence_id=?", (bingo["id"],)).fetchone()[0] == 2
    assert bingo["venue_id"] is not None and bingo["image_ok"] == 1 and bingo["image_credit"] == "92ZEW"
    assert bingo["curation_score"] == 1 and bingo["independent_source_count"] == 1  # same party twice = one vote

    beet = conn.execute("SELECT * FROM occurrences WHERE title_key LIKE 'beethoven%'").fetchone()
    assert beet["price"] == "$25" and beet["curation_score"] == 1 and beet["independent_source_count"] == 2

    # strict mode: everything held; only the unknown venue is a *real* gate
    assert out["strict"] and out["summary"]["held"] == 3
    q = {r["occurrence_id"]: r for r in review.open_items(conn)}
    myst = conn.execute("SELECT id FROM occurrences WHERE title_raw='Mystery Show'").fetchone()["id"]
    assert q[myst]["venue_unknown"] == 1 and q[myst]["strict_mode"] == 0
    assert q[beet["id"]]["venue_unknown"] == 0 and q[beet["id"]]["strict_mode"] == 1

    title, body = review.issue_body(conn, rid, out["alerts"], out["summary"])
    assert "Unknown venues" in body and "Nowhere Bar" in body and "Strict-mode holds" in body

    # release the strict batch: real gates stay held
    assert review.approve(conn, strict=True) == 2
    states = dict(conn.execute("SELECT title_raw, publish_state FROM occurrences"))
    assert states["Beethoven 9"] == "published" and states["Mystery Show"] == "held"

    counts = publish(conn, tmp_path / "site", vercel_path=tmp_path / "vercel.json")
    site = tmp_path / "site"
    assert (site / "index.html").exists() and (site / "events" / "beethoven-9" / "index.html").exists()
    assert not (site / "events" / "mystery-show").exists()
    html = (site / "events" / "beethoven-9" / "index.html").read_text(encoding="utf-8")
    assert '"@type": "Event"' in html and "Saenger Theatre" in html and 'rel="canonical"' in html
    assert (site / "sitemap.xml").exists() and (site / "robots.txt").exists() and (site / "404.html").exists()
    assert (site / "daphne-al-events" / "index.html").exists()
    assert counts["series_pages"] == 2


def test_freshness_two_misses_then_flag_and_failed_source_guard(conn):
    a = [ev("mobilesymphony", "s1", "Beethoven 9", "Saenger Theatre"), ev("92zew", "z", "Beethoven 9", "Saenger Theatre")]
    run(conn, a, ok(mobilesymphony=1, **{"92zew": 1}))
    occ = conn.execute("SELECT id FROM occurrences").fetchone()["id"]

    # run 2: symphony (tier A) drops it, 92ZEW still lists it -> miss 1, still active
    run(conn, [a[1]], ok(mobilesymphony=5, **{"92zew": 1}))
    row = conn.execute("SELECT consecutive_misses FROM occurrence_sources WHERE source_id='mobilesymphony'").fetchone()
    assert row["consecutive_misses"] == 1
    assert conn.execute("SELECT status FROM occurrences WHERE id=?", (occ,)).fetchone()["status"] == "active"

    # run 3: symphony pull FAILED -> guard: no increment, no flag
    run(conn, [a[1]], {"mobilesymphony": {"status": "failed", "count": 0, "underdelivered": 0, "error": "boom"}, "92zew": {"status": "ok", "count": 1, "underdelivered": 0, "error": None}})
    assert conn.execute("SELECT consecutive_misses FROM occurrence_sources WHERE source_id='mobilesymphony'").fetchone()["consecutive_misses"] == 1

    # run 4: healthy pull, still missing -> second miss -> flagged (A gone stale, C hasn't)
    run(conn, [a[1]], ok(mobilesymphony=5, **{"92zew": 1}))
    assert conn.execute("SELECT status FROM occurrences WHERE id=?", (occ,)).fetchone()["status"] == "flagged_cancelled"
    assert any(r["cancellation_flagged"] for r in review.open_items(conn))


def test_lower_tier_dropping_does_not_flag(conn):
    a = [ev("mobilesymphony", "s1", "Beethoven 9", "Saenger Theatre"), ev("92zew", "z", "Beethoven 9", "Saenger Theatre")]
    run(conn, a, ok(mobilesymphony=1, **{"92zew": 1}))
    for _ in range(3):
        run(conn, [a[0]], ok(mobilesymphony=1, **{"92zew": 5}))
    assert conn.execute("SELECT status FROM occurrences").fetchone()["status"] == "active"


def test_unknown_venue_resolves_after_alias_added(conn, monkeypatch):
    from pipeline import config
    run(conn, [ev("mobilesymphony", "s1", "Show", "Brand New Hall")], ok(mobilesymphony=1))
    assert conn.execute("SELECT venue_id FROM occurrences").fetchone()["venue_id"] is None
    venues = [dict(v) for v in config.venues()]
    venues[0] = {**venues[0], "aliases": [*venues[0]["aliases"], "Brand New Hall"]}
    monkeypatch.setattr(config, "venues", lambda: venues)
    run(conn, [ev("mobilesymphony", "s1", "Show", "Brand New Hall")], ok(mobilesymphony=1))
    assert conn.execute("SELECT venue_id FROM occurrences").fetchone()["venue_id"] is not None
    assert not any(r["venue_unknown"] for r in review.open_items(conn))
