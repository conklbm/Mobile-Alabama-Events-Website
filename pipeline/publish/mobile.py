"""V1 publisher: mobilebayevents.com as a static site in site/.

Read-only consumer of the SQLite store. Renders:
  /                         this week, curated, grouped by category
  /events/<series-slug>/    the durable event page (next occurrence on top, history below)
  /venues/<venue-slug>/     upcoming + history at that venue
  /this-weekend/            evergreen URL, rotating content
  /<city-slug>/             satellite city pages (first-class from day one)
  /<category-slug>/         category pages
  /about/ /privacy/ /terms/  standard trust pages (/contact/ redirects to /about/)
  sitemap.xml, robots.txt, 404.html, and vercel.json (redirects + noindex guard) at repo root
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

from .. import config, db
from ..dates import from_utc, tz, weekend_bounds
from ..scoring import TIER_RANK
from ..text import excerpt, is_free_price

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
STATIC = HERE / "static"

CATEGORY_LABELS = {
    "music": "Music", "family": "Family & Kids", "food": "Food & Drink", "active": "Active",
    "sports": "Sports", "arts": "Arts & Theater", "community": "Community", "nightlife": "Nightlife",
}
CATEGORY_ORDER = ["music", "family", "food", "active", "sports", "arts", "community", "nightlife"]


# ---------- view models ----------

class Site:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        s = config.settings()
        p = s.get("publish", {})
        self.url = p.get("site_url", "https://www.mobilebayevents.com").rstrip("/")
        self.name = p.get("site_name", "Mobile Bay Events")
        self.region = p.get("region", "mobile")
        self.featured_count = int(p.get("featured_count", 10))
        self.redirect_after = int(p.get("one_off_redirect_after_days", 7))
        self.tzname = s.get("timezone", "America/Chicago")
        self.now = datetime.now(tz(self.tzname))
        self.today = self.now.date()
        self.pages = config.pages()
        self.notes = config.series_notes()
        self.venues = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM venues")}
        self.sources = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM sources")}
        self.occurrences = self._load_occurrences()
        self.by_series: dict[int, list[dict]] = defaultdict(list)
        for o in self.occurrences:
            self.by_series[o["series_id"]].append(o)
        self.series = self._load_series()

    def _load_occurrences(self) -> list[dict]:
        rows = self.conn.execute(
            """SELECT o.*, s.slug AS series_slug, s.canonical_title AS series_title, s.cadence
               FROM occurrences o JOIN series s ON s.id=o.series_id
               WHERE o.publish_state='published' AND o.status IN ('active','flagged_cancelled')
               ORDER BY o.start_utc"""
        ).fetchall()
        out = []
        for r in rows:
            regions = db.uj(r["regions"])
            if self.region not in regions:
                continue
            out.append(self._occ_view(r))
        return out

    def _occ_view(self, r: sqlite3.Row) -> dict:
        start = from_utc(r["start_utc"], r["timezone"])
        end = from_utc(r["end_utc"], r["timezone"])
        venue = self.venues.get(r["venue_id"]) if r["venue_id"] else None
        srows = self.conn.execute(
            """SELECT os.source_url, os.origin_url, os.origin_tier, os.source_id, s.name, s.tier, s.curated, s.collector_type
               FROM occurrence_sources os JOIN sources s ON s.id=os.source_id WHERE os.occurrence_id=?""",
            (r["id"],),
        ).fetchall()

        def rank(x):
            return (TIER_RANK.get("A" if x["origin_tier"] == "A" else x["tier"], 9), 0 if x["curated"] else 1, x["source_id"])

        srows = sorted(srows, key=rank)
        primary = srows[0] if srows else None
        info_url = (primary["origin_url"] or primary["source_url"]) if primary else (r["info_url"] or "")
        notes = self.notes.get(r["series_slug"]) or {}
        override = notes.get("category")
        cats = ([override] if isinstance(override, str) else list(override)) if override else (db.uj(r["categories"]) or [r["category"]])
        cats = [c for c in cats if c in CATEGORY_LABELS][:2] or ["community"]
        multi_day = end.date() > start.date() and r["all_day"]
        return {
            "id": r["id"], "series_id": r["series_id"], "series_slug": r["series_slug"],
            "url": f"/events/{r['series_slug']}/",
            "title": r["title_raw"],
            "start": start, "end": end, "day": start.date(), "all_day": bool(r["all_day"]), "time_tba": bool(r["time_tba"]), "multi_day": multi_day,
            "venue": _venue_view(venue) if venue else None,
            "venue_name_raw": r["venue_name_raw"] or "",
            "city": (venue["city"] if venue else r["city"]) or "",
            "price": r["price"] or "", "is_free": is_free_price(r["price"]),
            "ticket_url": r["ticket_url"] or "",
            "info_url": info_url,
            "primary_source": primary["name"] if primary else "",
            "sources": [{"name": x["name"], "url": x["origin_url"] or x["source_url"], "tier": x["tier"]} for x in srows if (x["origin_url"] or x["source_url"])],
            "powered_by_ticketmaster": any(x["collector_type"] == "ticketmaster" for x in srows),
            "image": {"url": r["image_url"], "credit": r["image_credit"], "source_url": r["image_source_url"]} if r["image_ok"] and r["image_url"] else None,
            "category": cats[0],
            "categories": cats,
            "category_label": CATEGORY_LABELS.get(cats[0], "Community"),
            "category_labels": [CATEGORY_LABELS.get(c, c.title()) for c in cats],
            "description": r["description"] or "",
            "excerpt": excerpt(r["description"], 180),
            "kids_under_6": bool(notes.get("kids_under_6")),
            "blurb": notes.get("blurb", ""),
            "flagged": r["status"] == "flagged_cancelled",
            "curation_score": r["curation_score"], "independent_source_count": r["independent_source_count"],
            "featured_pin": bool(notes.get("featured")), "never_feature": bool(notes.get("never_feature")),
            "cadence": r["cadence"],
        }

    def _load_series(self) -> dict[int, dict]:
        out = {}
        for sid, occs in self.by_series.items():
            row = self.conn.execute("SELECT * FROM series WHERE id=?", (sid,)).fetchone()
            venue = self.venues.get(row["venue_id"]) if row["venue_id"] else None
            upcoming = [o for o in occs if o["end"] >= self.now]
            past = [o for o in occs if o["end"] < self.now]
            notes = self.notes.get(row["slug"]) or {}
            out[sid] = {
                "id": sid, "slug": row["slug"], "url": f"/events/{row['slug']}/",
                "title": row["canonical_title"],
                "venue": _venue_view(venue) if venue else None,
                "venue_name_raw": row["venue_name_raw"] or "",
                "cadence": notes.get("cadence") or row["cadence"],
                "category": notes.get("category") or row["category"],
                "description": (upcoming[0]["description"] if upcoming else (occs[-1]["description"] if occs else "")) or row["description"] or "",
                "blurb": notes.get("blurb", ""), "parking": notes.get("parking", ""),
                "kids_under_6": bool(notes.get("kids_under_6")),
                "upcoming": upcoming, "past": list(reversed(past))[:24],
                "next": upcoming[0] if upcoming else None,
                "last_end": max(o["end"] for o in occs),
            }
        return out

    # ---------- selections ----------

    @property
    def upcoming(self) -> list[dict]:
        return [o for o in self.occurrences if o["end"] >= self.now]

    def within(self, days: int) -> list[dict]:
        cutoff = self.today + timedelta(days=days)
        return [o for o in self.upcoming if o["day"] <= cutoff]

    def featured(self) -> list[dict]:
        pool = [o for o in self.within(7) if not o["never_feature"] and not o["flagged"] and not _never_feature_title(o["title"])]
        pool.sort(key=lambda o: (0 if o["featured_pin"] else 1, -o["curation_score"], -o["independent_source_count"],
                                 0 if o["image"] else 1, o["start"]))
        seen: set[int] = set()
        out = []
        for o in pool:
            if o["series_id"] in seen:
                continue
            seen.add(o["series_id"])
            out.append(o)
            if len(out) >= self.featured_count:
                break
        return out


def _venue_view(v: dict) -> dict:
    return {"slug": v["slug"], "name": v["canonical_name"], "city": v.get("city") or "", "address": v.get("address") or "",
            "state": v.get("state") or "AL", "zip": v.get("zip") or "", "url": f"/venues/{v['slug']}/",
            "notes": v.get("notes") or "", "lat": v.get("lat"), "lng": v.get("lng")}


def _never_feature_title(title: str) -> bool:
    from ..categories import never_feature
    return never_feature(title)


def group_by_day(occs: list[dict]) -> list[tuple[date, list[dict]]]:
    g: dict[date, list[dict]] = defaultdict(list)
    for o in occs:
        g[o["day"]].append(o)
    return sorted(g.items())


# ---------- rendering ----------

class Renderer:
    def __init__(self, site: Site, out: Path):
        self.site = site
        self.out = out
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))
        self.env.filters["day"] = lambda d: d.strftime("%A, %B %-d") if hasattr(d, "strftime") and _posix() else d.strftime("%A, %B %d").replace(" 0", " ")
        self.env.filters["shortday"] = lambda d: d.strftime("%a %b %d").replace(" 0", " ")
        self.env.filters["clock"] = _clock
        self.env.filters["isodt"] = lambda d: d.isoformat()
        self.env.filters["catlabel"] = lambda c: CATEGORY_LABELS.get(c, c.title())
        self.env.globals["CATEGORY_ORDER"] = CATEGORY_ORDER
        self.env.filters["richtext"] = render_richtext
        self.urls: list[tuple[str, str]] = []  # (path, lastmod)
        self.redirects: list[dict] = []
        self.nav = {
            "cities": [{"slug": c["slug"], "title": c["h1"]} for c in site.pages.get("cities", [])],
            "categories": [{"slug": c["slug"], "title": c["h1"]} for c in site.pages.get("categories", [])],
        }

    def page(self, path: str, template: str, *, title: str, description: str, noindex: bool = False, jsonld=None, index: bool = True, **ctx):
        path = path if path.endswith("/") else path + "/"
        html = self.env.get_template(template).render(
            site={"name": self.site.name, "url": self.site.url},
            nav=self.nav, now=self.site.now, year=self.site.now.year, today=self.site.today,
            canonical=self.site.url + path, path=path, title=title, meta_description=description[:160],
            noindex=noindex, jsonld=jsonld, **ctx,
        )
        dest = self.out / path.strip("/") / "index.html" if path != "/" else self.out / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        if index and not noindex:
            self.urls.append((path, self.site.now.date().isoformat()))

    def event_jsonld(self, s: dict) -> list[dict]:
        out = []
        for o in s["upcoming"][:10]:
            ev = {
                "@context": "https://schema.org", "@type": "Event",
                "name": o["title"],
                "startDate": o["start"].isoformat() if not (o["all_day"] or o["time_tba"]) else o["day"].isoformat(),
                "endDate": o["end"].isoformat() if not (o["all_day"] or o["time_tba"]) else o["end"].date().isoformat(),
                "eventStatus": "https://schema.org/EventCancelled" if o["flagged"] else "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "url": self.site.url + s["url"],
            }
            if o["description"]:
                ev["description"] = excerpt(o["description"], 300)
            if o["image"]:
                ev["image"] = o["image"]["url"]
            v = o["venue"]
            if v:
                ev["location"] = {"@type": "Place", "name": v["name"],
                                  "address": {"@type": "PostalAddress", "streetAddress": v["address"], "addressLocality": v["city"],
                                              "addressRegion": v["state"], "postalCode": v["zip"], "addressCountry": "US"}}
            elif o["venue_name_raw"]:
                ev["location"] = {"@type": "Place", "name": o["venue_name_raw"]}
            if o["ticket_url"] or o["price"]:
                offer = {"@type": "Offer", "url": o["ticket_url"] or o["info_url"], "availability": "https://schema.org/InStock"}
                if o["is_free"]:
                    offer.update({"price": "0", "priceCurrency": "USD"})
                ev["offers"] = offer
            out.append(ev)
        return out


_URL_RE = __import__("re").compile(r"(https?://[^\s<>\"')]+[^\s<>\"'.,;:!?)])")


def _linkify(text: str) -> str:
    parts, last = [], 0
    for m in _URL_RE.finditer(text):
        parts.append(str(escape(text[last:m.start()])))
        u = m.group(1)
        parts.append(f'<a href="{escape(u)}" target="_blank" rel="noopener">{escape(u)}</a>')
        last = m.end()
    parts.append(str(escape(text[last:])))
    return "".join(parts)


def render_richtext(text: str | None, fold_after: int = 3) -> Markup:
    """Plain text with blank-line paragraphs and '- ' bullets -> <p>/<ul>; long text folds behind Read more."""
    if not text:
        return Markup("")
    blocks: list[str] = []
    for chunk in [c.strip() for c in text.split("\n\n") if c.strip()]:
        lines = [l.strip() for l in chunk.split("\n") if l.strip()]
        if len(lines) == 1 and lines[0].startswith("## "):
            blocks.append(f"<h3>{_linkify(lines[0][3:].strip())}</h3>")
        elif all(l.startswith(("- ", "• ", "* ")) for l in lines):
            blocks.append("<ul>" + "".join(f"<li>{_linkify(l[2:].strip())}</li>" for l in lines) + "</ul>")
        else:
            blocks.append("<p>" + "<br>".join(_linkify(l) for l in lines) + "</p>")
    if len(blocks) <= fold_after + 1:
        return Markup("".join(blocks))
    # fold after `fold_after` real paragraphs; never end the visible part on a heading
    cut, seen = len(blocks), 0
    for i, b in enumerate(blocks):
        if not b.startswith("<h3>"):
            seen += 1
        if seen == fold_after:
            cut = i + 1
            break
    while cut > 1 and blocks[cut - 1].startswith("<h3>"):
        cut -= 1
    head, tail = "".join(blocks[:cut]), "".join(blocks[cut:])
    return Markup(f'{head}<details class="readmore"><summary>Read more</summary>{tail}</details>')


def _posix() -> bool:
    import os
    return os.name != "nt"


def _clock(d: datetime) -> str:
    s = d.strftime("%I:%M %p").lstrip("0").lower()
    return s.replace(":00", "")


# ---------- the publish entry point ----------

def publish(conn: sqlite3.Connection, out: Path | None = None, vercel_path: Path | None = None) -> dict:
    out = out or config.SITE
    vercel_path = vercel_path or (config.ROOT / "vercel.json")
    site = Site(conn)
    if out.exists():
        for child in out.iterdir():
            if child.name in (".gitkeep",):
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    if STATIC.exists():
        shutil.copytree(STATIC, out / "assets", dirs_exist_ok=True)
        for f in ("favicon.ico", "icon.svg", "apple-touch-icon.png", "icon-192.png", "icon-512.png"):
            if (STATIC / f).exists():
                shutil.copy(STATIC / f, out / f)
    r = Renderer(site, out)
    counts = defaultdict(int)

    # home
    week = site.within(7)
    r.page("/", "index.html", title=f"{site.name} — What's happening in Mobile, AL this week",
           description="This week's events in Mobile, the Eastern Shore, and Dauphin Island, pulled from venue calendars and merged so each shows once. Updated every Thursday.",
           featured=site.featured(), groups=group_by_day(week), week=week,
           week_count=len(week), upcoming_count=len(site.upcoming))
    counts["home"] += 1

    # this weekend
    fri, sun = weekend_bounds(site.today)
    wk = [o for o in site.upcoming if fri <= o["day"] <= sun]
    r.page("/this-weekend/", "list.html", title=f"This Weekend in Mobile, AL — {fri:%b %d}–{sun:%d}",
           description=f"Things to do in Mobile this weekend, {fri:%B %d} to {sun:%B %d}: live music, festivals, family events, and more.",
           h1="This Weekend in Mobile", intro=f"Friday {fri:%B %d} through Sunday {sun:%B %d}. Updated Thursdays.",
           groups=group_by_day(wk), empty="Nothing listed for this weekend yet. Check the full calendar below.")
    counts["pages"] += 1

    # all upcoming
    r.page("/events/", "list.html", title=f"All Upcoming Events in Mobile, AL — {site.name}",
           description="Every upcoming event we're tracking across Mobile, the Eastern Shore, and Dauphin Island, by date.",
           h1="All Upcoming Events", intro="", groups=group_by_day(site.upcoming), empty="No upcoming events yet.")
    counts["pages"] += 1

    # city pages
    for c in site.pages.get("cities", []):
        cities = {x.lower() for x in c.get("cities", [])}
        occs = [o for o in site.upcoming if (o["city"] or "").lower() in cities]
        r.page(f"/{c['slug']}/", "list.html", title=f"{c['title']} — This Week & Upcoming",
               description=(c.get("intro") or "").strip()[:160], h1=c["h1"], intro=(c.get("intro") or "").strip(),
               groups=group_by_day(occs), empty=f"Nothing listed for {c['h1'].replace(' Events', '')} right now. New events are added every Thursday.",
               noindex=len(occs) == 0)
        counts["city_pages"] += 1

    # category pages
    for c in site.pages.get("categories", []):
        cat = c["category"]
        occs = [o for o in site.upcoming if (o["is_free"] if cat == "free" else cat in o["categories"])]
        r.page(f"/{c['slug']}/", "list.html", title=c["title"], description=(c.get("intro") or "").strip()[:160],
               h1=c["h1"], intro=(c.get("intro") or "").strip(), groups=group_by_day(occs),
               empty="Nothing in this category right now. New events are added every Thursday.", noindex=len(occs) == 0)
        counts["category_pages"] += 1

    # series pages + expiry
    venue_series: dict[str, list[dict]] = defaultdict(list)
    for s in site.series.values():
        if s["venue"]:
            venue_series[s["venue"]["slug"]].append(s)
        expired = not s["upcoming"] and (site.now - s["last_end"]).days > site.redirect_after
        if s["cadence"] == "one_off" and expired:
            r.redirects.append({"source": s["url"].rstrip("/") + "(/)?", "destination": s["venue"]["url"] if s["venue"] else "/", "permanent": True})
            counts["expired_redirects"] += 1
            continue
        nxt = s["next"]
        when = f" — {nxt['day']:%b %d}" if nxt else ""
        where = f" at {s['venue']['name']}" if s["venue"] else (f" at {s['venue_name_raw']}" if s["venue_name_raw"] else "")
        desc = s["blurb"] or excerpt(s["description"], 160) or f"{s['title']}{where}. Dates, tickets, and details."
        r.page(s["url"], "series.html", title=f"{s['title']}{where}{when} | {site.name}", description=desc,
               s=s, jsonld=r.event_jsonld(s), noindex=not s["upcoming"] and not s["past"])
        counts["series_pages"] += 1

    # venue pages
    for slug, slist in venue_series.items():
        v = slist[0]["venue"]
        up = sorted((o for s in slist for o in s["upcoming"]), key=lambda o: o["start"])
        past = sorted((o for s in slist for o in s["past"]), key=lambda o: o["start"], reverse=True)[:30]
        r.page(v["url"], "venue.html", title=f"Events at {v['name']} — {v['city']}, {v['state']}",
               description=f"Upcoming events at {v['name']} in {v['city']}, AL, plus past shows. {v['notes'] or ''}".strip()[:160],
               v=v, upcoming=group_by_day(up), past=past,
               jsonld=[{"@context": "https://schema.org", "@type": "Place", "name": v["name"],
                        "address": {"@type": "PostalAddress", "streetAddress": v["address"], "addressLocality": v["city"], "addressRegion": v["state"], "postalCode": v["zip"]}}])
        counts["venue_pages"] += 1
    venues_list = sorted(({**slist[0]["venue"], "count": sum(len(s["upcoming"]) for s in slist)} for slist in venue_series.values()), key=lambda v: (-v["count"], v["name"]))
    r.page("/venues/", "venues_index.html", title=f"Venues in Mobile, AL — {site.name}",
           description="Every venue we track across Mobile, the Eastern Shore, and Dauphin Island, with upcoming event counts.", venues=venues_list)

    # search: compact index of upcoming events + venues, and the results page
    idx = [{"y": "event", "t": o["title"], "v": o["venue"]["name"] if o["venue"] else o["venue_name_raw"], "c": o["city"],
            "d": o["day"].isoformat(), "w": f"{o['day']:%a %b %d}".replace(" 0", " "), "u": o["url"], "k": " ".join(o["category_labels"])}
           for o in site.upcoming]
    seen_series: set[str] = set()
    idx = [i for i in idx if not (i["u"] in seen_series or seen_series.add(i["u"]))]  # one entry per series (next date)
    idx += [{"y": "venue", "t": v["name"], "v": "", "c": v["city"], "d": "", "w": "", "u": v["url"], "k": "venue"} for v in venues_list]
    (out / "api" / "search.json").parent.mkdir(parents=True, exist_ok=True)
    (out / "api" / "search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    r.page("/search/", "search.html", title=f"Search — {site.name}", description="Search upcoming events and venues in Mobile, AL.", noindex=True, index=False)

    # standard pages
    about = site.pages.get("about", {})
    r.page("/about/", "page.html", title=f"About — {site.name}", description=(about.get("intro") or "")[:160], h1="About", body=_about_html(about, site),
           header_photo=about.get("header_photo"), header_alt=about.get("header_alt", ""), og_image=(site.url + about["header_photo"]) if about.get("header_photo") else None)
    r.redirects.append({"source": "/contact(/)?", "destination": "/about/", "permanent": True})
    r.page("/privacy/", "page.html", title=f"Privacy Policy — {site.name}", description="What this site collects (almost nothing) and who it shares it with.", h1="Privacy Policy", body=_privacy_html(site))
    r.page("/terms/", "page.html", title=f"Terms of Use — {site.name}", description="Terms for using this events calendar.", h1="Terms of Use", body=_terms_html(site))
    r.page("/404/", "404.html", title=f"Page not found — {site.name}", description="", noindex=True, index=False)
    shutil.move(out / "404" / "index.html", out / "404.html")
    shutil.rmtree(out / "404")

    # sitemap, robots, vercel.json
    (out / "sitemap.xml").write_text(_sitemap(site.url, r.urls), encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site.url}/sitemap.xml\n", encoding="utf-8")
    vercel_path.write_text(json.dumps(_vercel(r.redirects), indent=2) + "\n", encoding="utf-8")
    counts["urls"] = len(r.urls)
    return dict(counts)


def _sitemap(base: str, urls: list[tuple[str, str]]) -> str:
    items = "".join(f"  <url><loc>{base}{p}</loc><lastmod>{m}</lastmod></url>\n" for p, m in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}</urlset>\n'


def _vercel(redirects: list[dict]) -> dict:
    return {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "outputDirectory": "site",
        "buildCommand": "",
        "cleanUrls": True,
        "trailingSlash": True,
        "redirects": redirects,
        "headers": [
            # Kill duplicate hosts: platform domains get noindex. Fails OPEN — only known throwaway suffixes.
            {"source": "/(.*)", "has": [{"type": "host", "value": "(.*)\\.vercel\\.app"}],
             "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains"},
            ]},
        ],
    }


def _source_count(site: Site) -> str:
    """Automated sources + the hand-checked pages, rounded down to a 5 with a plus."""
    automated = [s for s in site.sources.values() if s["collector_type"] != "manual"]
    manual = next((s for s in site.sources.values() if s["collector_type"] == "manual"), None)
    pages = len((db.uj(manual["config"], {}) or {}).get("scanned_pages", [])) if manual else 0
    n = len(automated) + pages
    return f"{n - n % 5}+" if n >= 10 else str(n)


def _about_html(about: dict, site: Site) -> str:
    how = (about.get("how") or "").replace("{count}", _source_count(site))
    backstory = (about.get("backstory") or "")
    url = about.get("mobilebaynow_url", "https://mobilebaynow.com/")
    backstory = backstory.replace("MobileBayNow", f'<a href="{url}" target="_blank" rel="noopener">MobileBayNow<span class="sr-only"> (opens in new tab)</span></a>')
    photo = ""
    if about.get("photo"):
        photo = (f'<figure class="about-photo"><img src="{about["photo"]}" alt="{about.get("photo_alt", "")}" loading="lazy" width="1200" height="900">'
                 f'<figcaption>{about.get("photo_caption", "")}</figcaption></figure>')
    return f"""<p>{about.get('intro', '')}</p>
<p>{how}</p>
<h2>{about.get('backstory_title', 'The backstory')}</h2>
{photo}
<p>{backstory}</p>"""


def _privacy_html(site: Site) -> str:
    return f"""<p><em>Last updated: September 14, 2026</em></p>
<p>{site.name} is a static website. It does not have accounts, does not set cookies, and does not run advertising or third-party analytics scripts.</p>
<h2>What we collect</h2><p>Nothing directly. Our hosting provider (Vercel) logs standard server request data (IP address, user agent, requested page) for security and operations, retained per their policy.</p>
<h2>Contact</h2><p>If you contact us through brooksconkle.com, that site's privacy policy covers the message. We do not add you to any list.</p>
<h2>Third parties</h2><p>Outbound links go to venue websites, Ticketmaster, and other organizers. Their privacy policies apply once you leave this site.</p>
<p>Questions: <a href="https://www.brooksconkle.com/" target="_blank" rel="noopener">brooksconkle.com<span class="sr-only"> (opens in new tab)</span></a>.</p>"""


def _terms_html(site: Site) -> str:
    return f"""<p><em>Last updated: September 14, 2026</em></p>
<p>By using {site.name} you agree to these terms.</p>
<h2>Accuracy</h2><p>Listings are collected automatically from public sources and checked weekly. Dates, times, prices, and availability change. Always confirm with the venue or organizer before you go. We are not responsible for canceled, moved, or sold-out events.</p>
<h2>Tickets</h2><p>We do not sell tickets. Ticket links go to the venue, organizer, or Ticketmaster. Any purchase is between you and them.</p>
<h2>Content and attribution</h2><p>Event descriptions and images belong to their original publishers and are shown with a link to the source. If you own content shown here and want it removed or credited differently, reach us at <a href="https://www.brooksconkle.com/" target="_blank" rel="noopener">brooksconkle.com<span class="sr-only"> (opens in new tab)</span></a> and we will act within a week.</p>
<h2>Use of this site</h2><p>You may link to any page. Automated bulk copying of the listings is not permitted without permission.</p>
<h2>No warranty</h2><p>The site is provided as-is, without warranties of any kind. Our liability is limited to the fullest extent permitted by law.</p>
<h2>Changes</h2><p>We may update these terms; the date above reflects the latest change.</p>"""
