from datetime import date

from pipeline.collectors.growthzone import GrowthZoneCollector

SRC = {"id": "mobilechamber", "name": "Mobile Chamber", "url": "https://my.mobilechamber.com/mobilechambercalendar",
       "tier": "A", "regions": ["mobile"], "config": {"listing_url": "https://my.mobilechamber.com/mobilechambercalendar"}}

LISTING = '''<a href="https://my.mobilechamber.com/mobilechambercalendar/Details/business-after-hours-1696248?sourceTypeId=Website">x</a>
<a href="/mobilechambercalendar/Details/business-after-hours-1696248?sourceTypeId=Hub">dup</a>
<a href="/mobilechambercalendar/Details/state-of-the-economy-1680864">y</a>'''

ICS = '''BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;TZID=America/Chicago:20261022T160000
DTEND;TZID=America/Chicago:20261022T180000
SUMMARY:Business After Hours: The Portier at Midtown
DESCRIPTION:Join us for networking.
LOCATION:20 Graf Dairy Dr Mobile AL 36606
UID:e.3117.1433011
URL:https://my.mobilechamber.com/boacalendar/Details/business-after-hours-1696248?sourceTypeId=Hub
END:VEVENT
END:VCALENDAR
'''


def test_growthzone_fetches_one_ics_per_unique_slug(monkeypatch):
    c = GrowthZoneCollector(SRC, session=None)
    fetched = []

    def fake_get_text(url, params=None):
        fetched.append(url)
        return LISTING if url.endswith("/mobilechambercalendar") else ICS

    monkeypatch.setattr(c, "get_text", fake_get_text)
    evs = c.fetch(date(2026, 9, 1), date(2026, 12, 31))
    ics_urls = [u for u in fetched if u.endswith(".ics")]
    assert ics_urls == ["https://my.mobilechamber.com/mobilechambercalendar/ICal/business-after-hours-1696248.ics",
                        "https://my.mobilechamber.com/mobilechambercalendar/ICal/state-of-the-economy-1680864.ics"]
    assert len(evs) == 2
    e = evs[0]
    assert e.title == "Business After Hours: The Portier at Midtown"
    assert e.start_local.hour == 16 and e.end_local.hour == 18 and e.timezone == "America/Chicago"
    assert e.venue_address == "20 Graf Dairy Dr Mobile AL 36606" and e.venue_name == ""   # address, not a name
    assert e.external_id == "business-after-hours-1696248:2026-10-22"
    assert "boacalendar/Details/business-after-hours-1696248" in e.info_url
