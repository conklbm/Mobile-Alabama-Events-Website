"""Duda website "collections": the data tables behind event widgets on Duda-built sites
(Mobile Arts Council's community calendar, Eastern Shore Art Center's NeonCRM events).

GET {site}/rts/collections/public/{alias}/runtime/collection/{name}/data -> {"values": [{"data": {...}}], "page": {...}}

Every site names its columns differently, so config maps our fields to theirs. Only mapped
columns are read: Mobile Arts Council's rows also carry organizers' emails, which we never touch.

config:
  collection_url: https://www.mobilearts.org/rts/collections/public/eacd2e2c/runtime/collection/Event%20Information%20(Responses)/data
  fields: {title: "Event Title", start_date: "Event Start Date", start_time: "Event Start Time", ...}
          # also: end_date, end_time, venue, address, city, description, url, categories
  require: {"Event Web Publish": "Yes"}   # optional: only rows whose column equals this value
  category_sep: "||"
"""

from __future__ import annotations

import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from ..dates import DEFAULT_TZ
from ..models import RawEvent
from ..text import clean_title, slugify, strip_html, tame_caps
from .base import Collector, CollectorError, log

_CLOCK_RE = re.compile(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*([AP]M)?", re.I)


def _v(x) -> str:
    s = "" if x is None else str(x).strip()
    return "" if s in ("None", "null") else s


def _date(s: str) -> date | None:
    try:
        return date.fromisoformat(_v(s)[:10])
    except ValueError:
        return None


def _clock(s: str) -> time | None:
    """'3:00:00 PM' or '1970-01-01T10:00' (a time stored as a datetime)."""
    s = _v(s)
    m = _CLOCK_RE.search(s.split("T", 1)[1] if "T" in s else s)
    if not m:
        return None
    h, mi, ap = int(m[1]), int(m[2]), (m[3] or "").upper()
    if ap:
        h = h % 12 + (12 if ap == "PM" else 0)
    return time(h, mi) if h < 24 else None


class DudaCollectionCollector(Collector):
    collector_type = "duda_collection"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        data = self.get_json(self.cfg["collection_url"])
        if not isinstance(data, dict) or "values" not in data:
            raise CollectorError("collection response has no values (alias or collection name changed?)")
        if int((data.get("page") or {}).get("totalPages") or 1) > 1:
            # the endpoint ignores paging params and returns the first 100 rows
            log.warning("duda %s: %s rows but only the first page is readable", self.source["id"], data["page"].get("totalItems"))
        return self.parse(data["values"], start, end)

    def parse(self, rows: list[dict], start: date, end: date) -> list[RawEvent]:
        f = self.cfg["fields"]
        need = self.cfg.get("require", {})
        sep = self.cfg.get("category_sep", ",")
        z = ZoneInfo(DEFAULT_TZ)
        col = lambda r, k: _v(r.get(f[k])) if k in f else ""  # noqa: E731 — only mapped columns are ever read
        out: list[RawEvent] = []
        for row in rows:
            r = row.get("data") or {}
            if any(_v(r.get(k)) != v for k, v in need.items()):
                continue
            title = tame_caps(clean_title(col(r, "title")))
            sd = _date(col(r, "start_date"))
            if not title or sd is None or not (start <= sd <= end):
                continue
            ed = _date(col(r, "end_date")) or sd
            st, et = _clock(col(r, "start_time")), _clock(col(r, "end_time"))
            s = datetime.combine(sd, st or time(0, 0), tzinfo=z)
            fin = datetime.combine(ed, et, tzinfo=z) if et else (datetime.combine(ed, time(23, 59, 59), tzinfo=z) if st is None else None)
            venue, address = col(r, "venue"), col(r, "address")
            out.append(RawEvent(
                source_id=self.source["id"],
                external_id=f"{slugify(title)}:{sd.isoformat()}:{st.isoformat() if st else 'day'}",
                title=title,
                start_local=s,
                end_local=fin if fin and fin > s else None,
                timezone=DEFAULT_TZ,
                all_day=st is None,
                venue_name=venue or address,
                venue_address=", ".join(x for x in (venue, address) if x),  # "Art Center (Studio 5), 401 Oak St" still finds the venue
                city=col(r, "city"),
                description=strip_html(col(r, "description")),
                info_url=col(r, "url") or self.source["url"],
                organizer=col(r, "organizer"),
                categories=[c.strip(" []'\"") for c in col(r, "categories").split(sep) if c.strip(" []'\"")],
                raw={k: r.get(v) for k, v in f.items()},
            ))
        return out
