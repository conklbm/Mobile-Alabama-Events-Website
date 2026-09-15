"""Venue resolution against the hand-edited alias map (data/venues.yaml)."""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz, process

from . import config
from .text import domain_of, norm_key


@dataclass
class VenueMatch:
    slug: str
    name: str
    city: str
    regions: list[str]
    score: float
    via: str  # alias | fuzzy | domain


class VenueResolver:
    def __init__(self, venues: list[dict] | None = None, fuzzy_threshold: float | None = None):
        venues = venues if venues is not None else config.venues()
        self.threshold = fuzzy_threshold or config.settings().get("dedup", {}).get("venue_alias_threshold", 90)
        self.by_key: dict[str, dict] = {}
        self.by_domain: dict[str, dict] = {}
        self.keys: list[str] = []
        for v in venues:
            names = [v["name"], *v.get("aliases", [])]
            for n in names:
                k = norm_key(n)
                if k and k not in self.by_key:
                    self.by_key[k] = v
            for d in v.get("domains", []):
                self.by_domain[domain_of(d)] = v
        self.keys = list(self.by_key)

    def _hit(self, v: dict, score: float, via: str) -> VenueMatch:
        return VenueMatch(v["slug"], v["name"], v.get("city", ""), list(v.get("regions", [])), score, via)

    def resolve(self, name: str | None, address: str | None = None, url: str | None = None) -> VenueMatch | None:
        """Exact alias -> fuzzy alias -> address-string alias -> venue domain in url. None = unknown."""
        k = norm_key(name)
        if k and k in self.by_key:
            return self._hit(self.by_key[k], 100.0, "alias")
        if k and self.keys:
            best = process.extractOne(k, self.keys, scorer=fuzz.token_sort_ratio, score_cutoff=self.threshold)
            if best:
                return self._hit(self.by_key[best[0]], float(best[1]), "fuzzy")
        ak = norm_key(address)
        if ak and ak in self.by_key:
            return self._hit(self.by_key[ak], 100.0, "alias")
        if ak:
            # address with a known alias embedded ("1905 W 1st St Gulf Shores, AL 36547")
            for key, v in self.by_key.items():
                if len(key) >= 8 and key in ak:
                    return self._hit(v, 95.0, "alias")
        d = domain_of(url)
        if d and d in self.by_domain:
            return self._hit(self.by_domain[d], 90.0, "domain")
        return None

    def origin_for_url(self, url: str | None) -> dict | None:
        """The one-hop rule: a listing that links to a venue's own domain has handed us the Tier A source."""
        d = domain_of(url)
        return self.by_domain.get(d) if d else None
