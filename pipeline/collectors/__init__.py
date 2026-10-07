"""Collector registry. Add a collector_type here and in sources.yaml; nothing else changes."""

from .base import Collector, CollectorError, make_session
from .civicplus_rss import CivicPlusRssCollector
from .duda import DudaCollectionCollector
from .govcal import GovCalCollector
from .growthzone import GrowthZoneCollector
from .gulfshores import GulfShoresCollector
from .ics import IcsCollector
from .jsonld import JsonLdCollector
from .manual import ManualCollector
from .ticketmaster import TicketmasterCollector
from .tribe import TribeCollector
from .zew_rundown import ZewRundownCollector

COLLECTORS: dict[str, type[Collector]] = {
    TribeCollector.collector_type: TribeCollector,
    TicketmasterCollector.collector_type: TicketmasterCollector,
    CivicPlusRssCollector.collector_type: CivicPlusRssCollector,
    GrowthZoneCollector.collector_type: GrowthZoneCollector,
    IcsCollector.collector_type: IcsCollector,
    JsonLdCollector.collector_type: JsonLdCollector,
    ManualCollector.collector_type: ManualCollector,
    GovCalCollector.collector_type: GovCalCollector,
    ZewRundownCollector.collector_type: ZewRundownCollector,
    DudaCollectionCollector.collector_type: DudaCollectionCollector,
    GulfShoresCollector.collector_type: GulfShoresCollector,
}

__all__ = ["COLLECTORS", "Collector", "CollectorError", "make_session"]
