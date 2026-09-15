"""Confidence gates + review queue. Named booleans, never a blended score.

Auto-publish when no blocking gate fires. Queue when any does:
  venue_unknown, match_ambiguous, cancellation_flagged, source_underdelivered, date_uncertain
tier_c_only is recorded but only blocks when settings.review.gate_on_tier_c_only is true
(92ZEW alone would otherwise queue hundreds of real events).

Strict mode (first N runs): everything new is held and listed, so the first bad parse
is seen in an issue, not on the site. `approve --strict` releases the batch.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict

from . import config, db
from .dates import from_utc
from .scoring import TIER_RANK

BLOCKING = ("venue_unknown", "match_ambiguous", "cancellation_flagged", "source_underdelivered", "date_uncertain")


def evaluate(conn: sqlite3.Connection, run_id: int, source_results: dict[str, dict], strict: bool, created_this_run: set[int]) -> dict:
    ov = config.overrides()
    gate_c = bool(config.settings().get("review", {}).get("gate_on_tier_c_only", False))
    under = {sid for sid, r in source_results.items() if r.get("underdelivered")}
    forced = {int(x) for x in ov.get("force_publish", [])}
    now = db.now_iso()
    counts = defaultdict(int)
    occs = conn.execute(
        "SELECT * FROM occurrences WHERE start_utc >= datetime('now','-1 day') ORDER BY start_utc"
    ).fetchall()
    for occ in occs:
        srcs = conn.execute(
            "SELECT os.source_id, os.origin_tier, s.tier FROM occurrence_sources os JOIN sources s ON s.id=os.source_id WHERE os.occurrence_id=?",
            (occ["id"],),
        ).fetchall()
        flags = {
            "venue_unknown": occ["venue_id"] is None,
            "match_ambiguous": bool(occ["match_ambiguous"]),
            "cancellation_flagged": occ["status"] == "flagged_cancelled",
            "source_underdelivered": bool(srcs) and all(s["source_id"] in under for s in srcs),
            "date_uncertain": not occ["date_confident"],
            "tier_c_only": not any((s["origin_tier"] == "A") or s["tier"] in ("A", "B") for s in srcs),
        }
        blocking = any(flags[k] for k in BLOCKING) or (gate_c and flags["tier_c_only"])
        strict_hold = False
        if occ["status"] == "cancelled":
            state = "held"
        elif occ["id"] in forced or occ["approved"]:
            state = "published"
        elif blocking:
            state = "held"
        elif strict:
            state, strict_hold = "held", True
        else:
            state = "published"
        if state != occ["publish_state"]:
            conn.execute("UPDATE occurrences SET publish_state=?, updated_at=? WHERE id=?", (state, now, occ["id"]))
        counts[state] += 1

        needs_queue = (blocking and occ["status"] != "cancelled") or strict_hold
        open_row = conn.execute(
            "SELECT id FROM review_queue WHERE occurrence_id=? AND resolved_at IS NULL", (occ["id"],)
        ).fetchone()
        if needs_queue:
            details = {"candidate_id": occ["match_candidate_id"], "venue_name_raw": occ["venue_name_raw"]}
            vals = (
                int(flags["venue_unknown"]), int(flags["match_ambiguous"]), int(flags["cancellation_flagged"]),
                int(flags["source_underdelivered"]), int(flags["date_uncertain"]), int(flags["tier_c_only"]),
                int(strict_hold), json.dumps(details),
            )
            if open_row:
                conn.execute(
                    """UPDATE review_queue SET venue_unknown=?, match_ambiguous=?, cancellation_flagged=?,
                       source_underdelivered=?, date_uncertain=?, tier_c_only=?, strict_mode=?, details=? WHERE id=?""",
                    vals + (open_row["id"],),
                )
            else:
                conn.execute(
                    """INSERT INTO review_queue (occurrence_id, run_id, created_at, venue_unknown, match_ambiguous,
                       cancellation_flagged, source_underdelivered, date_uncertain, tier_c_only, strict_mode, details)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (occ["id"], run_id, now) + vals,
                )
            counts["queued"] += 1
        elif open_row:
            conn.execute("UPDATE review_queue SET resolved_at=? WHERE id=?", (now, open_row["id"]))
            counts["auto_resolved"] += 1
    return dict(counts)


def approve(conn: sqlite3.Connection, ids: list[int] | None = None, strict: bool = False, everything: bool = False) -> int:
    """Human said yes. Sticks across runs."""
    now = db.now_iso()
    if everything:
        rows = conn.execute("SELECT occurrence_id FROM review_queue WHERE resolved_at IS NULL").fetchall()
    elif strict:
        rows = conn.execute(
            """SELECT occurrence_id FROM review_queue WHERE resolved_at IS NULL AND strict_mode=1
               AND venue_unknown=0 AND match_ambiguous=0 AND cancellation_flagged=0 AND source_underdelivered=0 AND date_uncertain=0"""
        ).fetchall()
    else:
        rows = [{"occurrence_id": int(i)} for i in (ids or [])]
    n = 0
    for r in rows:
        oid = r["occurrence_id"]
        conn.execute("UPDATE occurrences SET approved=1, publish_state='published', match_ambiguous=0, updated_at=? WHERE id=? AND status!='cancelled'", (now, oid))
        conn.execute("UPDATE review_queue SET resolved_at=? WHERE occurrence_id=? AND resolved_at IS NULL", (now, oid))
        n += 1
    conn.commit()
    return n


def open_items(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT q.*, o.title_raw, o.start_utc, o.timezone, o.venue_name_raw, o.venue_id, o.city, o.status, o.match_candidate_id,
                  v.canonical_name AS venue_name
           FROM review_queue q JOIN occurrences o ON o.id=q.occurrence_id
           LEFT JOIN venues v ON v.id=o.venue_id
           WHERE q.resolved_at IS NULL ORDER BY o.start_utc"""
    ).fetchall()


def _line(conn: sqlite3.Connection, r: sqlite3.Row) -> str:
    when = from_utc(r["start_utc"], r["timezone"])
    src = conn.execute(
        "SELECT source_url, source_id FROM occurrence_sources WHERE occurrence_id=? ORDER BY id LIMIT 1", (r["occurrence_id"],)
    ).fetchone()
    link = f" — [{src['source_id']}]({src['source_url']})" if src and src["source_url"] else ""
    venue = r["venue_name"] or r["venue_name_raw"] or "(no venue)"
    return f"- `#{r['occurrence_id']}` **{r['title_raw']}** — {when:%a %b %d, %I:%M %p} — {venue}{link}"


def issue_body(conn: sqlite3.Connection, run_id: int, alerts: list[str], summary: dict) -> tuple[str, str]:
    """(title, markdown body) for the GitHub issue. Empty title = nothing to report."""
    items = open_items(conn)
    real = [r for r in items if any(r[k] for k in BLOCKING)]
    strict_only = [r for r in items if not any(r[k] for k in BLOCKING) and r["strict_mode"]]
    n = len(real) + len(strict_only) + len(alerts)
    if n == 0:
        return "", ""
    out = [f"Run #{run_id}. Published: {summary.get('published', 0)}, held: {summary.get('held', 0)}, auto-resolved: {summary.get('auto_resolved', 0)}.", ""]
    if alerts:
        out += ["## Source alerts (silent-breakage check)", *[f"- {a}" for a in alerts], ""]

    cancel = [r for r in real if r["cancellation_flagged"]]
    if cancel:
        out += ["## Possibly cancelled", "Primary source stopped listing these two runs in a row. Confirm in `overrides.yaml` (`cancelled:` / `not_cancelled:`).", *[_line(conn, r) for r in cancel], ""]

    unknown = [r for r in real if r["venue_unknown"]]
    if unknown:
        out += ["## Unknown venues", "Add an alias in `data/venues.yaml`; next run resolves and publishes automatically.", ""]
        by_name: dict[str, list] = defaultdict(list)
        for r in unknown:
            by_name[r["venue_name_raw"] or json.loads(r["details"]).get("venue_name_raw") or "(blank)"].append(r)
        for name, rows in sorted(by_name.items(), key=lambda kv: -len(kv[1])):
            out.append(f"### `{name}` ({len(rows)})")
            out += [_line(conn, r) for r in rows[:5]]
            if len(rows) > 5:
                out.append(f"- …and {len(rows) - 5} more")
        out.append("")

    amb = [r for r in real if r["match_ambiguous"]]
    if amb:
        out += ["## Ambiguous matches", "Fuzzy score in the gray band. Merge via `overrides.yaml` (`merge: [[a, b]]`) or approve as separate.", ""]
        for r in amb:
            cand = conn.execute("SELECT id, title_raw FROM occurrences WHERE id=?", (r["match_candidate_id"],)).fetchone()
            out.append(_line(conn, r) + (f"  ↔ candidate `#{cand['id']}` **{cand['title_raw']}**" if cand else ""))
        out.append("")

    dates = [r for r in real if r["date_uncertain"]]
    if dates:
        out += ["## Uncertain dates", *[_line(conn, r) for r in dates], ""]

    under = [r for r in real if r["source_underdelivered"] and not (r["venue_unknown"] or r["match_ambiguous"] or r["cancellation_flagged"])]
    if under:
        out += ["## Only source underdelivered this run", *[_line(conn, r) for r in under[:20]], ""]

    if strict_only:
        out += [f"## Strict-mode holds ({len(strict_only)})",
                "No gate fired; held because this is one of the first runs. Skim, then release all with:",
                "```bash", "uv run python -m pipeline approve --strict", "```",
                *[_line(conn, r) for r in strict_only[:60]]]
        if len(strict_only) > 60:
            out.append(f"- …and {len(strict_only) - 60} more")
        out.append("")
    title = f"{len(real) + len(strict_only)} items need review" if (real or strict_only) else "Source alerts"
    return title, "\n".join(out)
