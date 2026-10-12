"""Happy hours: a hand-kept guide (data/happy_hours.yaml), not events. Turns the YAML into page views.

Each spot has one or more windows (days + start/end in 24h local time, end may be "close"), a short
list of deals, our own one-line note, the page that confirms it, and the date it was last checked.
"""

from __future__ import annotations

import json
from datetime import date

from .. import areas, config

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
_DAY_LABEL = {"mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu", "fri": "Fri", "sat": "Sat", "sun": "Sun"}


def _days_label(days: list[str]) -> str:
    """[mon..fri] -> 'Mon–Fri'; all seven -> 'Daily'; gaps -> 'Mon, Wed, Fri'."""
    idx = sorted(DAYS.index(d) for d in days if d in DAYS)
    if len(idx) == 7:
        return "Daily"
    runs: list[list[int]] = []
    for i in idx:
        if runs and i == runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    parts = []
    for r in runs:
        a, b = _DAY_LABEL[DAYS[r[0]]], _DAY_LABEL[DAYS[r[-1]]]
        parts.append(a if len(r) == 1 else (f"{a}, {b}" if len(r) == 2 else f"{a}–{b}"))
    return ", ".join(parts)


def _clock(hhmm: str) -> tuple[str, str]:
    """'16:00' -> ('4', 'pm'); '11:30' -> ('11:30', 'am'); 'close' -> ('close', '')."""
    if str(hhmm).lower() == "close":
        return "close", ""
    h, m = (int(x) for x in str(hhmm).split(":"))
    ap = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return (f"{h12}:{m:02d}" if m else f"{h12}"), ap


def _time_label(start: str, end: str) -> str:
    (s, sap), (e, eap) = _clock(start), _clock(end)
    if e == "close":
        return f"{s} {sap}–close"
    return f"{s}–{e} {eap}" if sap == eap else f"{s} {sap}–{e} {eap}"


def views(venue_pages: set[str] | None = None) -> list[dict]:
    """Spots ready for the template, sorted by area then name."""
    out = []
    for h in config.happy_hours():
        if h.get("status") == "unverified" or not h.get("windows"):
            continue  # kept for the monthly check, not shown until confirmed
        windows = h.get("windows") or []
        area = areas.area_of(h.get("city")) or ""
        checked = h.get("checked")
        checked_d = checked if isinstance(checked, date) else (date.fromisoformat(str(checked)) if checked else None)
        out.append({
            "name": h["name"],
            "neighborhood": h.get("neighborhood") or h.get("city") or "",
            "city": h.get("city") or "",
            "address": h.get("address") or "",
            "area": area,
            "area_label": areas.label(area) or (h.get("city") or ""),
            "when": " · ".join(f"{_days_label(w.get('days', []))} {_time_label(w['start'], w['end'])}" for w in windows),
            "windows_json": json.dumps([{"d": [DAYS.index(d) for d in w.get("days", []) if d in DAYS],
                                         "s": w["start"], "e": "23:59" if str(w["end"]).lower() == "close" else w["end"]}
                                        for w in windows], separators=(",", ":")),
            "deals": h.get("deals") or [],
            "note": h.get("note") or "",
            "url": h.get("url") or "",
            "checked": checked_d,
            "checked_label": f"{checked_d:%b} {checked_d.day}, {checked_d.year}" if checked_d else "",
            "venue_url": f"/venues/{h['venue']}/" if h.get("venue") and venue_pages and h["venue"] in venue_pages else "",
            "venue": h.get("venue") or "",
        })
    order = {k: i for i, k in enumerate((config.settings().get("areas") or {}).keys())}
    return sorted(out, key=lambda s: (order.get(s["area"], 99), s["name"].lower()))


def grouped(spots: list[dict]) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = {}
    for s in spots:
        groups.setdefault(s["area_label"], []).append(s)
    return list(groups.items())


def jsonld(spots: list[dict], site_url: str) -> dict:
    return {
        "@context": "https://schema.org", "@type": "ItemList", "name": "Happy hours in Mobile, AL and the Eastern Shore",
        "url": f"{site_url}/happy-hours/",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "FoodEstablishment", "name": s["name"],
                      "address": {"@type": "PostalAddress", "streetAddress": s["address"], "addressLocality": s["city"], "addressRegion": "AL"}}}
            for i, s in enumerate(spots)
        ],
    }
