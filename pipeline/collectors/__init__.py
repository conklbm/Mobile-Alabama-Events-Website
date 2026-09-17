"""Collector registry. Add a collector_type here and in sources.yaml; nothing else changes."""

from .base import Collector, CollectorError, make_session
from .civicplus_rss import CivicPlusRssCollector
from .growthzone import GrowthZoneCollector
from .ics import IcsCollector
from .jsonld import JsonLdCollector
from .manual import ManualCollector
from .ticketmaster import TicketmasterCollector
from .tribe import TribeCollector

COLLECTORS: dict[str, type[Collector]] = {
    TribeCollector.collector_type: TribeCollector,
    TicketmasterCollector.collector_type: TicketmasterCollector,
    CivicPlusRssCollector.collector_type: CivicPlusRssCollector,
    GrowthZoneCollector.collector_type: GrowthZoneCollector,
    IcsCollector.collector_type: IcsCollector,
    JsonLdCollector.collector_type: JsonLdCollector,
    ManualCollector.collector_type: ManualCollector,
}

__all__ = ["COLLECTORS", "Collector", "CollectorError", "make_session"]
