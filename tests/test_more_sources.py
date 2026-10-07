from datetime import date

from pipeline.collectors.duda import DudaCollectionCollector
from pipeline.collectors.growthzone import GrowthZoneCollector
from pipeline.collectors.ics import IcsCollector
from pipeline.collectors.jsonld import JsonLdCollector

WINDOW = (date(2026, 10, 1), date(2026, 12, 31))


def _ics(summary, location, day="20261016T180000"):
    return f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:{summary}@x
DTSTART;TZID=America/Chicago:{day}
SUMMARY:{summary}
LOCATION:{location}
END:VEVENT
END:VCALENDAR
"""


# ---------- GrowthZone classic layout (Eastern Shore Chamber) ----------

def test_growthzone_classic_reads_month_pages_skips_news_and_filtered_slugs(monkeypatch):
    src = {"id": "esc", "url": "https://chamber.example/events/calendar", "config": {
        "listing_url": "https://chamber.example/events/calendar", "layout": "classic", "months": 2,
        "skip_titles": ["ribbon cutting"]}}
    c = GrowthZoneCollector(src, session=None)
    pages = {
        "https://chamber.example/events/calendar/2026-10-01":
            '<a href="https://chamber.example/news/details/big-news-1">n</a>'
            '<a href="https://chamber.example/events/details/fall-market-101">a</a>'
            '<a href="https://chamber.example/events/details/ribbon-cutting-acme-102">b</a>',
        "https://chamber.example/events/calendar/2026-11-01":
            '<a href="https://chamber.example/events/details/fall-market-101">dup</a>'
            '<a href="https://chamber.example/events/details/jubilee-festival-103">c</a>',
    }
    fetched = []

    def fake_get_text(url, params=None):
        fetched.append(url)
        return pages.get(url) or _ics(url.rsplit("/", 1)[1], "Downtown Fairhope")

    monkeypatch.setattr(c, "get_text", fake_get_text)
    evs = c.fetch(*WINDOW)
    assert [u for u in fetched if u.endswith(".ics")] == ["https://chamber.example/events/ICal/fall-market-101.ics",
                                                           "https://chamber.example/events/ICal/jubilee-festival-103.ics"]
    assert evs[0].info_url == "https://chamber.example/events/details/fall-market-101"


# ---------- iCal filters (South Alabama home games) ----------

def test_ics_keeps_home_games_and_shortens_titles():
    src = {"id": "usa", "url": "https://x", "config": {"title_includes": [" vs "], "location_includes": ["mobile"],
                                                       "title_replace": {"University of South Alabama ": "South Alabama "}}}
    c = IcsCollector(src, session=None)
    home = c.parse(_ics("University of South Alabama Soccer vs Troy", "Mobile\\, AL\\, The Cage"), *WINDOW)
    away = c.parse(_ics("University of South Alabama Soccer at Troy", "Troy\\, AL"), *WINDOW)
    neutral = c.parse(_ics("University of South Alabama Tennis vs ITA Regionals", "Baton Rouge\\, LA"), *WINDOW)
    assert [e.title for e in home] == ["South Alabama Soccer vs Troy"] and away == [] and neutral == []


# ---------- JSON-LD via sitemap (Visit Mobile) ----------

def _ld(name, start, end):
    return ('<script type="application/ld+json">{"@type":"Event","name":"%s","startDate":"%s","endDate":"%s",'
            '"location":{"name":"Cooper Riverside Park"}}</script>' % (name, start, end))


def test_jsonld_sitemap_follows_matching_urls_and_skips_long_runs(monkeypatch):
    src = {"id": "vm", "url": "https://visit.example/events/", "config": {
        "sitemap": "https://visit.example/sitemap.xml", "follow_pattern": "/event/", "max_days": 7}}
    c = JsonLdCollector(src, session=None)
    pages = {
        "https://visit.example/sitemap.xml": "<urlset><url><loc>https://visit.example/about/</loc></url>"
                                             "<url><loc>https://visit.example/event/wine/1/</loc></url>"
                                             "<url><loc> https://visit.example/event/exhibit/2/ </loc></url></urlset>",
        "https://visit.example/event/wine/1/": _ld("Wine on the River", "2026-10-24", "2026-10-24"),
        "https://visit.example/event/exhibit/2/": _ld("Long Exhibit", "2026-10-01", "2026-12-31"),
    }
    fetched = []
    monkeypatch.setattr(c, "get_text", lambda url, params=None: fetched.append(url) or pages[url])
    evs = c.fetch(*WINDOW)
    assert "https://visit.example/about/" not in fetched
    assert [e.title for e in evs] == ["Wine on the River"] and evs[0].all_day


# ---------- Duda collections (Mobile Arts Council, Eastern Shore Art Center) ----------

def test_duda_maps_columns_and_never_reads_unmapped_ones():
    src = {"id": "mac", "url": "https://arts.example/calendar", "config": {
        "fields": {"title": "Event Title", "start_date": "Event Start Date", "start_time": "Event Start Time",
                   "address": "Event Location", "organizer": "Organization Name"}}}
    rows = [
        {"data": {"Event Title": "SKETCH CLUB", "Event Start Date": "2026-10-09T00:00", "Event Start Time": "2:00:00 PM",
                  "Event Location": "Mobile Botanical Gardens, 5151 Museum Dr", "Organization Name": "MBG",
                  "Organization Contact Information": "someone@example.com"}},
        {"data": {"Event Title": "Last year", "Event Start Date": "2025-10-11T00:00", "Event Start Time": "3:00:00 PM"}},
    ]
    (ev,) = DudaCollectionCollector(src, session=None).parse(rows, *WINDOW)
    assert ev.title == "Sketch Club" and ev.start_local.hour == 14 and not ev.all_day
    assert ev.venue_address == "Mobile Botanical Gardens, 5151 Museum Dr" and ev.organizer == "MBG"
    assert "someone@example.com" not in repr(ev)


def test_duda_neon_times_and_publish_flag():
    src = {"id": "esac", "url": "https://esac.example/events", "config": {
        "require": {"Event Web Publish": "Yes"}, "category_sep": "||",
        "fields": {"title": "Event Name", "start_date": "Event Start Date", "start_time": "Event Start Time",
                   "end_date": "Event End Date", "end_time": "Event End Time", "venue": "Event Location Name",
                   "address": "Full Street Address (F)", "categories": "Event Category Name"}}}
    base = {"Event Name": "Mess Makers", "Event Start Date": "2026-10-10T00:00", "Event Start Time": "1970-01-01T10:00",
            "Event End Date": "2026-10-10T00:00", "Event End Time": "1970-01-01T12:00",
            "Event Location Name": "Eastern Shore Art Center (Studio 5)", "Full Street Address (F)": "401 Oak Ave, Fairhope",
            "Event Category Name": "Teen||Mixed Media", "Event Web Publish": "Yes"}
    rows = [{"data": base}, {"data": dict(base, **{"Event Name": "Draft", "Event Web Publish": "No"})}]
    (ev,) = DudaCollectionCollector(src, session=None).parse(rows, *WINDOW)
    assert (ev.start_local.hour, ev.end_local.hour) == (10, 12)
    assert ev.venue_address.startswith("Eastern Shore Art Center (Studio 5), ") and ev.categories == ["Teen", "Mixed Media"]
