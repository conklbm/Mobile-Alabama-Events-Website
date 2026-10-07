"""92ZEW's "Weekend Rundown" posts: an editor's pick of the weekend, many of them missing from every calendar.

Each post is a WordPress article, one event per paragraph:
    <p><strong>EVENT NAME-</strong> Saturday, 9am-2pm, Venue Name, City. Description... <a>INFO HERE</a></p>
with bare <strong>FRIDAY:</strong> paragraphs as section headers. We read the newest few posts through the
WP REST API and keep only items we can place: a weekday, a start time, and a location in our area.
Anything else (TV listings for away games, Mississippi concerts, "various locations", weather
reschedules) is skipped, not guessed.
"""

from __future__ import annotations

import html
import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from ..dates import DEFAULT_TZ
from ..models import RawEvent
from ..text import clean_title, slugify, strip_html, tame_caps
from .base import Collector, log

_DAYS = {"mon": 0, "monday": 0, "tue": 1, "tues": 1, "tuesday": 1, "wed": 2, "weds": 2, "wednesday": 2,
         "thu": 3, "thur": 3, "thurs": 3, "thursday": 3, "fri": 4, "friday": 4, "sat": 5, "saturday": 5,
         "sun": 6, "sunday": 6}
_DAY_RE = re.compile(r"\b(" + "|".join(sorted(_DAYS, key=len, reverse=True)) + r")\b\.?", re.I)
_T = r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.|noon)?"
_TIME_RE = re.compile(_T + r"(?:\s*(?:-|–|to)\s*" + _T + r")?", re.I)
_STATUS_RE = re.compile(r"reschedul|postpon|cancel", re.I)
_LINK_WORDS_RE = re.compile(r"\b(click|info|tickets?|more info)\s+here\b", re.I)
_ABBR = {"mt", "st", "ave", "dr", "blvd", "rd", "hwy", "jr", "sr", "a.m", "p.m", "ft"}
_P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.S | re.I)
_LEAD_STRONG_RE = re.compile(r"^\s*<(strong|b)>(.*?)</\1>(.*)$", re.S | re.I)
_HREF_RE = re.compile(r'href="([^"]+)"', re.I)
_TV_RE = re.compile(r"^(espn\S*|abc|cbs|nbc|fox|sec network|acc network|cw|tv)$", re.I)


def _text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ")).strip()


def _first_sentence(s: str) -> tuple[str, str]:
    """Split 'Saturday, 9am, Coastal Cafe, Daphne.Join us for...' at the first real sentence end."""
    for m in re.finditer(r"\.(?=\s+[A-Z]|[A-Z][a-z])", s):
        word = re.split(r"[\s,;]", s[: m.start()])[-1].lower()
        if word not in _ABBR and not re.fullmatch(r"[a-z]", word):
            return s[: m.start()].strip(), s[m.end():].strip()
    return s.strip().rstrip("."), ""


def _clock(h: str, m: str | None, ap: str | None, default_ap: str | None) -> time | None:
    ap = (ap or default_ap or "").lower().replace(".", "")
    if ap == "noon":
        return time(12, int(m or 0))
    if ap not in ("am", "pm"):
        return None
    hour = int(h) % 12 + (12 if ap == "pm" else 0)
    return time(hour, int(m or 0)) if hour < 24 else None


def _times(token: str) -> tuple[time | None, time | None]:
    m = _TIME_RE.search(token)
    if not m or not (m[3] or m[6]):
        return None, None
    start = _clock(m[1], m[2], m[3], m[6])  # "7-8:30pm": the start borrows the end's pm
    end = _clock(m[4], m[5], m[6], None) if m[4] else None
    return start, end


def _days(token: str) -> list[int]:
    """'Friday and Saturday' -> [4, 5]; 'Thurs/Fri/Sat' -> [3, 4, 5]; 'Tues-Sat' -> [1..5]."""
    found = [(_DAYS[m[1].lower()], m.start(), m.end()) for m in _DAY_RE.finditer(token)]
    if len(found) == 2 and re.fullmatch(r"\s*[-–]\s*", token[found[0][2]:found[1][1]]):
        a, b = found[0][0], found[1][0]
        return [(a + i) % 7 for i in range((b - a) % 7 + 1)]
    return [d for d, _, _ in found]


class ZewRundownCollector(Collector):
    collector_type = "zew_rundown"

    def fetch(self, start: date, end: date) -> list[RawEvent]:
        api = self.source["url"].rstrip("/") + "/wp-json/wp/v2/posts"
        posts = self.get_json(api, {"search": "Weekend Rundown", "per_page": int(self.cfg.get("posts", 3)),
                                    "_fields": "id,date,link,title,content"})
        out: dict[str, RawEvent] = {}
        for p in posts:
            if "rundown" not in _text(p["title"]["rendered"]).lower():
                continue
            for ev in self.parse_post(p["content"]["rendered"], date.fromisoformat(p["date"][:10]), p["link"], start, end):
                out.setdefault(ev.external_id, ev)  # newest post wins; items repeat under each day heading
        return list(out.values())

    def parse_post(self, content: str, posted: date, link: str, start: date, end: date) -> list[RawEvent]:
        z = ZoneInfo(DEFAULT_TZ)
        local = [w.lower() for w in self.cfg.get("local_places", [])]
        away = [w.lower() for w in self.cfg.get("away_places", [])]
        max_days = int(self.cfg.get("max_days_per_item", 3))
        anchor = posted - timedelta(days=1)  # a Wednesday post's "Tuesday" is yesterday, not next week
        section_days: list[int] = []
        out: list[RawEvent] = []
        for para in _P_RE.findall(content):
            m = _LEAD_STRONG_RE.match(para)
            if not m:
                continue
            name = clean_title(_text(m[2])).rstrip(" -–:;")
            rest = _text(m[3]).lstrip(" -–:;")
            if not re.sub(r"[\W_]", "", rest):  # a bare <strong>FRIDAY:</strong> section header
                section_days = _days(name)
                continue
            if _STATUS_RE.search(_text(para)):
                continue  # weather reschedules: the new date is in prose, not worth guessing
            loc, desc = _first_sentence(_LINK_WORDS_RE.sub("", rest))
            groups: list[tuple[list[int], time | None, time | None]] = []
            places: list[str] = []
            for tok in (t.strip() for t in re.split(r"[;,]", loc)):
                if not tok or re.fullmatch(r"\(.*\)", tok):
                    continue
                days = _days(tok)
                st, et = _times(tok)
                if days:
                    groups.append((days, st, et))
                elif st and groups and groups[-1][1] is None:
                    groups[-1] = (groups[-1][0], st, et)
                elif st and not groups and section_days:
                    groups.append((section_days, st, et))
                elif not st and not _TV_RE.match(tok):
                    places.append(tok)
            if not places and desc:
                # "Friday, 8:30PM. Electric Piano Parlor, Mobile": the place got its own sentence
                nxt, _ = _first_sentence(desc)
                if len(nxt) < 80 and not _days(nxt):
                    places = [t.strip() for t in re.split(r"[;,]", nxt) if t.strip()]
            from_name = not places and " @ " in name
            if from_name:
                places = [name.split(" @ ", 1)[1]]  # "MUSIC BINGO @ MUSIC MATRIX": the venue resolver decides
            where = ", ".join(places).lower()
            if not places or any(w in where for w in away) or (local and not from_name and not any(w in where for w in local)):
                continue  # TV listings for away games, out-of-area shows, "various locations"
            hrefs = _HREF_RE.findall(para)
            url = html.unescape(hrefs[0]) if hrefs else link
            title = tame_caps(name)
            for days, st, et in groups:
                if st is None or len(days) > max_days:
                    continue  # no start time, or an ongoing exhibition ("Tues-Sat 10am")
                for wd in days:
                    d = anchor + timedelta(days=(wd - anchor.weekday()) % 7)
                    if d < start or d > end:
                        continue
                    s = datetime.combine(d, st, tzinfo=z)
                    fin = datetime.combine(d, et, tzinfo=z) if et else None
                    out.append(RawEvent(
                        source_id=self.source["id"],
                        external_id=f"{slugify(name)}:{d.isoformat()}",
                        title=title,
                        start_local=s,
                        end_local=fin if fin and fin > s else None,
                        timezone=DEFAULT_TZ,
                        venue_name=places[0],
                        venue_address=", ".join(places),
                        city=places[-1] if len(places) > 1 else "",
                        description=strip_html(desc),
                        info_url=url,
                        website=url if hrefs else "",
                        raw={"post": link, "item": _text(para)},
                    ))
        if not out:
            log.info("zew_rundown: no upcoming items in %s", link)
        return out
