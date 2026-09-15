"""Standalone entity-resolution module.

Collapse N messy records describing one real-world thing, and decide which
source wins per field. The schema is passed in, not baked in, so the next
project (license records vs. websites, vendor SKUs, duplicate CRM contacts)
imports this instead of rewriting it.

    from pipeline.matcher import Matcher, MatchSchema

    schema = MatchSchema(
        text_of=lambda r: r["title"],
        bucket_of=lambda r: (r["day"], r["venue"]),
        rank_of=lambda r: (TIER_RANK[r["tier"]],),   # lower wins
        field_rules={"description": "longest", "image": "first_nonempty"},
    )
    m = Matcher(schema)
    result = m.best(new_record, existing_records)   # MatchResult(decision, candidate, score)
    merged = m.merge([rec_a, rec_b])                 # source-priority merge
    groups = m.cluster(records)                      # dedup a whole set at once
"""

from .core import MatchResult, MatchSchema, Matcher

__all__ = ["Matcher", "MatchSchema", "MatchResult"]
