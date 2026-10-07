from datetime import date

from pipeline.collectors.govcal import GovCalCollector
from pipeline.collectors.zew_rundown import ZewRundownCollector
from pipeline.text import tame_caps

# ---------- City of Mobile / Mobile County JSON ----------

GOV_SRC = {"id": "mobile-county", "url": "https://example.gov/community_events/",
           "config": {"site": "https://example.gov/community_events/", "detail_base": "https://example.gov/community_events/events/"}}


def _gov(**kw):
    e = {"title": "SAMPLE 5K AND FESTIVAL", "start_date": "2026-10-10", "end_date": "2026-10-10", "start_time": "8:00 AM",
         "end_time": "None", "venue_name": "Sample Park", "event_address": "1 Main St.", "event_city": "Mobile",
         "slug": "sample-5k-2026-10-10", "cancelled": "0", "postponed": "0", "recurring_type": "Day", "content": "<p>Run.</p>",
         "event_website": "None", "category": "Health/Wellness,General"}
    e.update(kw)
    return e


def test_govcal_basic_fields_and_detail_url():
    (ev,) = GovCalCollector(GOV_SRC, session=None).parse({"data": [_gov()]}, date(2026, 10, 1), date(2026, 12, 31))
    assert ev.title == "Sample 5K and Festival"
    assert ev.start_local.hour == 8 and ev.end_local is None and not ev.all_day
    assert ev.venue_name == "Sample Park" and ev.venue_address == "1 Main St., Mobile"
    assert ev.info_url == "https://example.gov/community_events/events/sample-5k-2026-10-10"
    assert ev.categories == ["Health/Wellness", "General"] and ev.website == ""


def test_govcal_skips_long_runs_and_postponed_but_expands_weekly_markets():
    data = {"data": [
        _gov(slug="haunt", start_date="2026-09-19", end_date="2026-11-01"),                      # month-long run
        _gov(slug="later", postponed="1"),
        _gov(slug="market", start_date="2026-10-10", end_date="2026-10-24", recurring_type="Week",
             start_time="7:30 AM", end_time="12:00 PM"),
        _gov(slug="gone", cancelled="1", start_date="2026-10-12", end_date="2026-10-12"),
    ]}
    evs = GovCalCollector(GOV_SRC, session=None).parse(data, date(2026, 10, 1), date(2026, 12, 31))
    market = [e for e in evs if e.external_id.startswith("market:")]
    assert [e.start_local.day for e in market] == [10, 17, 24]
    assert all(e.end_local.hour == 12 and e.end_local.day == e.start_local.day for e in market)
    assert not any(e.external_id.startswith(("haunt:", "later:")) for e in evs)
    assert [e.cancelled for e in evs if e.external_id.startswith("gone:")] == [True]


# ---------- 92ZEW Weekend Rundown ----------

RUNDOWN_SRC = {"id": "92zew-rundown", "url": "https://example.net", "config": {
    "local_places": ["mobile", "fairhope", "daphne", "mt. vernon", "usa campus"],
    "away_places": ["biloxi", ", ms", "starkville"]}}

# Synthetic post in the Rundown's format (posted Wednesday, Sept 30, 2026)
POST = """
<p><strong>FRIDAY:</strong></p>
<p><strong>FAIRHOPE FIRST FRIDAY ARTWALK-</strong> Friday, 6pm-8pm, Downtown Fairhope</p>
<p><strong>BIG COUNTRY STAR-</strong> Friday, 7pm, Some Amphitheater, Gautier, MS. A concert.</p>
<p><strong>SATURDAY:</strong></p>
<p><strong>ALABAMA @ MISSISSIPPI STATE-</strong> Saturday, 11am, Starkville, ABC.</p>
<p><strong>SOUTH ALABAMA JAGUARS vs. ULM-</strong> Saturday, 6pm, Hancock Whitney Stadium, USA Campus. Kickoff.</p>
<p><strong>RAINED OUT 5K-</strong> <strong>**** RESCHEDULED FOR OCT 31 DUE TO WX ****</strong>Saturday, 8am, Airport, Mobile.</p>
<p><strong>POW WOW-</strong> Friday and Saturday, 9am-2pm, Pow Wow Grounds, Mt. Vernon.The tribe hosts. <a href="https://example.org/powwow">INFO HERE</a></p>
<p><strong>DUELING PIANOS-</strong> Friday, 8:30PM. Electric Piano Parlor, Mobile</p>
<p><strong>BINGO NIGHT-</strong> Thurs 7-8:30pm</p>
<p><strong>BURGER WEEK-</strong> October 2-11, various locations throughout Mobile</p>
<p><strong>GALLERY SHOW-</strong> Tues-Sat 10am, Museum of Art, Mobile</p>
<p><strong>SATURDAY:</strong></p>
<p><strong>DUELING PIANOS-</strong> Friday, 8:30PM. Electric Piano Parlor, Mobile</p>
"""


def _rundown():
    c = ZewRundownCollector(RUNDOWN_SRC, session=None)
    return c.parse_post(POST, date(2026, 9, 30), "https://example.net/weekend-rundown/", date(2026, 9, 1), date(2026, 12, 31))


def test_rundown_keeps_local_items_with_a_day_and_time():
    by = {}
    for e in _rundown():
        by.setdefault(e.title, []).append(e)
    assert set(by) == {"Fairhope First Friday Artwalk", "South Alabama Jaguars vs. ULM", "Pow Wow", "Dueling Pianos"}
    art = by["Fairhope First Friday Artwalk"][0]
    assert (art.start_local.date(), art.start_local.hour, art.end_local.hour) == (date(2026, 10, 2), 18, 20)
    assert art.venue_name == "Downtown Fairhope"
    assert [e.start_local.date() for e in by["Pow Wow"]] == [date(2026, 10, 2), date(2026, 10, 3)]
    assert by["Pow Wow"][0].info_url == "https://example.org/powwow" and by["Pow Wow"][0].city == "Mt. Vernon"
    assert by["Dueling Pianos"][0].venue_name == "Electric Piano Parlor"


def test_rundown_skips_away_games_out_of_area_reschedules_and_unplaceable_items():
    titles = {e.title for e in _rundown()}
    for gone in ("Big Country Star", "Alabama @ Mississippi State", "Rained Out 5K", "Bingo Night", "Burger Week", "Gallery Show"):
        assert gone not in titles


def test_tame_caps():
    assert tame_caps("WEIRD AL YANKOVIC with special guest PUDDLES") == "Weird Al Yankovic with Special Guest Puddles"
    assert tame_caps("GULF COAST CHALLENGE: ALABAMA A&M vs. JACKSON STATE") == "Gulf Coast Challenge: Alabama A&M vs. Jackson State"
    assert tame_caps("LEINKAUF LOCALS' EVENT: A NIGHT AT MONROE'S") == "Leinkauf Locals' Event: A Night at Monroe's"
    assert tame_caps("10TH ANNUAL BFM5K") == "10th Annual BFM5K"
    assert tame_caps("Port City R&B") == "Port City R&B"  # mixed case is left alone
