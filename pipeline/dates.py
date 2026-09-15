"""Date parsing. The least glamorous, most common source of wrong output. Tested.

Rules:
- Store UTC + explicit tz. Local times are for display only.
- "Fri 7pm" with no year -> guess the next occurrence, mark date_confident=False.
- All-day events: start at 00:00 local, end at 23:59:59 local.
- Ranges "04:00 PM - 05:00 PM" and "September 21, 2026 - September 23, 2026" handled.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from dateutil import parser as dtparser

DEFAULT_TZ = "America/Chicago"
UTC = ZoneInfo("UTC")

_TIME_RANGE_RE = re.compile(
    r"(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?)\s*(?:-|–|—|to)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?)",
    re.I,
)
_TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)\b", re.I)
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


@dataclass
class ParsedWhen:
    start: datetime | None          # aware, local tz
    end: datetime | None
    all_day: bool
    confident: bool


def tz(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or DEFAULT_TZ)
    except Exception:
        return ZoneInfo(DEFAULT_TZ)


def to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz(DEFAULT_TZ))
    return dt.astimezone(UTC)


def from_utc(dt: datetime | str | None, tzname: str = DEFAULT_TZ) -> datetime | None:
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(tz(tzname))


def iso_utc(dt: datetime | None) -> str | None:
    u = to_utc(dt)
    return u.strftime("%Y-%m-%dT%H:%M:%SZ") if u else None


def parse_local(s: str | None, tzname: str = DEFAULT_TZ, all_day_if_no_time: bool = True) -> ParsedWhen:
    """Parse a datetime string like '2026-09-15 19:00:00' or 'September 21, 2026 4:00 PM'."""
    if not s or not s.strip():
        return ParsedWhen(None, None, False, False)
    s = s.strip()
    z = tz(tzname)
    has_time = bool(_TIME_RE.search(s)) or bool(re.search(r"\d{1,2}:\d{2}", s))
    confident = bool(_YEAR_RE.search(s))
    try:
        dt = dtparser.parse(s, default=datetime(datetime.now(z).year, 1, 1, 0, 0))
    except (ValueError, OverflowError):
        return ParsedWhen(None, None, False, False)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=z)
    else:
        dt = dt.astimezone(z)
    if not confident:
        # no year: if that date is more than ~30 days in the past, it meant next year
        now = datetime.now(z)
        if dt < now - timedelta(days=30):
            dt = dt.replace(year=dt.year + 1)
    if not has_time and all_day_if_no_time:
        start = datetime.combine(dt.date(), time(0, 0), tzinfo=z)
        end = datetime.combine(dt.date(), time(23, 59, 59), tzinfo=z)
        return ParsedWhen(start, end, True, confident)
    return ParsedWhen(dt, None, False, confident and has_time)


def parse_time_range(times: str | None, on: date, tzname: str = DEFAULT_TZ) -> tuple[datetime | None, datetime | None, bool]:
    """'04:00 PM - 05:00 PM' on a date -> (start, end, has_time). Handles single times too."""
    z = tz(tzname)
    if not times or not times.strip():
        return None, None, False
    times = times.strip()
    m = _TIME_RANGE_RE.search(times)
    if m:
        a, b = m.group(1), m.group(2)
        # "7 - 9pm" -> the first time inherits the meridiem of the second
        a, b = a.strip(), b.strip()
        if not re.search(r"[ap]", a, re.I) and re.search(r"[ap]", b, re.I):
            a = a + " " + re.search(r"(am|pm|a\.m\.|p\.m\.)", b, re.I).group(1)
        try:
            start = dtparser.parse(a, default=datetime.combine(on, time(0, 0))).replace(tzinfo=z)
            end = dtparser.parse(b, default=datetime.combine(on, time(0, 0))).replace(tzinfo=z)
        except (ValueError, OverflowError):
            return None, None, False
        if end <= start:
            end += timedelta(days=1)  # crosses midnight
        return start, end, True
    m = _TIME_RE.search(times)
    if m:
        try:
            start = dtparser.parse(m.group(0), default=datetime.combine(on, time(0, 0))).replace(tzinfo=z)
            return start, None, True
        except (ValueError, OverflowError):
            return None, None, False
    return None, None, False


def parse_date_range(dates: str | None, tzname: str = DEFAULT_TZ) -> tuple[date | None, date | None]:
    """'September 21, 2026' or 'September 21, 2026 - September 23, 2026' -> (d1, d2)."""
    if not dates:
        return None, None
    parts = re.split(r"\s+(?:-|–|—|to|through)\s+", dates.strip(), maxsplit=1)
    try:
        d1 = dtparser.parse(parts[0]).date()
    except (ValueError, OverflowError):
        return None, None
    d2 = d1
    if len(parts) > 1:
        try:
            d2 = dtparser.parse(parts[1], default=datetime.combine(d1, time(0, 0))).date()
        except (ValueError, OverflowError):
            d2 = d1
    return d1, d2


def all_day_bounds(d1: date, d2: date | None, tzname: str = DEFAULT_TZ) -> tuple[datetime, datetime]:
    z = tz(tzname)
    return (
        datetime.combine(d1, time(0, 0), tzinfo=z),
        datetime.combine(d2 or d1, time(23, 59, 59), tzinfo=z),
    )


def local_day(dt_utc: datetime | str | None, tzname: str = DEFAULT_TZ) -> date | None:
    d = from_utc(dt_utc, tzname)
    return d.date() if d else None


def default_end(start: datetime | None, all_day: bool) -> datetime | None:
    """When a source gives no end: all-day ends 23:59:59; timed events assume 3 hours."""
    if start is None:
        return None
    if all_day:
        return datetime.combine(start.date(), time(23, 59, 59), tzinfo=start.tzinfo)
    return start + timedelta(hours=3)


def weekend_bounds(today: date) -> tuple[date, date]:
    """Fri..Sun containing or following today. On Sat/Sun returns the current weekend."""
    wd = today.weekday()  # Mon=0
    if wd >= 4:
        fri = today - timedelta(days=wd - 4)
    else:
        fri = today + timedelta(days=4 - wd)
    return fri, fri + timedelta(days=2)
