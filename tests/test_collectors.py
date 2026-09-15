from datetime import date

from pipeline.collectors.civicplus_rss import CivicPlusRssCollector
from pipeline.collectors.jsonld import extract_events
from pipeline.collectors.tribe import TribeCollector

SRC = {"id": "t", "name": "T", "url": "https://x", "tier": "A", "regions": ["mobile"], "config": {}}

RSS = """<?xml version="1.0"?><rss version="2.0" xmlns:calendarEvent="https://www.gulfshoresal.gov/Calendar.aspx"><channel>
<item><title>Council Work Session</title><link>https://www.gulfshoresal.gov/Calendar.aspx?EID=16360</link>
<description>&lt;strong&gt;Event date:&lt;/strong&gt; September 21, 2026 &lt;br&gt;desc here</description>
<calendarEvent:EventDates> September 21, 2026 </calendarEvent:EventDates>
<calendarEvent:EventTimes>04:00 PM - 05:00 PM</calendarEvent:EventTimes>
<calendarEvent:Location>1905 W 1st StGulf Shores, AL 36547</calendarEvent:Location></item>
<item><title>Fall Festival</title><link>https://www.gulfshoresal.gov/Calendar.aspx?EID=999</link>
<calendarEvent:EventDates>October 3, 2026 - October 4, 2026</calendarEvent:EventDates>
<calendarEvent:EventTimes></calendarEvent:EventTimes>
<calendarEvent:Location>Gulf Place</calendarEvent:Location></item>
<item><title>Way past</title><link>x?EID=1</link><calendarEvent:EventDates>January 1, 2020</calendarEvent:EventDates></item>
</channel></rss>"""


def test_civicplus_parse():
    c = CivicPlusRssCollector(SRC, session=None)
    evs = c.parse(RSS, date(2026, 9, 1), date(2026, 12, 31))
    assert [e.title for e in evs] == ["Council Work Session", "Fall Festival"]
    a, b = evs
    assert a.start_local.hour == 16 and a.end_local.hour == 17 and not a.all_day
    assert a.venue_address == "1905 W 1st St, Gulf Shores, AL 36547"
    assert a.external_id == "16360:2026-09-21"
    assert b.all_day and b.start_local.day == 3 and b.end_local.day == 4
    assert "desc here" in a.description and "Event date" not in a.description


def test_tribe_convert():
    e = {"id": 42, "title": "Beer, BBQ &#038; Bingo", "description": "<p>Join us &amp; win</p>", "all_day": False,
         "start_date": "2026-09-15 19:00:00", "end_date": "2026-09-15 21:00:00", "timezone": "America/Chicago",
         "cost": "Free", "website": "https://moesbbq.com", "url": "https://92zew.net/calendar/x/",
         "image": {"url": "https://92zew.net/i.jpg"}, "categories": [{"name": "92ZEW Live!"}],
         "venue": {"venue": "Moe&#8217;s Original BBQ", "address": "701 Springhill Ave", "city": "Mobile"}, "organizer": []}
    ev = TribeCollector(SRC, session=None)._convert(e)
    assert ev.title == "Beer, BBQ & Bingo" and ev.venue_name == "Moe’s Original BBQ"
    assert ev.external_id == "42:2026-09-15" and ev.website == "https://moesbbq.com"
    assert ev.end_local.hour == 21 and ev.categories == ["92ZEW Live!"] and ev.description == "Join us & win"


def test_jsonld_extract_handles_graph_lists_and_subtypes():
    html = """<html><script type="application/ld+json">{"@context":"https://schema.org","@graph":[
      {"@type":"WebSite","name":"x"},{"@type":"MusicEvent","name":"Show","startDate":"2026-10-01T20:00:00-05:00"}]}</script>
      <script type='application/ld+json'>[{"@type":["Event"],"name":"Fest","startDate":"2026-10-02"}]</script></html>"""
    found = extract_events(html)
    assert sorted(i["name"] for i in found) == ["Fest", "Show"]
