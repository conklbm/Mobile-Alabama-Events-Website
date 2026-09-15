"""SQLite store: the single source of truth. Publishers are read-only consumers."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  collector_type TEXT NOT NULL,
  tier TEXT NOT NULL,
  curated INTEGER NOT NULL DEFAULT 0,
  regions TEXT NOT NULL,            -- JSON list
  brand_tokens TEXT NOT NULL,       -- JSON list
  license_notes TEXT NOT NULL,
  redistributable INTEGER NOT NULL,
  expected_min_events INTEGER NOT NULL DEFAULT 0,
  config TEXT NOT NULL DEFAULT '{}',
  last_successful_pull TEXT,
  last_event_count INTEGER
);

CREATE TABLE IF NOT EXISTS venues (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  canonical_name TEXT NOT NULL,
  address TEXT, city TEXT, state TEXT, zip TEXT,
  lat REAL, lng REAL,
  regions TEXT NOT NULL,            -- JSON list
  domains TEXT NOT NULL DEFAULT '[]',
  notes TEXT
);

CREATE TABLE IF NOT EXISTS series (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  canonical_title TEXT NOT NULL,
  title_key TEXT NOT NULL,
  venue_id INTEGER REFERENCES venues(id),
  venue_name_raw TEXT,
  venue_key TEXT,
  description TEXT,
  cadence TEXT NOT NULL DEFAULT 'one_off',
  category TEXT NOT NULL DEFAULT 'community',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_series_venue ON series(venue_id);
CREATE INDEX IF NOT EXISTS idx_series_vkey ON series(venue_key);

CREATE TABLE IF NOT EXISTS occurrences (
  id INTEGER PRIMARY KEY,
  series_id INTEGER NOT NULL REFERENCES series(id),
  title_raw TEXT NOT NULL,
  title_key TEXT NOT NULL,
  start_utc TEXT NOT NULL,
  end_utc TEXT NOT NULL,
  timezone TEXT NOT NULL,
  local_day TEXT NOT NULL,          -- YYYY-MM-DD in event tz; the dedup bucket key
  all_day INTEGER NOT NULL DEFAULT 0,
  time_tba INTEGER NOT NULL DEFAULT 0,
  date_confident INTEGER NOT NULL DEFAULT 1,
  venue_id INTEGER REFERENCES venues(id),
  venue_name_raw TEXT,
  venue_key TEXT,                   -- normalized raw venue name; bucket key when venue unresolved
  city TEXT,
  regions TEXT NOT NULL DEFAULT '[]',   -- JSON list, from venue or source
  description TEXT,
  price TEXT,
  ticket_url TEXT,
  info_url TEXT,
  category TEXT NOT NULL DEFAULT 'community',
  categories TEXT NOT NULL DEFAULT '[]',      -- JSON list, primary first, max 2
  status TEXT NOT NULL DEFAULT 'active',        -- active | flagged_cancelled | canceled
  independent_source_count INTEGER NOT NULL DEFAULT 0,
  curation_score INTEGER NOT NULL DEFAULT 0,
  image_url TEXT, image_source_url TEXT, image_credit TEXT,
  image_ok INTEGER NOT NULL DEFAULT 0,
  match_ambiguous INTEGER NOT NULL DEFAULT 0,
  match_candidate_id INTEGER,
  publish_state TEXT NOT NULL DEFAULT 'held',   -- held | published
  approved INTEGER NOT NULL DEFAULT 0,          -- human said yes once; sticks
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_occ_day ON occurrences(local_day);
CREATE INDEX IF NOT EXISTS idx_occ_series ON occurrences(series_id);
CREATE INDEX IF NOT EXISTS idx_occ_start ON occurrences(start_utc);

CREATE TABLE IF NOT EXISTS occurrence_sources (
  id INTEGER PRIMARY KEY,
  occurrence_id INTEGER NOT NULL REFERENCES occurrences(id),
  source_id TEXT NOT NULL REFERENCES sources(id),
  external_id TEXT NOT NULL,
  source_url TEXT,
  origin_url TEXT,                  -- one-hop outbound link, if it resolved to a venue domain
  origin_tier TEXT,                 -- tier of the origin (A when origin_url hits a venue domain)
  image_url TEXT,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  consecutive_misses INTEGER NOT NULL DEFAULT 0,
  self_promoted INTEGER NOT NULL DEFAULT 0,
  raw_pull_id INTEGER,
  UNIQUE(source_id, external_id)
);
CREATE INDEX IF NOT EXISTS idx_os_occ ON occurrence_sources(occurrence_id);

CREATE TABLE IF NOT EXISTS raw_pulls (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  source_id TEXT NOT NULL,
  external_id TEXT NOT NULL,
  pulled_at TEXT NOT NULL,
  payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_raw_run ON raw_pulls(run_id);

CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL DEFAULT 'running',
  notes TEXT
);

CREATE TABLE IF NOT EXISTS source_runs (
  run_id INTEGER NOT NULL,
  source_id TEXT NOT NULL,
  status TEXT NOT NULL,             -- ok | failed | skipped
  event_count INTEGER NOT NULL DEFAULT 0,
  underdelivered INTEGER NOT NULL DEFAULT 0,
  error TEXT,
  PRIMARY KEY (run_id, source_id)
);

CREATE TABLE IF NOT EXISTS review_queue (
  id INTEGER PRIMARY KEY,
  occurrence_id INTEGER NOT NULL REFERENCES occurrences(id),
  run_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  resolved_at TEXT,
  -- named booleans, never a blended score
  venue_unknown INTEGER NOT NULL DEFAULT 0,
  match_ambiguous INTEGER NOT NULL DEFAULT 0,
  cancellation_flagged INTEGER NOT NULL DEFAULT 0,
  source_underdelivered INTEGER NOT NULL DEFAULT 0,
  date_uncertain INTEGER NOT NULL DEFAULT 0,
  tier_c_only INTEGER NOT NULL DEFAULT 0,
  strict_mode INTEGER NOT NULL DEFAULT 0,
  details TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_rq_open ON review_queue(resolved_at);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = DELETE")  # single committed .db file, no -wal sidecar
    conn.executescript(SCHEMA)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Additive column migrations for stores created by older schema versions."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(occurrences)")}
    if "time_tba" not in cols:
        conn.execute("ALTER TABLE occurrences ADD COLUMN time_tba INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    if "categories" not in cols:
        conn.execute("ALTER TABLE occurrences ADD COLUMN categories TEXT NOT NULL DEFAULT '[]'")
        conn.execute("UPDATE occurrences SET categories = '[\"' || category || '\"]'")
        conn.commit()


@contextmanager
def tx(conn: sqlite3.Connection):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def j(v) -> str:
    return json.dumps(v, ensure_ascii=False)


def uj(s: str | None, default=None):
    if not s:
        return default if default is not None else []
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return default if default is not None else []


# ---------- config sync ----------

def sync_sources(conn: sqlite3.Connection) -> None:
    """YAML wins for config fields; runtime fields (last_successful_pull) are preserved."""
    for s in config.sources():
        conn.execute(
            """INSERT INTO sources (id,name,url,collector_type,tier,curated,regions,brand_tokens,license_notes,
                 redistributable,expected_min_events,config)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET name=excluded.name,url=excluded.url,collector_type=excluded.collector_type,
                 tier=excluded.tier,curated=excluded.curated,regions=excluded.regions,brand_tokens=excluded.brand_tokens,
                 license_notes=excluded.license_notes,redistributable=excluded.redistributable,
                 expected_min_events=excluded.expected_min_events,config=excluded.config""",
            (s["id"], s["name"], s["url"], s["collector_type"], s["tier"], int(bool(s["curated"])),
             j(s["regions"]), j(s["brand_tokens"]), s["license_notes"], int(bool(s["redistributable"])),
             int(s["expected_min_events"]), j(s["config"])),
        )


def sync_venues(conn: sqlite3.Connection) -> None:
    for v in config.venues():
        conn.execute(
            """INSERT INTO venues (slug,canonical_name,address,city,state,zip,lat,lng,regions,domains,notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(slug) DO UPDATE SET canonical_name=excluded.canonical_name,address=excluded.address,
                 city=excluded.city,state=excluded.state,zip=excluded.zip,lat=excluded.lat,lng=excluded.lng,
                 regions=excluded.regions,domains=excluded.domains,notes=excluded.notes""",
            (v["slug"], v["name"], v.get("address"), v.get("city"), v.get("state"), str(v.get("zip") or "") or None,
             v.get("lat"), v.get("lng"), j(v["regions"]), j(v["domains"]), v.get("notes")),
        )


def source_row(conn: sqlite3.Connection, source_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()


def venue_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM venues WHERE slug=?", (slug,)).fetchone()


# ---------- runs ----------

def start_run(conn: sqlite3.Connection) -> int:
    cur = conn.execute("INSERT INTO runs (started_at) VALUES (?)", (now_iso(),))
    conn.commit()
    return cur.lastrowid


def finish_run(conn: sqlite3.Connection, run_id: int, status: str = "ok", notes: str = "") -> None:
    conn.execute("UPDATE runs SET finished_at=?, status=?, notes=? WHERE id=?", (now_iso(), status, notes, run_id))
    conn.commit()


def run_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]


def latest_run_id(conn: sqlite3.Connection) -> int | None:
    r = conn.execute("SELECT MAX(id) FROM runs").fetchone()
    return r[0]
