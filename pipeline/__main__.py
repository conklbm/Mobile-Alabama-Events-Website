"""CLI.  uv run python -m pipeline <command>

  run                 collect -> process -> publish -> write issue.md (the weekly job)
  collect [--only id] pull sources into raw_pulls
  process [--run N]   normalize/dedup/gate a run (default: latest)
  publish             render site/ from the store
  approve --strict | --all | --ids 1 2 3
  queue               print open review items
  issue [--out f]     print/write the review issue markdown for the latest run
  stats               counts
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import collect as collect_mod
from . import config, db, review
from .process import process as process_run
from .publish import export_json
from .publish.mobile import publish as publish_site


def _conn():
    conn = db.connect()
    with db.tx(conn):
        db.sync_sources(conn)
        db.sync_venues(conn)
    return conn


def cmd_collect(args) -> int:
    conn = _conn()
    run_id = db.start_run(conn)
    res = collect_mod.collect(conn, run_id, only=args.only)
    db.finish_run(conn, run_id, "collected")
    _print_results(res)
    print(f"run {run_id}")
    return 0


def cmd_process(args) -> int:
    conn = _conn()
    run_id = args.run or db.latest_run_id(conn)
    if not run_id:
        print("no runs yet; collect first", file=sys.stderr)
        return 2
    out = process_run(conn, run_id, collect_mod.source_results(conn, run_id))
    _print_process(out)
    return 0


def cmd_publish(args) -> int:
    conn = _conn()
    counts = publish_site(conn)
    counts["json"] = export_json.export(conn)
    print(counts)
    return 0


def cmd_run(args) -> int:
    conn = _conn()
    run_id = db.start_run(conn)
    try:
        res = collect_mod.collect(conn, run_id, only=args.only)
        _print_results(res)
        out = process_run(conn, run_id, res)
        _print_process(out)
        counts = publish_site(conn)
        counts["json"] = export_json.export(conn)
        print("published:", counts)
        title, body = review.issue_body(conn, run_id, out["alerts"], out["summary"])
        if args.issue_out:
            p = Path(args.issue_out)
            p.write_text((title + "\n" + body) if title else "", encoding="utf-8")
            print(f"issue -> {p} ({'empty' if not title else title})")
        elif title:
            print("\n" + title + "\n" + body)
        if args.alerts_out:
            # skipped-for-missing-key is a config choice, not breakage; everything else is
            real = [a for a in out["alerts"] if "skipped" not in a]
            Path(args.alerts_out).write_text("\n".join(real) + ("\n" if real else ""), encoding="utf-8")
            print(f"alerts -> {args.alerts_out} ({len(real)})")
        db.finish_run(conn, run_id, "ok")
    except Exception:
        db.finish_run(conn, run_id, "failed")
        raise
    return 0


def cmd_approve(args) -> int:
    conn = _conn()
    n = review.approve(conn, ids=args.ids, strict=args.strict, everything=args.all)
    print(f"approved {n}")
    if n:
        print("re-publish with: uv run python -m pipeline publish")
    return 0


def cmd_queue(args) -> int:
    conn = _conn()
    items = review.open_items(conn)
    if not items:
        print("queue empty")
        return 0
    for r in items:
        flags = [k for k in ("venue_unknown", "match_ambiguous", "cancellation_flagged", "source_underdelivered", "date_uncertain", "strict_mode") if r[k]]
        print(f"#{r['occurrence_id']:<6} {r['start_utc'][:10]}  {r['title_raw'][:50]:<50}  {(r['venue_name'] or r['venue_name_raw'] or '')[:30]:<30}  {','.join(flags)}")
    print(f"{len(items)} open")
    return 0


def cmd_issue(args) -> int:
    conn = _conn()
    run_id = db.latest_run_id(conn)
    from .freshness import breakage_alerts
    res = collect_mod.source_results(conn, run_id)
    if args.remaining:
        lines = [review._line(conn, r) for r in review.open_items(conn) if any(r[k] for k in review.BLOCKING) or r["strict_mode"]]
        text = "\n".join(lines) + ("\n" if lines else "")
    else:
        title, body = review.issue_body(conn, run_id, breakage_alerts(conn, run_id, res), {})
        text = (title + "\n" + body) if title else ""
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text or "(nothing to report)")
    return 0


def cmd_commands(args) -> int:
    """Apply review commands from an issue comment (file or stdin); write a markdown report."""
    from . import commands
    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    conn = _conn()
    res = commands.apply(text, conn)
    rep = commands.report(res)
    if args.report:
        Path(args.report).write_text(rep, encoding="utf-8")
    print(rep)
    return 0


def cmd_stats(args) -> int:
    conn = _conn()
    q = lambda sql: conn.execute(sql).fetchone()[0]
    print(f"runs: {q('SELECT COUNT(*) FROM runs')}   raw_pulls: {q('SELECT COUNT(*) FROM raw_pulls')}")
    print(f"series: {q('SELECT COUNT(*) FROM series')}   occurrences: {q('SELECT COUNT(*) FROM occurrences')}   "
          f"published upcoming: {q(chr(39).join(['SELECT COUNT(*) FROM occurrences WHERE publish_state=', 'published', ' AND end_utc >= datetime(', 'now', ')']))}")
    print(f"open review items: {q('SELECT COUNT(*) FROM review_queue WHERE resolved_at IS NULL')}")
    for r in conn.execute("SELECT id, tier, last_successful_pull, last_event_count FROM sources ORDER BY id"):
        print(f"  {r['id']:<22} tier {r['tier']}  last ok {str(r['last_successful_pull'] or '-')[:10]}  {r['last_event_count'] if r['last_event_count'] is not None else '-'} events")
    return 0


def _print_results(res: dict) -> None:
    for sid, r in res.items():
        flag = "  <-- UNDERDELIVERED" if r["underdelivered"] else ""
        err = f"  ({r['error']})" if r["error"] else ""
        print(f"  {sid:<22} {r['status']:<8} {r['count']:>4}{flag}{err}")


def _print_process(out: dict) -> None:
    print("process:", out["stats"])
    print("gates:", out["summary"], "(strict mode)" if out.get("strict") else "")
    for a in out["alerts"]:
        print("ALERT:", a)


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    p = argparse.ArgumentParser(prog="pipeline", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run"); s.add_argument("--only", nargs="*"); s.add_argument("--issue-out"); s.add_argument("--alerts-out"); s.set_defaults(fn=cmd_run)
    s = sub.add_parser("collect"); s.add_argument("--only", nargs="*"); s.set_defaults(fn=cmd_collect)
    s = sub.add_parser("process"); s.add_argument("--run", type=int); s.set_defaults(fn=cmd_process)
    s = sub.add_parser("publish"); s.set_defaults(fn=cmd_publish)
    s = sub.add_parser("approve"); s.add_argument("--ids", nargs="*", type=int); s.add_argument("--strict", action="store_true"); s.add_argument("--all", action="store_true"); s.set_defaults(fn=cmd_approve)
    s = sub.add_parser("queue"); s.set_defaults(fn=cmd_queue)
    s = sub.add_parser("issue"); s.add_argument("--out"); s.add_argument("--remaining", action="store_true"); s.set_defaults(fn=cmd_issue)
    s = sub.add_parser("commands"); s.add_argument("--file"); s.add_argument("--report"); s.set_defaults(fn=cmd_commands)
    s = sub.add_parser("stats"); s.set_defaults(fn=cmd_stats)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
