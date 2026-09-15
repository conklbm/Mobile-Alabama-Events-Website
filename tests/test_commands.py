"""Review commands: parsing email-style replies and applying them to the YAML files + store."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from pipeline import commands, db
from pipeline.collect import _serialize
from pipeline.models import RawEvent
from pipeline.process import process

CT = ZoneInfo("America/Chicago")
SOON = datetime.now(CT).replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(days=10)

OVERRIDES = '''# comment stays
merge: []
#  - [1234, 5678]
never_merge:
  - [1, 2]   # existing pair
cancelled: []
not_cancelled: []
force_publish: []
'''
VENUES = '''# alias map
- slug: soul-kitchen
  name: Soul Kitchen Music Hall
  aliases: ["Soul Kitchen", "Soul Kitchen Music Hall"]
  domains: ["soulkitchenmobile.com"]
  city: Mobile
  state: AL
  regions: [mobile]

- slug: saenger-theatre
  name: Saenger Theatre
  aliases: ["Saenger Theatre"]
  domains: []
  city: Mobile
  state: AL
  regions: [mobile]
'''


@pytest.fixture
def env(tmp_path):
    (tmp_path / "overrides.yaml").write_text(OVERRIDES, encoding="utf-8")
    (tmp_path / "venues.yaml").write_text(VENUES, encoding="utf-8")
    conn = db.connect(tmp_path / "t.db")
    with db.tx(conn):
        db.sync_sources(conn)
        db.sync_venues(conn)
    rid = db.start_run(conn)
    evs = [RawEvent("mobilesymphony", f"e{i}", f"Show {i}", SOON, venue_name="Nowhere Bar", info_url="https://x/e") for i in range(1, 4)]
    with db.tx(conn):
        for e in evs:
            conn.execute("INSERT INTO raw_pulls (run_id, source_id, external_id, pulled_at, payload) VALUES (?,?,?,?,?)",
                         (rid, e.source_id, e.external_id, db.now_iso(), _serialize(e)))
    process(conn, rid, {"mobilesymphony": {"status": "ok", "count": 3, "underdelivered": 0, "error": None}})
    return conn, tmp_path


def test_parse_ignores_quoted_reply_and_signature():
    text = '''approve 1, #2
cancel 3
alias "Nowhere Bar" = soul-kitchen
venue new-place "New Place" "Spanish Fort"
never-merge 4 5
what is this
On Thu, Sep 18 2026, github-actions[bot] wrote:
> approve 999
'''
    cmds, unknown = commands.parse(text)
    assert [c.verb for c in cmds] == ["approve", "cancel", "alias", "venue", "never-merge"]
    assert cmds[0].ids == [1, 2] and cmds[2].slug == "soul-kitchen" and cmds[3].city == "Spanish Fort"
    assert unknown == ["what is this"]


def test_apply_edits_yaml_as_text_and_keeps_comments(env):
    conn, d = env
    ids = [r[0] for r in conn.execute("SELECT id FROM occurrences ORDER BY id")]
    text = f'''cancel {ids[0]}
not-cancelled {ids[1]}
merge {ids[1]} {ids[2]}
never-merge {ids[0]} {ids[2]}
alias "Nowhere Bar" = soul-kitchen
alias "Nowhere Bar" = soul-kitchen
venue nowhere-bar "Nowhere Bar Annex" Daphne
alias "x" = does-not-exist
approve {ids[2]} 99999
'''
    res = commands.apply(text, conn, d)
    ov = (d / "overrides.yaml").read_text(encoding="utf-8")
    ve = (d / "venues.yaml").read_text(encoding="utf-8")
    assert "# comment stays" in ov and "# existing pair" in ov
    assert f"cancelled: [{ids[0]}]" in ov and f"not_cancelled: [{ids[1]}]" in ov
    assert f"merge: [[{ids[1]}, {ids[2]}]]" in ov
    assert f"  - [1, 2]   # existing pair\n  - [{ids[0]}, {ids[2]}]" in ov
    assert 'aliases: ["Soul Kitchen", "Soul Kitchen Music Hall", "Nowhere Bar"]' in ve
    assert ve.count("Nowhere Bar") == 3  # alias once (dedup), new venue name + its own alias
    assert "- slug: nowhere-bar\n  name: Nowhere Bar Annex" in ve and "city: Daphne" in ve
    assert any("does-not-exist" in e for e in res.errors)
    assert any("99999" in e for e in res.errors)
    assert len(res.ok) == 7
    rep = commands.report(res)
    assert rep.startswith("<!-- bot -->") and "Applied:" in rep and "Couldn't apply:" in rep


def test_approve_and_ignore_change_store(env):
    conn, d = env
    ids = [r[0] for r in conn.execute("SELECT id FROM occurrences ORDER BY id")]
    assert conn.execute("SELECT COUNT(*) FROM review_queue WHERE resolved_at IS NULL").fetchone()[0] == 3
    res = commands.apply(f"approve {ids[0]}\nignore {ids[1]}", conn, d)
    assert res.ok and not res.errors
    assert conn.execute("SELECT publish_state FROM occurrences WHERE id=?", (ids[0],)).fetchone()[0] == "published"
    assert conn.execute("SELECT COUNT(*) FROM review_queue WHERE resolved_at IS NULL").fetchone()[0] == 1


def test_empty_comment_reports_usage():
    assert "No commands found" in commands.report(commands.Result())
