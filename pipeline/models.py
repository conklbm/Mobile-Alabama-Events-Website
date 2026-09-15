"""The one record type every collector emits. Normalization happens downstream."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawEvent:
    source_id: str
    external_id: str                 # stable within the source; used to recognize re-pulls
    title: str
    start_local: datetime | None     # tz-aware, in the event's own timezone
    end_local: datetime | None = None
    timezone: str = "America/Chicago"
    all_day: bool = False
    date_confident: bool = True      # False when year/time had to be guessed
    venue_name: str = ""
    venue_address: str = ""
    city: str = ""
    description: str = ""            # plain text, already stripped of HTML
    price: str = ""
    ticket_url: str = ""
    info_url: str = ""               # the listing we scraped (attribution link)
    website: str = ""                # outbound link from the listing (one-hop origin)
    image_url: str = ""
    organizer: str = ""
    categories: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)   # only when the source knows better than the venue
    cancelled: bool = False          # source explicitly says cancelled
    raw: dict = field(default_factory=dict)             # exactly as received; archived in raw_pulls
