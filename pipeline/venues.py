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
        self.by_key: dict[str, list[dict]] = {}
        self.by_domain: dict[str, dict] = {}
        self.keys: list[str] = []
        for v in venues:
            names = [v["name"], *v.get("aliases", [])]
            for n in names:
                k = norm_key(n)
                if k:
                    self.by_key.setdefault(k, [])
                    if v not in self.by_key[k]:
                        self.by_key[k].append(v)
            for d in v.get("domains", []):
                self.by_domain[domain_of(d)] = v
        self.keys = list(self.by_key)

    def _hit(self, v: dict, score: float, via: str) -> VenueMatch:
        return VenueMatch(v["slug"], v["name"], v.get("city", ""), list(v.get("regions", [])), score, via)

    def _pick(self, cands: list[dict], city: str | None) -> dict | None:
        """Same name in two towns (Saenger Theatre: Mobile and Pensacola). A source-supplied city
        chooses; a city that contradicts every candidate means this is a venue we don't have."""
        ck = norm_key(city)
        if not ck:
            return cands[0]
        for v in cands:
            if norm_key(v.get("city")) == ck:
                return v
        if all(norm_key(v.get("city")) for v in cands):
            return None  # every candidate is somewhere else
        return next((v for v in cands if not norm_key(v.get("city"))), cands[0])

    def resolve(self, name: str | None, address: str | None = None, url: str | None = None, city: str | None = None) -> VenueMatch | None:
        """Exact alias -> fuzzy alias -> address-string alias -> venue domain in url. None = unknown."""
        k = norm_key(name)
        if k and k in self.by_key:
            v = self._pick(self.by_key[k], city)
            return self._hit(v, 100.0, "alias") if v else None
        if k and self.keys:
            best = process.extractOne(k, self.keys, scorer=fuzz.token_sort_ratio, score_cutoff=self.threshold)
            if best:
                v = self._pick(self.by_key[best[0]], city)
                if v:
                    return self._hit(v, float(best[1]), "fuzzy")
        ak = norm_key(address)
        if ak and ak in self.by_key:
            v = self._pick(self.by_key[ak], city)
            if v:
                return self._hit(v, 100.0, "alias")
        if ak:
            # address with a known alias embedded ("1905 W 1st St Gulf Shores, AL 36547")
            for key, cands in self.by_key.items():
                if len(key) >= 8 and key in ak:
                    v = self._pick(cands, city)
                    if v:
                        return self._hit(v, 95.0, "alias")
        d = domain_of(url)
        if d and d in self.by_domain:
            return self._hit(self.by_domain[d], 90.0, "domain")
        return None

    def origin_for_url(self, url: str | None) -> dict | None:
        """The one-hop rule: a listing that links to a venue's own domain has handed us the Tier A source."""
        d = domain_of(url)
        return self.by_domain.get(d) if d else None
