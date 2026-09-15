"""CivicPlus municipal calendar RSS (Gulf Shores, Orange Beach, ...).

Feed: /RSSFeed.aspx?ModID=58&CID=All-calendar.xml
Each <item> carries calendarEvent:EventDates / EventTimes / Location in a
site-specific namespace, so we match on local tag names rather than the URI.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from ..dates import all_day_bounds, parse_date_range, parse_time_range
from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, CollectorError

_EID_RE = re.compile(r"EID=(\d+)")


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1].lower()


class CivicPlusRssCollector(Collector):
    collector_type = "civicplus_rss"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        url = self.cfg.get("feed_url") or self.source["url"]
        text = self.get_text(url)
        return self.parse(text, start, end)

    def parse(self, text: str, start: date, end: date) -> list[RawEvent]:
        try:
            root = ET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
        except ET.ParseError as e:
            raise CollectorError(f"RSS parse error: {e}") from e
        out: list[RawEvent] = []
        for item in root.iter():
            if _local(item.tag) != "item":
                continue
            f: dict[str, str] = {}
            for child in item:
                f[_local(child.tag)] = (child.text or "").strip()
            title = clean_title(f.get("title"))
            link = f.get("link", "")
            d1, d2 = parse_date_range(f.get("eventdates"))
            if not title or d1 is None:
                continue
            if d2 < start or d1 > end:
                continue
            tzname = "America/Chicago"
            s, e, has_time = parse_time_range(f.get("eventtimes"), d1, tzname)
            if has_time and s:
                all_day = False
                if d2 != d1 and e:
                    e = e.replace(year=d2.year, month=d2.month, day=d2.day)
            else:
                s, e = all_day_bounds(d1, d2, tzname)
                all_day = True
            location = strip_html(f.get("location", ""))
            # CivicPlus concatenates street and city with no separator; split on the 2-letter state
            location = re.sub(r"(\S)([A-Z][a-z]+(?: [A-Z][a-z]+)*, [A-Z]{2} \d{5})$", r"\1, \2", location)
            eid = (_EID_RE.search(link) or _EID_RE.search(f.get("guid", "")))
            ext = f"{eid.group(1) if eid else title}:{d1.isoformat()}"
            out.append(RawEvent(
                source_id=self.source["id"],
                external_id=ext,
                title=title,
                start_local=s,
                end_local=e,
                timezone=tzname,
                all_day=all_day,
                date_confident=True,
                venue_name="",
                venue_address=location,
                city="",
                description=strip_html(re.sub(r"<strong>.*?</strong>", "", f.get("description", ""))),
                info_url=link,
                categories=[],
                raw=f,
            ))
        return out
