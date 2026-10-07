"""Areas and the two rings.

Core ring (Mobile, Eastern Shore): every event shows. Outer ring (Baldwin coast, Pensacola): only
events worth the drive, i.e. from a draw source (ticketed shows, editors' picks) or with a festival-type
title. A city outside every area falls back to the region tags on the venue/source.
All of it is configured in settings.yaml (areas:, outer_ring:).
"""

from __future__ import annotations

import re
from functools import lru_cache

from . import config
from .text import norm_key


@lru_cache(maxsize=None)
def _city_map() -> dict[str, str]:
    out: dict[str, str] = {}
    for area, a in (config.settings().get("areas") or {}).items():
        for c in a.get("cities", []):
            out[norm_key(c)] = area
    return out


@lru_cache(maxsize=None)
def _outer() -> tuple[frozenset[str], re.Pattern | None, re.Pattern | None]:
    o = config.settings().get("outer_ring") or {}
    words = re.compile(o["draw_words"], re.I) if o.get("draw_words") else None
    never = re.compile(o["never"], re.I) if o.get("never") else None
    return frozenset(o.get("draw_sources", [])), words, never


def area_of(city: str | None) -> str | None:
    return _city_map().get(norm_key(city))


def label(area: str | None) -> str:
    return ((config.settings().get("areas") or {}).get(area) or {}).get("label", "") if area else ""


def ring_of(area: str | None) -> str | None:
    return ((config.settings().get("areas") or {}).get(area) or {}).get("ring") if area else None


def _area_rule(area: str | None) -> dict:
    return ((config.settings().get("outer_ring") or {}).get("areas") or {}).get(area) or {}


def is_draw(title: str, source_ids, area: str | None = None, venue_slug: str | None = None) -> bool:
    """Worth an hour's drive: a draw source or a festival-type title, and not on the never list.
    An area can tighten this: draw sources count only at its big venues, plus its own never list."""
    sources, words, never = _outer()
    rule = _area_rule(area)
    title = title or ""
    if (never and never.search(title)) or (rule.get("never") and re.search(rule["never"], title, re.I)):
        return False
    if words and words.search(title):
        return True
    if not set(source_ids) & sources:
        return False
    return "venues" not in rule or venue_slug in rule["venues"]


def shows_on_site(region: str, regions: list[str], city: str | None, title: str, source_ids,
                  venue_slug: str | None = None) -> bool:
    if region != (config.settings().get("publish") or {}).get("region", "mobile"):
        return region in regions  # the rings belong to the Mobile site; other feeds keep plain region tags
    area = area_of(city)
    ring = ring_of(area)
    if ring == "core":
        return True
    if ring == "outer":
        return is_draw(title, source_ids, area, venue_slug)
    return region in regions


def clear_cache() -> None:
    _city_map.cache_clear()
    _outer.cache_clear()
