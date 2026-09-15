"""Keyword classifier into the seven site categories. Rules live in data/categories.yaml."""

from __future__ import annotations

import re
from functools import lru_cache

from . import config

CATEGORIES = ["music", "family", "food", "arts", "sports", "community", "nightlife"]


@lru_cache(maxsize=None)
def _rules() -> list[tuple[str, list[re.Pattern]]]:
    out = []
    for rule in config.categories().get("rules", []):
        pats = [re.compile(r"(?<![a-z0-9])" + re.escape(str(k).lower()) + r"(?![a-z0-9])") for k in rule["keywords"]]
        out.append((rule["category"], pats))
    return out


def classify(title: str, source_categories: list[str] | None = None, description: str = "") -> str:
    """Source categories are checked first (strong signal), then title, then description (weak)."""
    texts = [
        " ".join(source_categories or []).lower(),
        (title or "").lower(),
        (description or "")[:400].lower(),
    ]
    for text in texts:
        if not text.strip():
            continue
        for cat, pats in _rules():
            if any(p.search(text) for p in pats):
                return cat
    return config.categories().get("default", "community")


def never_feature(title: str) -> bool:
    t = (title or "").lower()
    return any(str(k).lower() in t for k in config.categories().get("never_feature_keywords", []))
