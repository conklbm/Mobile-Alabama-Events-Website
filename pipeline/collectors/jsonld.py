"""schema.org Event JSON-LD collector. Reads listing pages; optionally follows
links matching `follow_pattern` one hop to detail pages that carry the markup.

config:
  pages: [url, ...]
  follow_pattern: "/event/"   # optional substring; links containing it get fetched
  max_follow: 40
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from ..dates import DEFAULT_TZ, parse_local
from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, log

_LD_RE = re.compile(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.S | re.I)


def extract_events(html: str) -> list[dict]:
    """All JSON-LD objects whose @type is/contains 'Event'. Handles @graph and lists."""
    found: list[dict] = []
    for block in _LD_RE.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            try:
                data = json.loads(re.sub(r"[\x00-\x1f]", " ", block))
            except json.JSONDecodeError:
                continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                t = item.get("@type")
                types = t if isinstance(t, list) else [t]
                if any(isinstance(x, str) and x.endswith("Event") for x in types):
                    found.append(item)
                if "@graph" in item:
                    stack.append(item["@graph"])
                for k in ("subEvent", "itemListElement"):
                    if k in item:
                        stack.append(item[k])
    return found


class JsonLdCollector(Collector):
    collector_type = "jsonld"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        pages = list(self.cfg.get("pages") or [self.source["url"]])
        pattern = self.cfg.get("follow_pattern")
        max_follow = int(self.cfg.get("max_follow", 40))
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()
        out: list[RawEvent] = []
        queue = [(p, True) for p in pages]
        followed = 0
        while queue:
            url, is_listing = queue.pop(0)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            try:
                html = self.get_text(url)
            except Exception as e:
                log.warning("jsonld %s: %s", self.source["id"], e)
                continue
            for item in extract_events(html):
                ev = self._convert(item, url)
                if ev and start <= ev.start_local.date() <= end and ev.external_id not in seen_ids:
                    seen_ids.add(ev.external_id)
                    out.append(ev)
            if is_listing and pattern and followed < max_follow:
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, a["href"]).split("#")[0]
                    if pattern in href and href not in seen_urls and followed < max_follow:
                        queue.append((href, False))
                        followed += 1
        return out

    def _convert(self, it: dict, page_url: str) -> RawEvent | None:
        title = clean_title(it.get("name"))
        start_s = it.get("startDate")
        if not title or not start_s:
            return None
        tzname = self.cfg.get("timezone") or DEFAULT_TZ
        s = _parse_iso(start_s, tzname)
        e = _parse_iso(it.get("endDate"), tzname) if it.get("endDate") else None
        if s is None:
            return None
        all_day = len(str(start_s)) <= 10
        loc = it.get("location") or {}
        if isinstance(loc, list):
            loc = loc[0] if loc else {}
        if isinstance(loc, str):
            loc = {"name": loc}
        addr = loc.get("address") or {}
        if isinstance(addr, dict):
            addr_s = ", ".join(str(addr.get(k)) for k in ("streetAddress", "addressLocality") if addr.get(k))
            city = str(addr.get("addressLocality") or "")
        else:
            addr_s, city = str(addr), ""
        offers = it.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price = ""
        if isinstance(offers, dict):
            p = offers.get("price")
            if p not in (None, ""):
                price = "Free" if str(p) in ("0", "0.0", "0.00") else f"${p}"
        image = it.get("image")
        if isinstance(image, list):
            image = image[0] if image else ""
        if isinstance(image, dict):
            image = image.get("url") or ""
        org = it.get("organizer") or {}
        org_name = org.get("name") if isinstance(org, dict) else str(org or "")
        info_url = it.get("url") or page_url
        return RawEvent(
            source_id=self.source["id"],
            external_id=f"{info_url}:{s.date().isoformat()}",
            title=title,
            start_local=s,
            end_local=e,
            timezone=tzname,
            all_day=all_day,
            date_confident=True,
            venue_name=strip_html(loc.get("name") or ""),
            venue_address=addr_s,
            city=city,
            description=strip_html(it.get("description") or ""),
            price=price,
            ticket_url=(offers.get("url") if isinstance(offers, dict) else "") or "",
            info_url=info_url,
            website="",
            image_url=str(image or ""),
            organizer=org_name or "",
            categories=[str(it.get("eventType") or "")] if it.get("eventType") else [],
            raw=it,
        )


def _parse_iso(s: str | None, tzname: str) -> datetime | None:
    if not s:
        return None
    z = ZoneInfo(tzname)
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        p = parse_local(str(s), tzname)
        return p.start
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=z)
    return dt.astimezone(z)
