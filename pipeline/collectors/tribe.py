"""The Events Calendar (Tribe) WP REST collector. ONE collector, N domains.

GET {site}/wp-json/tribe/events/v1/events?per_page=50&start_date=...&end_date=...&page=N
Public, no auth. Extracts the `website` field — the one-hop origin link.
"""

from __future__ import annotations

from datetime import date

from ..dates import parse_local
from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, CollectorError, log


class TribeCollector(Collector):
    collector_type = "tribe_api"
    PER_PAGE = 50
    MAX_PAGES = 40  # 2000 events; a safety stop, not a target

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        base = self.source["url"].rstrip("/") + "/wp-json/tribe/events/v1/events"
        out: list[RawEvent] = []
        page = 1
        while page <= self.MAX_PAGES:
            data = self.get_json(base, {
                "per_page": self.PER_PAGE,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "page": page,
            })
            events = data.get("events") or []
            for e in events:
                ev = self._convert(e)
                if ev:
                    out.append(ev)
            total_pages = int(data.get("total_pages") or 1)
            if page >= total_pages or not events or not data.get("next_rest_url"):
                break
            page += 1
        return out

    def _convert(self, e: dict) -> RawEvent | None:
        tzname = e.get("timezone") or "America/Chicago"
        title = clean_title(e.get("title"))
        if not title:
            return None
        all_day = bool(e.get("all_day"))
        when = parse_local(e.get("start_date"), tzname, all_day_if_no_time=all_day)
        end_when = parse_local(e.get("end_date"), tzname, all_day_if_no_time=all_day)
        if when.start is None:
            log.warning("tribe %s: unparseable start_date %r for %r", self.source["id"], e.get("start_date"), title)
            return None
        end_dt = end_when.end if all_day else end_when.start
        venue = e.get("venue") or {}
        if isinstance(venue, list):
            venue = venue[0] if venue else {}
        organizers = e.get("organizer") or []
        if isinstance(organizers, dict):
            organizers = [organizers]
        org_name = ", ".join(strip_html(o.get("organizer")) for o in organizers if isinstance(o, dict) and o.get("organizer"))
        image = e.get("image") or {}
        image_url = image.get("url") if isinstance(image, dict) else ""
        cats = [c.get("name") for c in (e.get("categories") or []) if isinstance(c, dict) and c.get("name")]
        start_day = (e.get("start_date") or "")[:10]
        return RawEvent(
            source_id=self.source["id"],
            external_id=f"{e.get('id')}:{start_day}",
            title=title,
            start_local=when.start,
            end_local=end_dt,
            timezone=tzname,
            all_day=all_day,
            date_confident=True,
            venue_name=strip_html(venue.get("venue")),
            venue_address=", ".join(x for x in (strip_html(venue.get("address")), strip_html(venue.get("city"))) if x),
            city=strip_html(venue.get("city")),
            description=strip_html(e.get("description")),
            price=strip_html(e.get("cost")),
            ticket_url="",
            info_url=e.get("url") or "",
            website=(e.get("website") or "").strip(),
            image_url=image_url or "",
            organizer=org_name,
            categories=[strip_html(c) for c in cats],
            raw=e,
        )
