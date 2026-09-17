"""Generic iCalendar collector with RRULE expansion (recurring-ical-events)."""

from __future__ import annotations

import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events

from ..dates import DEFAULT_TZ
from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, CollectorError


class IcsCollector(Collector):
    collector_type = "ics"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        url = self.cfg.get("feed_url") or self.source["url"]
        text = self.get_text(url)
        return self.parse(text, start, end)

    def parse(self, text: str, start: date, end: date) -> list[RawEvent]:
        # ChamberMaster emits X-PUBLISHED-TTL:P1H / REFRESH-INTERVAL:P1H (invalid; PT1H is correct).
        # They're calendar-level hints we don't use, so drop them rather than fail the whole file.
        keep = [line for line in text.splitlines() if not line.startswith(("X-PUBLISHED-TTL", "REFRESH-INTERVAL"))]
        text = chr(10).join(keep)
        try:
            cal = icalendar.Calendar.from_ical(text)
        except Exception as e:  # icalendar raises ValueError subclasses
            raise CollectorError(f"ICS parse error: {e}") from e
        tzname = self.cfg.get("timezone") or DEFAULT_TZ
        z = ZoneInfo(tzname)
        out: list[RawEvent] = []
        for ev in recurring_ical_events.of(cal).between(start, end):
            title = clean_title(str(ev.get("SUMMARY", "")))
            if not title:
                continue
            dtstart = ev.get("DTSTART").dt if ev.get("DTSTART") else None
            dtend = ev.get("DTEND").dt if ev.get("DTEND") else None
            if dtstart is None:
                continue
            all_day = not isinstance(dtstart, datetime)
            if all_day:
                s = datetime.combine(dtstart, time(0, 0), tzinfo=z)
                # DTEND for all-day is exclusive; treat as inclusive end-of-day of the prior day
                e_date = (dtend if isinstance(dtend, date) and not isinstance(dtend, datetime) else None)
                if e_date and e_date > dtstart:
                    from datetime import timedelta
                    e_date = e_date - timedelta(days=1)
                e = datetime.combine(e_date or dtstart, time(23, 59, 59), tzinfo=z)
            else:
                s = dtstart if dtstart.tzinfo else dtstart.replace(tzinfo=z)
                s = s.astimezone(z)
                e = None
                if isinstance(dtend, datetime):
                    e = (dtend if dtend.tzinfo else dtend.replace(tzinfo=z)).astimezone(z)
            uid = str(ev.get("UID", "")) or title
            out.append(RawEvent(
                source_id=self.source["id"],
                external_id=f"{uid}:{s.date().isoformat()}",
                title=title,
                start_local=s,
                end_local=e,
                timezone=tzname,
                all_day=all_day,
                date_confident=True,
                venue_name=strip_html(str(ev.get("LOCATION", ""))),
                venue_address="",
                description=strip_html(str(ev.get("DESCRIPTION", ""))),
                info_url=str(ev.get("URL", "")) or self.source["url"],
                raw={k: str(v) for k, v in ev.items()},
            ))
        return out
