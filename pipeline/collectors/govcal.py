"""City of Mobile and Mobile County community calendars.

Both sites run the same vendor CMS. Their calendar pages fill themselves from one endpoint,
{site}assets/includes/ajax/json.php?type=events, which returns every event ever posted
(unsorted, ~10 MB for the county) as a JSON string wrapping a JSON object. No feed, no API docs.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from ..dates import DEFAULT_TZ
from ..models import RawEvent
from ..text import clean_title, strip_html, tame_caps
from .base import Collector, CollectorError

_TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*([AP]M)\s*$", re.I)


def _v(x) -> str:
    s = "" if x is None else str(x).strip()
    return "" if s in ("None", "null", "0000-00-00") else s


def _time(s: str) -> time | None:
    m = _TIME_RE.match(_v(s))
    if not m:
        return None
    h, mi, ap = int(m[1]) % 12, int(m[2]), m[3].upper()
    return time(h + (12 if ap == "PM" else 0), mi)


class GovCalCollector(Collector):
    collector_type = "govcal_json"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        site = self.cfg["site"].rstrip("/") + "/"
        r = self.get(site + "assets/includes/ajax/json.php",
                     {"type": "events", "layout": "list", "limit": int(self.cfg.get("limit", 20000))})
        try:
            data = r.json()
            if isinstance(data, str):  # the endpoint double-encodes
                data = json.loads(data)
        except ValueError as e:
            raise CollectorError(f"{site}: non-JSON event list") from e
        return self.parse(data, start, end)

    def parse(self, data: dict, start: date, end: date) -> list[RawEvent]:
        z = ZoneInfo(DEFAULT_TZ)
        detail = (self.cfg.get("detail_base") or self.cfg["site"]).rstrip("/") + "/"
        max_days = int(self.cfg.get("max_days", 10))
        out: list[RawEvent] = []
        for e in data.get("data") or []:
            title = tame_caps(clean_title(_v(e.get("title"))))
            if not title or _v(e.get("postponed")) == "1":
                continue
            try:
                sd = date.fromisoformat(_v(e.get("start_date")))
                ed = date.fromisoformat(_v(e.get("end_date")) or sd.isoformat())
            except ValueError:
                continue
            ed = max(ed, sd)
            if ed < start or sd > end:
                continue
            weekly = _v(e.get("recurring_type")) == "Week" and ed > sd
            if (ed - sd).days > max_days and not weekly:
                continue  # month-long runs (haunted houses, classes) have no single day to sit on
            days = [sd + timedelta(weeks=i) for i in range((ed - sd).days // 7 + 1)] if weekly else [sd]
            st, et = _time(e.get("start_time")), _time(e.get("end_time"))
            place = [_v(e.get("event_address")), _v(e.get("event_city"))]
            slug = _v(e.get("slug"))
            for d in days:
                if d < start or d > end:
                    continue
                last = d if weekly else ed
                s = datetime.combine(d, st or time(0, 0), tzinfo=z)
                if st is None:
                    fin = datetime.combine(last, time(23, 59, 59), tzinfo=z)
                else:
                    fin = datetime.combine(last, et, tzinfo=z) if et else None
                    if fin is not None and fin <= s:
                        fin = None  # "6 PM - 12 AM": let the pipeline pick a default end
                out.append(RawEvent(
                    source_id=self.source["id"],
                    external_id=f"{slug or title}:{d.isoformat()}",
                    title=title,
                    start_local=s,
                    end_local=fin,
                    timezone=DEFAULT_TZ,
                    all_day=st is None,
                    venue_name=_v(e.get("venue_name")),
                    venue_address=", ".join(p for p in place if p),
                    city=_v(e.get("event_city")),
                    description=strip_html(_v(e.get("content"))),
                    info_url=detail + slug if slug else self.source["url"],
                    website=_v(e.get("event_website")),
                    categories=[c.strip() for c in _v(e.get("category")).split(",") if c.strip()],
                    cancelled=_v(e.get("cancelled")) == "1",
                    raw={k: v for k, v in e.items() if k != "content"},
                ))
        return out
