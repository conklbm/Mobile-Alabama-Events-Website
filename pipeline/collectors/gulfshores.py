"""gulfshores.com (Gulf Shores & Orange Beach Tourism), festivals only.

The site's "Annual Events & Festivals" listing (/events-calendar/annual-festivals/, paged with
?page=,N) is server-rendered cards: title, venue name, and a date range. The event pages' own
JSON-LD dates are unreliable (stale years, shifted times), so dates come from the cards. Each event
page is opened only for its address block (a TouristDestination/LocalBusiness JSON-LD with a
PostalAddress), which gives the town, so the outer-ring rule can place it.

robots.txt asks for Crawl-delay: 5; config.delay honors it.

config:
  listing_url: https://www.gulfshores.com/events-calendar/annual-festivals/
  max_pages: 10
  delay: 5
  max_days: 7      # skip season-long runs
"""

from __future__ import annotations

import html
import json
import re
import time
from datetime import date, datetime, time as dtime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from ..dates import DEFAULT_TZ
from ..models import RawEvent
from ..text import clean_title, strip_html
from .base import Collector, CollectorError, log

_CARD_RE = re.compile(
    r'<h3>\s*<a href="(?P<href>/events-calendar/[a-z0-9-]+/(?P<slug>[a-z0-9-]+)/)"[^>]*>\s*<span>(?P<title>.*?)</span>\s*</a>\s*</h3>'
    r'(?P<rest>.*?)(?=<h3>\s*<a href="/events-calendar/|\Z)', re.S)
_VENUE_RE = re.compile(r'<div class="event-venue">(.*?)</div>', re.S)
_START_RE = re.compile(r'<span class="start">(.*?)</span>', re.S)
_END_RE = re.compile(r'<span class="end">(.*?)</span>', re.S)
_SUMMARY_RE = re.compile(r'field--name-body[^>]*>\s*<p>(.*?)</p>', re.S)
_LD_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S | re.I)


def _day(s: str) -> date | None:
    try:
        return datetime.strptime(re.sub(r"\s+", " ", html.unescape(strip_html(s))).strip(), "%B %d, %Y").date()
    except ValueError:
        return None


def _postal_address(page: str) -> dict:
    """The first schema.org PostalAddress on the page (the venue's), or {}."""
    for block in _LD_RE.findall(page):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for item in (data.get("@graph", [data]) if isinstance(data, dict) else data):
            addr = item.get("address") if isinstance(item, dict) else None
            if isinstance(addr, dict) and addr.get("streetAddress"):
                return addr
    return {}


class GulfShoresCollector(Collector):
    collector_type = "gulfshores_festivals"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        listing = self.cfg.get("listing_url") or self.source["url"]
        delay = float(self.cfg.get("delay", 5))
        cards: dict[str, dict] = {}
        for n in range(int(self.cfg.get("max_pages", 10))):
            if n:
                time.sleep(delay)
            page = self.get_text(listing + (f"?page=,{n}" if n else ""))
            found = self.parse_listing(page)
            new = {k: v for k, v in found.items() if k not in cards}
            if not new:
                break
            cards.update(new)
        if not cards:
            raise CollectorError(f"no event cards on {listing} (layout changed?)")
        out: list[RawEvent] = []
        for card in cards.values():
            if not self._keep(card, start, end):
                continue
            time.sleep(delay)
            try:
                addr = _postal_address(self.get_text(card["url"]))
            except Exception as e:  # one bad page must not sink the source
                log.warning("gulfshores: %s -> %s", card["url"], e)
                addr = {}
            out.append(self.to_event(card, addr))
        return out

    def parse_listing(self, page: str) -> dict[str, dict]:
        base = self.source["url"]
        cards: dict[str, dict] = {}
        for m in _CARD_RE.finditer(page):
            rest = m["rest"]
            first = _day((_START_RE.search(rest) or [None, ""])[1])
            if first is None:
                continue
            last = _day((_END_RE.search(rest) or [None, ""])[1]) or first
            cards[m["slug"]] = {
                "slug": m["slug"],
                "url": urljoin(base, m["href"]),
                "title": clean_title(html.unescape(strip_html(m["title"]))),
                "venue": html.unescape(strip_html((_VENUE_RE.search(rest) or [None, ""])[1])),
                "start": first,
                "end": max(last, first),
                "summary": strip_html((_SUMMARY_RE.search(rest) or [None, ""])[1]).rstrip(". "),
            }
        return cards

    def _keep(self, card: dict, start: date, end: date) -> bool:
        if card["end"] < start or card["start"] > end:
            return False
        return (card["end"] - card["start"]).days <= int(self.cfg.get("max_days", 7))

    def to_event(self, card: dict, addr: dict) -> RawEvent:
        z = ZoneInfo(DEFAULT_TZ)
        street, town = str(addr.get("streetAddress") or "").strip(), str(addr.get("addressLocality") or "").strip()
        return RawEvent(
            source_id=self.source["id"],
            external_id=f"{card['slug']}:{card['start'].isoformat()}",
            title=card["title"],
            start_local=datetime.combine(card["start"], dtime(0, 0), tzinfo=z),
            end_local=datetime.combine(card["end"], dtime(23, 59, 59), tzinfo=z),
            timezone=DEFAULT_TZ,
            all_day=True,
            venue_name=card["venue"],
            venue_address=", ".join(x for x in (card["venue"], street, town) if x),
            city=town,
            description=card["summary"],
            info_url=card["url"],
            raw={"card": {k: str(v) for k, v in card.items()}, "address": addr},
        )
