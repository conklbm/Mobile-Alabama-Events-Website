from pipeline.matcher import Matcher, MatchSchema
from pipeline.text import title_key

schema = MatchSchema(
    text_of=lambda r: r["t"],
    bucket_of=lambda r: (r["day"], r["venue"]),
    rank_of=lambda r: (r["rank"],),
    field_rules={"desc": "longest", "tags": "union", "n": "max", "img": "first_nonempty"},
)
m = Matcher(schema)


def rec(t, day="d1", venue="v1", rank=0, **kw):
    return {"t": title_key(t), "day": day, "venue": venue, "rank": rank, **kw}


def test_same_event_different_spelling_matches():
    r = m.best(rec("Beer, BBQ & Bingo"), [rec("Beer BBQ and Bingo w/ 92ZEW")])
    assert r.decision == "match" and r.score >= 82


def test_different_bucket_never_matches():
    r = m.best(rec("Beer, BBQ & Bingo"), [rec("Beer, BBQ & Bingo", day="d2")])
    assert r.decision == "new"


def test_unrelated_titles_are_new():
    r = m.best(rec("Mobile Symphony: Beethoven 9"), [rec("Trivia Night")])
    assert r.decision == "new"


def test_gray_band_is_ambiguous():
    s = MatchSchema(text_of=lambda r: r["t"], match_threshold=95, ambiguous_floor=50)
    r = Matcher(s).best({"t": "jazz night at the wharf"}, [{"t": "jazz brunch at the wharf"}])
    assert r.decision == "ambiguous" and r.candidate is not None


def test_veto_blocks_match():
    s = MatchSchema(text_of=lambda r: r["t"], veto=lambda a, b: a.get("id") == 1 and b.get("id") == 2)
    r = Matcher(s).best({"t": "same title", "id": 1}, [{"t": "same title", "id": 2}])
    assert r.decision == "new"


def test_merge_source_priority_and_rules():
    a = rec("x", rank=2, desc="short", price="", tags=["a"], n=1, img="")
    b = rec("x", rank=0, desc="a much longer description", price="$10", tags=["b", "a"], n=5, img="")
    c = rec("x", rank=1, desc="", price="$12", tags=[], n=None, img="pic.jpg")
    out = m.merge([a, b, c])
    assert out["desc"] == "a much longer description"
    assert out["price"] == "$10"          # best rank wins first_nonempty
    assert out["tags"] == ["b", "a"]
    assert out["n"] == 5
    assert out["img"] == "pic.jpg"        # first non-empty by rank


def test_cluster_dedups_within_bucket_only():
    groups = m.cluster([rec("Trivia Night"), rec("Trivia Night!"), rec("Trivia Night", day="d2"), rec("Jazz Brunch")])
    sizes = sorted(len(g) for g in groups)
    assert sizes == [1, 1, 2]


def test_winner_is_best_rank():
    assert m.winner([rec("x", rank=3, id=1), rec("x", rank=1, id=2)])["id"] == 2
