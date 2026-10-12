import json
from datetime import date

from pipeline import config
from pipeline.publish import happy_hours as hh


def test_day_and_time_labels():
    assert hh._days_label(["mon", "tue", "wed", "thu", "fri"]) == "Mon–Fri"
    assert hh._days_label(["sun", "mon", "tue", "wed", "thu", "fri", "sat"]) == "Daily"
    assert hh._days_label(["mon", "wed", "fri"]) == "Mon, Wed, Fri"
    assert hh._days_label(["sat", "sun"]) == "Sat, Sun"
    assert hh._time_label("16:00", "18:00") == "4–6 pm"
    assert hh._time_label("11:30", "14:00") == "11:30 am–2 pm"
    assert hh._time_label("21:00", "close") == "9 pm–close"


def test_views_group_by_area_and_link_known_venues(monkeypatch):
    data = [
        {"name": "Zed's", "city": "Fairhope", "windows": [{"days": ["fri"], "start": "15:00", "end": "18:00"}],
         "deals": ["$4 drafts"], "checked": date(2026, 10, 12)},
        {"name": "Dauphin's", "city": "Mobile", "neighborhood": "Downtown", "venue": "dauphins",
         "windows": [{"days": ["mon", "tue", "wed", "thu", "fri"], "start": "16:00", "end": "18:00"},
                     {"days": ["sat"], "start": "21:00", "end": "close"}],
         "deals": ["Half-price bottles of wine"], "url": "https://example.com", "checked": "2026-10-12"},
    ]
    monkeypatch.setattr(config, "happy_hours", lambda: data)
    spots = hh.views({"dauphins"})
    assert [s["name"] for s in spots] == ["Dauphin's", "Zed's"]                     # Mobile before Eastern Shore
    d = spots[0]
    assert d["when"] == "Mon–Fri 4–6 pm · Sat 9 pm–close" and d["venue_url"] == "/venues/dauphins/"
    assert json.loads(d["windows_json"])[1] == {"d": [5], "s": "21:00", "e": "23:59"}  # "close" counts as end of day
    assert d["checked_label"] == "Oct 12, 2026"
    assert [g for g, _ in hh.grouped(spots)] == ["Mobile", "Eastern Shore"]


def test_unverified_spots_stay_off_the_page(monkeypatch):
    data = [{"name": "Maybe Bar", "city": "Mobile", "status": "unverified",
             "windows": [{"days": ["fri"], "start": "16:00", "end": "18:00"}]},
            {"name": "No Times", "city": "Mobile", "deals": ["Cheap beer"]},
            {"name": "Sure Thing", "city": "Mobile", "windows": [{"days": ["fri"], "start": "16:00", "end": "18:00"}]}]
    monkeypatch.setattr(config, "happy_hours", lambda: data)
    assert [s["name"] for s in hh.views()] == ["Sure Thing"]

