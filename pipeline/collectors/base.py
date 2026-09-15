"""Collector base: one HTTP session, one fetch() contract, no cleverness."""

from __future__ import annotations

import logging
import time
from datetime import date

import requests

from .. import config
from ..models import RawEvent

log = logging.getLogger("collect")


class CollectorError(Exception):
    pass


class Collector:
    collector_type = "base"

    def __init__(self, source: dict, session: requests.Session | None = None):
        self.source = source
        self.cfg = source.get("config") or {}
        s = config.settings().get("collect", {})
        self.timeout = int(s.get("http_timeout", 25))
        self.session = session or make_session()

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        raise NotImplementedError

    # ---- http helpers ----

    def get(self, url: str, params: dict | None = None, retries: int = 2) -> requests.Response:
        last: Exception | None = None
        for attempt in range(retries + 1):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout, allow_redirects=True)
                if r.status_code >= 500 and attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                r.raise_for_status()
                return r
            except requests.RequestException as e:
                last = e
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
        raise CollectorError(f"GET {url} failed: {last}")

    def get_json(self, url: str, params: dict | None = None):
        r = self.get(url, params)
        try:
            return r.json()
        except ValueError as e:
            raise CollectorError(f"GET {url} returned non-JSON ({r.status_code}, {len(r.content)} bytes)") from e

    def get_text(self, url: str, params: dict | None = None) -> str:
        return self.get(url, params).text


def make_session() -> requests.Session:
    s = requests.Session()
    ua = config.settings().get("collect", {}).get("user_agent") or "MobileBayEventsBot/0.1"
    s.headers.update({"User-Agent": ua, "Accept": "application/json, text/html, application/xml;q=0.9, */*;q=0.8"})
    return s
