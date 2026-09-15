from datetime import date, datetime
from zoneinfo import ZoneInfo

from pipeline.dates import (all_day_bounds, iso_utc, parse_date_range, parse_local, parse_time_range,
                            to_utc, weekend_bounds)

CT = ZoneInfo("America/Chicago")


def test_tribe_style_datetime_to_utc():
    p = parse_local("2026-09-15 19:00:00", "America/Chicago")
    assert p.confident and not p.all_day
    assert iso_utc(p.start) == "2026-09-16T00:00:00Z"  # CDT is UTC-5


def test_dst_weekend_is_handled():
    # Nov 1 2026 is the fall-back day; 7pm CST is UTC-6
    p = parse_local("2026-11-01 19:00:00")
    assert iso_utc(p.start) == "2026-11-02T01:00:00Z"
    # the day before is still CDT (UTC-5)
    q = parse_local("2026-10-31 19:00:00")
    assert iso_utc(q.start) == "2026-11-01T00:00:00Z"


def test_date_only_is_all_day():
    p = parse_local("2026-10-03")
    assert p.all_day and p.confident
    assert p.start.hour == 0 and p.end.hour == 23 and p.end.second == 59


def test_no_year_is_not_confident():
    p = parse_local("Fri Oct 9 7pm")
    assert not p.confident
    assert p.start.month == 10 and p.start.hour == 19


def test_garbage_returns_none():
    p = parse_local("TBA")
    assert p.start is None and not p.confident


def test_civicplus_time_range():
    s, e, has = parse_time_range("04:00 PM - 05:00 PM", date(2026, 9, 21))
    assert has and s.hour == 16 and e.hour == 17 and s.tzinfo is not None


def test_time_range_inherits_meridiem():
    s, e, _ = parse_time_range("7 - 9pm", date(2026, 9, 21))
    assert s.hour == 19 and e.hour == 21


def test_time_range_crossing_midnight():
    s, e, _ = parse_time_range("10:00 PM - 1:00 AM", date(2026, 9, 21))
    assert e.day == 22 and e > s


def test_multi_day_date_range():
    d1, d2 = parse_date_range("September 21, 2026 - September 23, 2026")
    assert (d1, d2) == (date(2026, 9, 21), date(2026, 9, 23))
    s, e = all_day_bounds(d1, d2)
    assert s.day == 21 and e.day == 23


def test_single_date_range():
    d1, d2 = parse_date_range(" September 21, 2026 ")
    assert d1 == d2 == date(2026, 9, 21)


def test_weekend_bounds():
    assert weekend_bounds(date(2026, 9, 14)) == (date(2026, 9, 18), date(2026, 9, 20))  # Monday -> coming Fri
    assert weekend_bounds(date(2026, 9, 19)) == (date(2026, 9, 18), date(2026, 9, 20))  # Saturday -> current weekend
    assert weekend_bounds(date(2026, 9, 18)) == (date(2026, 9, 18), date(2026, 9, 20))  # Friday -> today


def test_to_utc_assumes_central_for_naive():
    assert to_utc(datetime(2026, 7, 4, 12, 0)).hour == 17
