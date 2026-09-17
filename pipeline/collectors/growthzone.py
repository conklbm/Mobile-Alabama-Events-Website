"""GrowthZone / ChamberMaster calendars (Mobile Chamber and most chambers of commerce).

The listing page is server-rendered with links to /<calendar>/Details/<slug>; each event
exposes a clean iCal at /<calendar>/ICal/<slug>.ics (title, local times with tz, address,
description, URL). We fetch the listing, then one .ics per event.

config:
  listing_url: https://my.mobilechamber.com/mobilechambercalendar
  max_events: 80
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin

from .ics import IcsCollector
from .base import Collector, CollectorError, log

_DETAIL_RE = re.compile(r'href="([^"]*?/Details/([^"?/]+))(?:\?[^"]*)?"', re.I)


class GrowthZoneCollector(Collector):
    collector_type = "growthzone"

    def fetch(self, start: date, end: date) -> list:
        listing = self.cfg.get("listing_url") or self.source["url"]
        html = self.get_text(listing)
        slugs: list[str] = []
        base_path = None
        for href, slug in _DETAIL_RE.findall(html):
            if slug not in slugs:
                slugs.append(slug)
                base_path = base_path or href.split("/Details/")[0]
        if not slugs:
            raise CollectorError(f"no event links found on {listing} (layout changed?)")
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
            for ev in events:
                ev.external_id = f"{slug}:{ev.start_local.date().isoformat()}"
                # the ICS LOCATION is an address, not a name; keep it where the resolver looks for addresses
                if ev.venue_name and not ev.venue_address and re.match(r"^\d", ev.venue_name):
                    ev.venue_address, ev.venue_name = ev.venue_name, ""
                if not ev.info_url or ev.info_url == self.source["url"]:
                    ev.info_url = urljoin(listing, f"{base_path}/Details/{slug}")
                out.append(ev)
        return out
