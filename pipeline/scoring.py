"""Two fields, not one.

independent_source_count — distinct parties that listed it, self-promo excluded. "Is this real?"
curation_score           — human-curated sources that picked it up, self-promo excluded. "Worth featuring?"

Self-promoted events still appear normally; they just don't vote for themselves.
"""

from __future__ import annotations

import re
import sqlite3

from . import db

TIER_RANK = {"A": 0, "B": 1, "C": 2}


def is_self_promoted(brand_tokens: list[str], *texts: str) -> bool:
    """True when the source's own brand appears in the organizer, venue, or title."""
    blob = " ".join(t for t in texts if t).lower()
    if not blob:
        return False
    for tok in brand_tokens or []:
        t = str(tok).strip().lower()
        if not t:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", blob):
            return True
    return False


def rescore(conn: sqlite3.Connection, occurrence_ids: list[int] | None = None) -> None:
    """Recompute self_promoted per source row and the two scores per occurrence."""
    sources = {r["id"]: r for r in conn.execute("SELECT * FROM sources")}
    if occurrence_ids is None:
        ids = [r[0] for r in conn.execute("SELECT id FROM occurrences WHERE start_utc >= datetime('now','-1 day')")]
    else:
        ids = occurrence_ids
    for oid in ids:
        occ = conn.execute("SELECT title_raw, venue_name_raw FROM occurrences WHERE id=?", (oid,)).fetchone()
        if not occ:
            continue
        rows = conn.execute("SELECT * FROM occurrence_sources WHERE occurrence_id=?", (oid,)).fetchall()
        parties: set[str] = set()
        curated_parties: set[str] = set()
        for r in rows:
            src = sources.get(r["source_id"])
            tokens = db.uj(src["brand_tokens"]) if src else []
            raw = conn.execute("SELECT payload FROM raw_pulls WHERE id=?", (r["raw_pull_id"],)).fetchone() if r["raw_pull_id"] else None
            organizer = ""
            if raw:
                import json
                try:
                    organizer = json.loads(raw["payload"]).get("organizer", "") or ""
                except Exception:
                    organizer = ""
            sp = is_self_promoted(tokens, occ["title_raw"], occ["venue_name_raw"], organizer)
            conn.execute("UPDATE occurrence_sources SET self_promoted=? WHERE id=?", (int(sp), r["id"]))
            if sp:
                continue
            parties.add(r["source_id"])
            if src and src["curated"]:
                curated_parties.add(r["source_id"])
        conn.execute(
            "UPDATE occurrences SET independent_source_count=?, curation_score=? WHERE id=?",
            (len(parties), len(curated_parties), oid),
        )


def source_rank(src_row) -> tuple:
    """Lower wins. Tier first, then curated, then name for determinism."""
    return (TIER_RANK.get(src_row["tier"], 9), 0 if src_row["curated"] else 1, src_row["id"])


def primary_source(conn: sqlite3.Connection, occurrence_id: int):
    """Computed at render time from tier ranking — never stored as a fixed fact.
    A source row whose origin resolved to a venue domain counts as Tier A."""
    rows = conn.execute(
        """SELECT os.*, s.tier, s.curated, s.name AS source_name, s.collector_type
           FROM occurrence_sources os JOIN sources s ON s.id = os.source_id
           WHERE os.occurrence_id=?""",
        (occurrence_id,),
    ).fetchall()
    if not rows:
        return None

    def rank(r):
        tier = "A" if r["origin_tier"] == "A" else r["tier"]
        return (TIER_RANK.get(tier, 9), 0 if r["curated"] else 1, r["source_id"])

    return min(rows, key=rank)
