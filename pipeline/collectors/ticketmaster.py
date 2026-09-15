"""Ticketmaster Discovery API v2. Free key: https://developer.ticketmaster.com

Terms: attribution + link-back on every listing; no image reuse. The publisher
renders the "Powered by Ticketmaster" credit and images are gated off (image_ok=false)
for anything whose only image comes from here.

Skipped with a warning when TICKETMASTER_API_KEY is unset.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, CollectorError, log

API = "https://app.ticketmaster.com/discovery/v2/events.json"


class TicketmasterCollector(Collector):
    collector_type = "ticketmaster"
    SIZE = 100
    MAX_PAGES = 9  # API caps page*size at 1000

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        key = os.environ.get("TICKETMASTER_API_KEY", "").strip()
        if not key:
            raise CollectorError("TICKETMASTER_API_KEY not set — collector skipped")
        out: list[RawEvent] = []
        seen: set[str] = set()
        for sweep in self.cfg.get("sweeps") or []:
            for page in range(self.MAX_PAGES):
                data = self.get_json(API, {
                    "apikey": key,
                    "latlong": sweep["latlong"],
                    "radius": sweep.get("radius_miles", 40),
                    "unit": "miles",
                    "startDateTime": f"{start.isoformat()}T00:00:00Z",
                    "endDateTime": f"{end.isoformat()}T23:59:59Z",
                    "size": self.SIZE,
                    "page": page,
                    "sort": "date,asc",
                })
                events = (data.get("_embedded") or {}).get("events") or []
                for e in events:
                    if e.get("id") in seen:
                        continue
                    seen.add(e.get("id"))
                    ev = self._convert(e, sweep.get("regions") or [])
                    if ev:
                        out.append(ev)
                pg = data.get("page") or {}
                if page + 1 >= int(pg.get("totalPages") or 1) or not events:
                    break
        return out

    def _convert(self, e: dict, regions: list[str]) -> RawEvent | None:
        title = clean_title(e.get("name"))
        dates = e.get("dates") or {}
        st = dates.get("start") or {}
        tzname = dates.get("timezone") or "America/Chicago"
        z = ZoneInfo(tzname) if tzname else ZoneInfo("America/Chicago")
        start_local = None
        all_day = False
        confident = True
        if st.get("dateTime"):
            start_local = datetime.fromisoformat(st["dateTime"].replace("Z", "+00:00")).astimezone(z)
        elif st.get("localDate"):
            d = date.fromisoformat(st["localDate"])
            if st.get("localTime"):
                h, m, *_ = [int(x) for x in st["localTime"].split(":")]
                start_local = datetime(d.year, d.month, d.day, h, m, tzinfo=z)
            else:
                start_local = datetime(d.year, d.month, d.day, 0, 0, tzinfo=z)
                all_day = True
                confident = False
        if not title or start_local is None:
            return None
        if st.get("timeTBA") or st.get("noSpecificTime"):
            confident = False
        status = ((dates.get("status") or {}).get("code") or "").lower()
        emb = e.get("_embedded") or {}
        venue = (emb.get("venues") or [{}])[0] or {}
        addr = (venue.get("address") or {}).get("line1") or ""
        city = (venue.get("city") or {}).get("name") or ""
        price = ""
        for pr in e.get("priceRanges") or []:
            lo, hi = pr.get("min"), pr.get("max")
            if lo is not None:
                price = f"${lo:g}" if hi in (None, lo) else f"${lo:g}-{hi:g}"
                break
        cls = (e.get("classifications") or [{}])[0] or {}
        cats = [((cls.get(k) or {}).get("name") or "") for k in ("segment", "genre", "subGenre")]
        cats = [c for c in cats if c and c.lower() != "undefined"]
        attractions = [a.get("name") for a in emb.get("attractions") or [] if a.get("name")]
        desc = strip_html(e.get("info") or e.get("pleaseNote") or "")
        return RawEvent(
            source_id=self.source["id"],
            external_id=e.get("id") or f"tm:{title}:{start_local.isoformat()}",
            title=title,
            start_local=start_local,
            end_local=None,
            timezone=tzname,
            all_day=all_day,
            date_confident=confident,
            venue_name=strip_html(venue.get("name")),
            venue_address=", ".join(x for x in (addr, city) if x),
            city=city,
            description=desc,
            price=price,
            ticket_url=e.get("url") or "",
            info_url=e.get("url") or "",
            website="",
            image_url="",  # never reuse TM images
            organizer=", ".join(attractions),
            categories=cats,
            regions=list(regions),
            cancelled=(status == 'cancelled'),
            raw=e,
        )
