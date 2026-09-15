"""Text normalization helpers: HTML stripping, slugs, fuzzy-ready keys."""

from __future__ import annotations

import html
import re
import unicodedata

_TAG_RE = re.compile(r"<[^>]+>")
_SHORTCODE_RE = re.compile(r"\[/?[a-zA-Z_][\w-]*(?:\s[^\]]*)?\]")
_WS_RE = re.compile(r"\s+")
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_NOISE_RE = re.compile(r"[^a-z0-9 ]+")

# Words that add nothing to a title match ("Live at", "presents", "w/ special guests"...)
_TITLE_NOISE = re.compile(
    r"\b(presents?|featuring|feat\.?|ft\.?|w/|with special guests?|live|tour|the|a|an|and|&|at|in|on|of|"
    r"tickets?|show|event|night|free|\d{4})\b",
    re.I,
)


def strip_html(s: str | None) -> str:
    if not s:
        return ""
    s = _TAG_RE.sub(" ", s)
    s = _SHORTCODE_RE.sub(" ", s)
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    return _WS_RE.sub(" ", s).strip()


def clean_title(s: str | None) -> str:
    s = strip_html(s)
    return s.strip(" -–—|:")


def norm_key(s: str | None) -> str:
    """Lowercase, ascii, punctuation-free key for exact-ish comparisons."""
    if not s:
        return ""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " and ")
    s = _NOISE_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def title_key(s: str | None) -> str:
    """Aggressive title normalization for fuzzy matching."""
    k = norm_key(clean_title(s))
    k = _TITLE_NOISE.sub(" ", k)
    return _WS_RE.sub(" ", k).strip()


def slugify(s: str | None, max_len: int = 70) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = _SLUG_RE.sub("-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0]
    return s or "event"


def excerpt(s: str | None, n: int = 160) -> str:
    s = strip_html(s)
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def domain_of(url: str | None) -> str:
    if not url:
        return ""
    m = re.match(r"^(?:https?://)?(?:www\.)?([^/:?#]+)", url.strip(), re.I)
    return m.group(1).lower() if m else ""


def is_free_price(price: str | None) -> bool:
    if not price:
        return False
    p = price.strip().lower()
    return p in {"free", "$0", "0", "$0.00", "no cover", "free admission"} or p.startswith("free")
