"""Load YAML config from data/. Everything tunable lives there, not in code."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
DB_PATH = DATA / "events.db"


def _load(name: str) -> Any:
    path = DATA / name
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=None)
def settings() -> dict:
    s = _load("settings.yaml")
    # env overrides for the few things that differ per environment
    site_url = os.environ.get("SITE_URL")
    if site_url:
        s.setdefault("publish", {})["site_url"] = site_url.rstrip("/")
    return s


@lru_cache(maxsize=None)
def sources() -> list[dict]:
    items = _load("sources.yaml")
    required = {"id", "name", "url", "collector_type", "tier", "regions", "license_notes", "redistributable"}
    for s in items:
        missing = required - set(s)
        if missing:
            raise ValueError(f"source {s.get('id')!r} missing required fields: {sorted(missing)}")
        s.setdefault("brand_tokens", [])
        s.setdefault("curated", False)
        s.setdefault("expected_min_events", 0)
        s.setdefault("config", {})
    return items


@lru_cache(maxsize=None)
def venues() -> list[dict]:
    items = _load("venues.yaml")
    for v in items:
        v.setdefault("aliases", [])
        v.setdefault("domains", [])
        v.setdefault("regions", ["mobile"])
        v.setdefault("state", "AL")
    return items


@lru_cache(maxsize=None)
def categories() -> dict:
    return _load("categories.yaml")


@lru_cache(maxsize=None)
def pages() -> dict:
    return _load("pages.yaml")


@lru_cache(maxsize=None)
def overrides() -> dict:
    o = _load("overrides.yaml")
    for k in ("merge", "never_merge", "cancelled", "not_cancelled", "force_publish"):
        o.setdefault(k, [])
    o.setdefault("attach_to_series", {})
    return o


@lru_cache(maxsize=None)
def series_notes() -> dict:
    return _load("series_notes.yaml") or {}


def clear_cache() -> None:
    for fn in (settings, sources, venues, categories, pages, overrides, series_notes):
        fn.cache_clear()
