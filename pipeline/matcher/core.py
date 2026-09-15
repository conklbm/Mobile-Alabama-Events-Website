from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Literal

from rapidfuzz import fuzz

Decision = Literal["match", "ambiguous", "new"]

# How to pick a field's value across records ordered by rank (best first).
#   priority       -> first record's value, even if empty (rarely what you want)
#   first_nonempty -> first record (by rank) with a truthy value          (default)
#   longest        -> the longest truthy value (descriptions)
#   max / min      -> numeric extremes
#   union          -> merged list, order-preserving, deduped
#   any            -> True if any record has a truthy value
FieldRule = Literal["priority", "first_nonempty", "longest", "max", "min", "union", "any"]


@dataclass
class MatchSchema:
    text_of: Callable[[dict], str]
    bucket_of: Callable[[dict], Hashable] = lambda r: None
    rank_of: Callable[[dict], tuple] = lambda r: (0,)
    match_threshold: float = 82.0
    ambiguous_floor: float = 70.0
    scorer: Callable[[str, str], float] = fuzz.token_set_ratio
    field_rules: dict[str, FieldRule] = field(default_factory=dict)
    default_rule: FieldRule = "first_nonempty"
    # optional hard veto: return True to forbid a match regardless of score
    veto: Callable[[dict, dict], bool] = lambda a, b: False


@dataclass
class MatchResult:
    decision: Decision
    candidate: dict | None
    score: float
    runner_up: float = 0.0


class Matcher:
    def __init__(self, schema: MatchSchema):
        self.s = schema

    # ---------- matching ----------

    def score(self, a: dict, b: dict) -> float:
        ta, tb = self.s.text_of(a) or "", self.s.text_of(b) or ""
        if not ta or not tb:
            return 0.0
        return float(self.s.scorer(ta, tb))

    def best(self, record: dict, candidates: Iterable[dict]) -> MatchResult:
        """Compare one record against candidates in the same bucket."""
        bucket = self.s.bucket_of(record)
        scored: list[tuple[float, dict]] = []
        for c in candidates:
            if self.s.bucket_of(c) != bucket:
                continue
            if self.s.veto(record, c):
                continue
            scored.append((self.score(record, c), c))
        if not scored:
            return MatchResult("new", None, 0.0)
        scored.sort(key=lambda t: -t[0])
        top, cand = scored[0]
        runner = scored[1][0] if len(scored) > 1 else 0.0
        if top >= self.s.match_threshold:
            return MatchResult("match", cand, top, runner)
        if top >= self.s.ambiguous_floor:
            return MatchResult("ambiguous", cand, top, runner)
        return MatchResult("new", None, top, runner)

    def cluster(self, records: Iterable[dict]) -> list[list[dict]]:
        """Greedy single-link clustering within buckets. Ambiguous pairs stay separate."""
        by_bucket: dict[Hashable, list[dict]] = defaultdict(list)
        for r in records:
            by_bucket[self.s.bucket_of(r)].append(r)
        groups: list[list[dict]] = []
        for items in by_bucket.values():
            local: list[list[dict]] = []
            for r in items:
                placed = False
                for g in local:
                    if any(not self.s.veto(r, o) and self.score(r, o) >= self.s.match_threshold for o in g):
                        g.append(r)
                        placed = True
                        break
                if not placed:
                    local.append([r])
            groups.extend(local)
        return groups

    # ---------- merging ----------

    def merge(self, records: list[dict]) -> dict:
        """Source-priority merge. Records sorted by rank (best first); per-field rules decide."""
        if not records:
            return {}
        ordered = sorted(records, key=self.s.rank_of)
        keys: list[str] = []
        for r in ordered:
            for k in r:
                if k not in keys:
                    keys.append(k)
        out: dict[str, Any] = {}
        for k in keys:
            rule = self.s.field_rules.get(k, self.s.default_rule)
            values = [r.get(k) for r in ordered]
            out[k] = _apply(rule, values)
        return out

    def winner(self, records: list[dict]) -> dict:
        """The single highest-ranked record (useful for 'primary source' at render time)."""
        return min(records, key=self.s.rank_of)


def _apply(rule: FieldRule, values: list[Any]) -> Any:
    if rule == "priority":
        return values[0]
    if rule == "first_nonempty":
        for v in values:
            if v not in (None, "", [], {}):
                return v
        return values[0]
    if rule == "longest":
        best = None
        for v in values:
            if v not in (None, "", [], {}) and (best is None or len(str(v)) > len(str(best))):
                best = v
        return best if best is not None else values[0]
    if rule in ("max", "min"):
        nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if not nums:
            return values[0]
        return max(nums) if rule == "max" else min(nums)
    if rule == "union":
        seen: list[Any] = []
        for v in values:
            for item in (v if isinstance(v, (list, tuple, set)) else ([v] if v not in (None, "") else [])):
                if item not in seen:
                    seen.append(item)
        return seen
    if rule == "any":
        return any(bool(v) for v in values)
    raise ValueError(f"unknown field rule {rule!r}")
