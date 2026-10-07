"""GrowthZone / ChamberMaster calendars (Mobile Chamber and most chambers of commerce).

Two URL layouts, both server-rendered listings with one clean iCal per event:
  hub:     /<calendar>/Details/<slug>   -> /<calendar>/ICal/<slug>.ics   (one listing page)
  classic: /events/details/<slug>       -> /events/ICal/<slug>.ics       (one listing page per month:
           /events/calendar/YYYY-MM-01; the page also links news items under /news/details/)
We fetch the listing(s), then one .ics per event.

config:
  listing_url: https://my.mobilechamber.com/mobilechambercalendar
  layout: hub | classic        # default hub
  months: 3                    # classic only: this month and the next N-1
  max_events: 80
  skip_titles: ["ribbon cutting", "\\bmeeting\\b"]   # regexes, matched against the slug and the title
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin, urlsplit

from .ics import IcsCollector
from .base import Collector, CollectorError, log

_HUB_RE = re.compile(r'href="([^"]*?/Details/([^"?/]+))(?:\?[^"]*)?"', re.I)
_CLASSIC_RE = re.compile(r'href="[^"]*?/events/details/([^"?/]+)', re.I)


class GrowthZoneCollector(Collector):
    collector_type = "growthzone"

    def fetch(self, start: date, end: date) -> list:
        listing = self.cfg.get("listing_url") or self.source["url"]
        skip = [re.compile(p, re.I) for p in self.cfg.get("skip_titles", [])]
        if self.cfg.get("layout") == "classic":
            slugs, base_path = self._classic_slugs(listing, start)
        else:
            slugs, base_path = self._hub_slugs(listing)
        if not slugs:
            raise CollectorError(f"no event links found on {listing} (layout changed?)")
        slugs = [s for s in slugs if not any(p.search(s.replace("-", " ")) for p in skip)]
        max_events = int(self.cfg.get("max_events", 80))
        ics = IcsCollector(self.source, session=self.session)
        out = []
        for slug in slugs[:max_events]:
            url = urljoin(listing, f"{base_path}/ICal/{slug}.ics")
            try:
                text = self.get_text(url)
                events = ics.parse(text, start, end)
            except Exception as e:  # one bad event must not sink the source
                log.warning("growthzone %s: %s -> %s", self.source["id"], slug, e)
                continue
            for ev in events:  # titles are filtered again after the fetch, in collect.py
                ev.external_id = f"{slug}:{ev.start_local.date().isoformat()}"
                # the ICS LOCATION is an address, not a name (parse already copied it to venue_address)
                if re.match(r"^\d", ev.venue_name):
                    ev.venue_name = ""
                if not ev.info_url or ev.info_url == self.source["url"]:
                    ev.info_url = urljoin(listing, f"{base_path}/{'details' if self.cfg.get('layout') == 'classic' else 'Details'}/{slug}")
                out.append(ev)
        return out

    def _hub_slugs(self, listing: str) -> tuple[list[str], str | None]:
        html = self.get_text(listing)
        slugs: list[str] = []
        base_path = None
        for href, slug in _HUB_RE.findall(html):
            if slug not in slugs:
                slugs.append(slug)
                base_path = base_path or href.split("/Details/")[0]
        return slugs, base_path

    def _classic_slugs(self, listing: str, start: date) -> tuple[list[str], str]:
        base = listing.rstrip("/")
        slugs: list[str] = []
        y, m = start.year, start.month
        for _ in range(int(self.cfg.get("months", 3))):
            for slug in _CLASSIC_RE.findall(self.get_text(f"{base}/{y:04d}-{m:02d}-01")):
                if slug not in slugs:
                    slugs.append(slug)
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        parts = urlsplit(listing)
        return slugs, f"{parts.scheme}://{parts.netloc}/events"
