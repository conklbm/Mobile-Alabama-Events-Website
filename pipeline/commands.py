"""Review commands, typed into a GitHub issue comment (usually by replying to the email).

    approve 73 79                      publish these ids as-is
    cancel 151 222                     confirm cancelled (removed from the site)
    not-cancelled 222                  the source was wrong; bring it back
    merge 271 269                      same event; keep 271, fold 269 into it
    never-merge 271 269                different events; stop asking
    alias "Nowhere Bar" = soul-kitchen add an alias to an existing venue (slug from /venues/<slug>/)
    venue statemint-pop-up "Statemint Mobile Pop Up" Mobile   create a new venue (slug, name, city)
    ignore 73                          leave it held; stop listing it in the issue

One command per line. Lines starting with '>' (quoted email) and everything after a
"On ... wrote:" line are ignored. YAML files are edited as text so comments survive.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import config, db, review
from .text import slugify

_QUOTE_RE = re.compile(r"^\s*>")
_WROTE_RE = re.compile(r"^\s*On .* wrote:\s*$|^\s*-- ?$|^\s*_{3,}\s*$|^\s*From: ")
_ALIAS_RE = re.compile(r'^alias\s+"(?P<name>[^"]+)"\s*=\s*(?P<slug>[a-z0-9-]+)\s*$', re.I)
_VENUE_RE = re.compile(r'^venue\s+(?P<slug>[a-z0-9-]+)\s+"(?P<name>[^"]+)"\s+(?P<city>"[^"]+"|\S+)\s*$', re.I)
_IDS_RE = re.compile(r"^(?P<verb>approve|cancel|not-cancelled|uncancel|merge|never-merge|ignore|hide)\s+(?P<ids>[\d\s,#]+)$", re.I)


@dataclass
class Command:
    verb: str
    ids: list[int] = field(default_factory=list)
    name: str = ""
    slug: str = ""
    city: str = ""
    raw: str = ""


@dataclass
class Result:
    ok: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    touched_files: set[str] = field(default_factory=set)

    @property
    def applied(self) -> bool:
        return bool(self.ok)


def parse(text: str) -> tuple[list[Command], list[str]]:
    """Returns (commands, unrecognized lines). Stops at the quoted-reply boundary."""
    cmds: list[Command] = []
    unknown: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or _QUOTE_RE.match(raw):
            continue
        if _WROTE_RE.match(line):
            break
        if line.startswith("<!--"):
            continue
        m = _ALIAS_RE.match(line)
        if m:
            cmds.append(Command("alias", name=m["name"].strip(), slug=m["slug"].lower(), raw=line))
            continue
        m = _VENUE_RE.match(line)
        if m:
            cmds.append(Command("venue", slug=m["slug"].lower(), name=m["name"].strip(), city=m["city"].strip('"'), raw=line))
            continue
        m = _IDS_RE.match(line)
        if m:
            ids = [int(x) for x in re.findall(r"\d+", m["ids"])]
            verb = m["verb"].lower().replace("uncancel", "not-cancelled").replace("hide", "ignore")
            if ids:
                cmds.append(Command(verb, ids=ids, raw=line))
                continue
        unknown.append(line)
    return cmds, unknown


# ---------- text-level YAML edits (comments and ordering survive) ----------

def _add_to_list(text: str, key: str, item: str) -> str:
    """Append `item` to the top-level list `key` in overrides.yaml, flow or block style."""
    flow = re.search(rf"^(?P<k>{re.escape(key)}:\s*)\[(?P<body>[^\]]*)\]\s*(?P<c>#.*)?$", text, re.M)
    if flow:
        body = flow["body"].strip()
        new_body = f"{body}, {item}" if body else item
        line = f"{flow['k']}[{new_body}]" + (f"  {flow['c']}" if flow["c"] else "")
        return text[: flow.start()] + line + text[flow.end():]
    block = re.search(rf"^{re.escape(key)}:\s*(#.*)?$", text, re.M)
    if block:
        # insert after the last "  - " line that follows the key
        pos = block.end()
        rest = text[pos:]
        m = re.match(r"(\n(?:\s*#.*|\s+- .*|\s*)\n?)*", rest)
        end = pos + (m.end() if m else 0)
        # back up over trailing blank lines so the new item sits with the list
        while end > pos and text[end - 1] == "\n" and text[end - 2:end] == "\n\n":
            end -= 1
        return text[:end].rstrip("\n") + f"\n  - {item}\n" + text[end:].lstrip("\n")
    return text.rstrip("\n") + f"\n{key}:\n  - {item}\n"


def _add_alias(text: str, slug: str, alias: str) -> str | None:
    """Insert alias into the venue block for `slug`. None if the slug isn't in the file."""
    m = re.search(rf"^- slug: {re.escape(slug)}\s*$", text, re.M)
    if not m:
        return None
    block_end = text.find("\n- slug:", m.end())
    block = text[m.start(): block_end if block_end != -1 else len(text)]
    am = re.search(r"^(?P<k>\s*aliases:\s*)\[(?P<body>[^\]]*)\]\s*$", block, re.M)
    q = '"' + alias.replace('"', "'") + '"'
    if am:
        body = am["body"].strip()
        if alias.lower() in [a.strip().strip('"\'').lower() for a in body.split(",") if a.strip()]:
            return text  # already there
        new = f"{am['k']}[{body + ', ' if body else ''}{q}]"
        block2 = block[: am.start()] + new + block[am.end():]
    else:
        block2 = block.rstrip("\n") + f"\n  aliases: [{q}]\n"
    return text[: m.start()] + block2 + text[m.start() + len(block):]


def _venue_block(slug: str, name: str, city: str) -> str:
    return (f"\n- slug: {slug}\n  name: {name}\n  aliases: [\"{name}\"]\n  domains: []\n"
            f"  city: {city}\n  state: AL\n  regions: [mobile]\n")


# ---------- apply ----------

def apply(text: str, conn: sqlite3.Connection, data_dir: Path | None = None) -> Result:
    data_dir = data_dir or config.DATA
    ov_path, v_path = data_dir / "overrides.yaml", data_dir / "venues.yaml"
    ov = ov_path.read_text(encoding="utf-8")
    venues = v_path.read_text(encoding="utf-8")
    res = Result()
    cmds, unknown = parse(text)
    for u in unknown:
        res.errors.append(f"didn't understand: `{u}`")
    known_ids = {r[0] for r in conn.execute("SELECT id FROM occurrences")}
    known_slugs = set(re.findall(r"^- slug: ([a-z0-9-]+)\s*$", venues, re.M))

    for c in cmds:
        bad = [i for i in c.ids if i not in known_ids]
        if bad:
            res.errors.append(f"`{c.raw}`: no event with id {', '.join(f'#{i}' for i in bad)}")
            continue
        if c.verb == "approve":
            n = review.approve(conn, ids=c.ids)
            res.ok.append(f"approved {', '.join(f'#{i}' for i in c.ids)} ({n} published)")
        elif c.verb == "cancel":
            for i in c.ids:
                ov = _add_to_list(ov, "cancelled", str(i))
            res.ok.append(f"cancelled {', '.join(f'#{i}' for i in c.ids)}")
            res.touched_files.add("overrides.yaml")
        elif c.verb == "not-cancelled":
            for i in c.ids:
                ov = _add_to_list(ov, "not_cancelled", str(i))
            res.ok.append(f"un-cancelled {', '.join(f'#{i}' for i in c.ids)}")
            res.touched_files.add("overrides.yaml")
        elif c.verb in ("merge", "never-merge"):
            if len(c.ids) != 2:
                res.errors.append(f"`{c.raw}`: needs exactly two ids")
                continue
            key = "merge" if c.verb == "merge" else "never_merge"
            ov = _add_to_list(ov, key, f"[{c.ids[0]}, {c.ids[1]}]")
            res.ok.append(f"{c.verb} #{c.ids[0]} ↔ #{c.ids[1]}")
            res.touched_files.add("overrides.yaml")
        elif c.verb == "ignore":
            now = db.now_iso()
            for i in c.ids:
                conn.execute("UPDATE review_queue SET resolved_at=? WHERE occurrence_id=? AND resolved_at IS NULL", (now, i))
            conn.commit()
            res.ok.append(f"ignored {', '.join(f'#{i}' for i in c.ids)} (stays hidden, out of the issue)")
        elif c.verb == "alias":
            if c.slug not in known_slugs:
                res.errors.append(f"`{c.raw}`: no venue with slug `{c.slug}` (see /venues/ or use `venue {c.slug} \"Name\" City` first)")
                continue
            new = _add_alias(venues, c.slug, c.name)
            if new is None:
                res.errors.append(f"`{c.raw}`: could not edit venue `{c.slug}`")
                continue
            venues = new
            res.ok.append(f"alias \"{c.name}\" → {c.slug}")
            res.touched_files.add("venues.yaml")
        elif c.verb == "venue":
            if c.slug in known_slugs:
                res.errors.append(f"`{c.raw}`: venue `{c.slug}` already exists; use `alias` instead")
                continue
            venues = venues.rstrip("\n") + "\n" + _venue_block(c.slug, c.name, c.city)
            known_slugs.add(c.slug)
            res.ok.append(f"new venue {c.slug} (\"{c.name}\", {c.city})")
            res.touched_files.add("venues.yaml")
    if "overrides.yaml" in res.touched_files:
        ov_path.write_text(ov, encoding="utf-8")
    if "venues.yaml" in res.touched_files:
        v_path.write_text(venues, encoding="utf-8")
    return res


def report(res: Result) -> str:
    lines = ["<!-- bot -->"]
    if res.ok:
        lines += ["Applied:", *[f"- {x}" for x in res.ok]]
    if res.errors:
        lines += ["", "Couldn't apply:", *[f"- {x}" for x in res.errors]]
    if not res.ok and not res.errors:
        lines.append("No commands found in that comment. One per line, e.g. `approve 73` or `alias \"Some Venue\" = venue-slug`.")
    return "\n".join(lines)
