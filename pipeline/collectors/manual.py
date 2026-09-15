"""Hand-entered events (the weekly Facebook scan). CSV in data/manual/events.csv."""

from __future__ import annotations

import csv
import hashlib
from datetime import date

from .. import config
from ..dates import DEFAULT_TZ, parse_local
from ..models import RawEvent
from ..text import clean_title
from .base import Collector, log


class ManualCollector(Collector):
    collector_type = "manual"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        path = config.ROOT / (self.cfg.get("path") or "data/manual/events.csv")
        if not path.exists():
            return []
        out: list[RawEvent] = []
        with path.open(encoding="utf-8", newline="") as f:
            for i, row in enumerate(csv.DictReader(f), start=2):
                row = {k.strip(): (v or "").strip() for k, v in row.items() if k}
                title = clean_title(row.get("title"))
                if not title:
                    continue
                when = parse_local(row.get("start"), DEFAULT_TZ)
                if when.start is None:
                    log.warning("manual row %d: bad start %r", i, row.get("start"))
                    continue
                end_when = parse_local(row.get("end"), DEFAULT_TZ) if row.get("end") else None
                if not (start <= when.start.date() <= end):
                    continue
                key = hashlib.sha1(f"{title}|{when.start.isoformat()}|{row.get('venue','')}".encode()).hexdigest()[:12]
                out.append(RawEvent(
                    source_id=self.source["id"],
                    external_id=key,
                    title=title,
                    start_local=when.start,
                    end_local=(end_when.end if (end_when and when.all_day) else (end_when.start if end_when else when.end)),
                    timezone=DEFAULT_TZ,
                    all_day=when.all_day,
                    date_confident=when.confident,
                    venue_name=row.get("venue", ""),
                    city=row.get("city", ""),
                    description=row.get("description", ""),
                    price=row.get("price", ""),
                    ticket_url=row.get("ticket_url", ""),
                    info_url=row.get("info_url", ""),
                    image_url=row.get("image_url", ""),
                    categories=[row["category"]] if row.get("category") else [],
                    raw=row,
                ))
        return out
