"""Keyword classifier into the seven site categories. Rules live in data/categories.yaml."""

from __future__ import annotations

import re
from functools import lru_cache

from . import config

CATEGORIES = ["music", "family", "food", "active", "sports", "arts", "community", "nightlife"]
MAX_CATEGORIES = 2


@lru_cache(maxsize=None)
def _rules() -> list[tuple[str, list[re.Pattern]]]:
    out = []
    for rule in config.categories().get("rules", []):
        pats = [re.compile(r"(?<![a-z0-9])" + re.escape(str(k).lower()) + r"(?![a-z0-9])") for k in rule["keywords"]]
        out.append((rule["category"], pats))
    return out


def classify_all(title: str, source_categories: list[str] | None = None, description: str = "") -> list[str]:
    """Up to MAX_CATEGORIES categories. Source categories are checked first (strong signal),
    then title, then description (weak). Rule order breaks ties within a text."""
    texts = [
        " ".join(source_categories or []).lower(),
        (title or "").lower(),
        (description or "")[:400].lower(),
    ]
    found: list[str] = []
    for text in texts:
        if not text.strip():
            continue
        for cat, pats in _rules():
            if cat not in found and any(p.search(text) for p in pats):
                found.append(cat)
                if len(found) >= MAX_CATEGORIES:
                    return found
    return found or [config.categories().get("default", "community")]


def classify(title: str, source_categories: list[str] | None = None, description: str = "") -> str:
    return classify_all(title, source_categories, description)[0]


def never_feature(title: str) -> bool:
    t = (title or "").lower()
    return any(str(k).lower() in t for k in config.categories().get("never_feature_keywords", []))
