"""Shared time model (WP10; spec: docs/expansion/02_ontology_and_data.md section 4, D033).

Semantics fixed by D033:

* ``[t_low, t_high]`` bounds the *uncertainty* about one event's date (aoristic
  reading), not a duration.
* Inputs are historical years CE: BCE negative, **no year 0**. All arithmetic is
  done in astronomical years (1 BCE = 0, 2 BCE = -1).
* Bounds are inclusive: ``|A| = a_high - a_low + 1``. (1 BCE, 1 CE) spans 2 years.
* Overlap join: pairs with ``|A∩B| > 0``; reports ``overlap_frac = |A∩B| / |A|``
  (asymmetric aoristic weight) and ``jaccard = |A∩B| / |A∪B|``.
* Containment join: ``B.low <= A.low`` and ``A.high <= B.high`` (inclusive; equal
  intervals count).
* Lag join: ``0 <= B.low - A.high <= k``, inclusive at both ends.
* Monte Carlo: uniform integer draws within each interval, seeded (default 42).
* Circular dating: following ``dating_dependency`` links over a chain of any
  length reaches the other side of the join, or returns to itself.

Fractions are exact (``fractions.Fraction``), as in :mod:`romeco.units`.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

#: Allowed ``t_resolution`` values (spec section 4 table).
RESOLUTIONS: frozenset[str] = frozenset(
    {"day", "month", "season", "year", "regnal_year", "decade", "generation", "century", "phase"}
)

#: Default Monte Carlo seed (D033).
DEFAULT_SEED: int = 42


# --------------------------------------------------------------------------- years


def to_astronomical(year: int) -> int:
    """Convert a historical year (CE positive, BCE negative, no year 0) to astronomical.

    1 BCE (-1) -> 0, 2 BCE (-2) -> -1, 1 CE (1) -> 1.
    """
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError(f"year must be int, got {type(year).__name__}")
    if year == 0:
        raise ValueError("historical year 0 does not exist (1 BCE is followed by 1 CE)")
    return year + 1 if year < 0 else year


def from_astronomical(year: int) -> int:
    """Convert an astronomical year back to historical (no year 0)."""
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError(f"year must be int, got {type(year).__name__}")
    return year - 1 if year <= 0 else year


# ----------------------------------------------------------------------- interval


@dataclass(frozen=True)
class Interval:
    """A dated record's time interval.

    ``t_low``/``t_high`` are historical years (no year 0) bounding the uncertainty
    about a single event's date. ``record_origin`` marks synthetic/simulated rows.
    """

    record_id: str
    t_low: int
    t_high: int
    t_resolution: str = "year"
    dating_method: str | None = None
    calendar_source: str | None = None
    dating_dependency: str | None = None
    record_origin: str | None = None

    def __post_init__(self) -> None:
        lo, hi = to_astronomical(self.t_low), to_astronomical(self.t_high)
        if lo > hi:
            raise ValueError(f"{self.record_id}: t_low {self.t_low} is after t_high {self.t_high}")
        if self.t_resolution not in RESOLUTIONS:
            raise ValueError(f"{self.record_id}: unknown t_resolution {self.t_resolution!r}")

    @property
    def a_low(self) -> int:
        """Lower bound in astronomical years."""
        return to_astronomical(self.t_low)

    @property
    def a_high(self) -> int:
        """Upper bound in astronomical years."""
        return to_astronomical(self.t_high)

    @property
    def length(self) -> int:
        """Number of whole years in the interval (inclusive bounds)."""
        return self.a_high - self.a_low + 1


def intersection_years(a: Interval, b: Interval) -> int:
    """``|A∩B|`` in whole years (0 if disjoint)."""
    return max(0, min(a.a_high, b.a_high) - max(a.a_low, b.a_low) + 1)


def overlap_frac(a: Interval, b: Interval) -> Fraction:
    """``|A∩B| / |A|``: under uniform uncertainty, P(A's date falls in B)."""
    return Fraction(intersection_years(a, b), a.length)


def jaccard(a: Interval, b: Interval) -> Fraction:
    """``|A∩B| / |A∪B|`` (symmetric)."""
    inter = intersection_years(a, b)
    return Fraction(inter, a.length + b.length - inter)


def is_contained(a: Interval, b: Interval) -> bool:
    """A inside B, inclusive (equal intervals count)."""
    return b.a_low <= a.a_low and a.a_high <= b.a_high


def lag_years(a: Interval, b: Interval) -> int:
    """``B.low - A.high`` in astronomical years (may be negative)."""
    return b.a_low - a.a_high


# --------------------------------------------------------------------------- joins


@dataclass(frozen=True)
class OverlapPair:
    a_id: str
    b_id: str
    overlap_years: int
    overlap_frac: Fraction
    jaccard: Fraction


@dataclass(frozen=True)
class ContainmentPair:
    a_id: str
    b_id: str


@dataclass(frozen=True)
class LagPair:
    a_id: str
    b_id: str
    lag: int


def overlap_join(left: Iterable[Interval], right: Iterable[Interval]) -> list[OverlapPair]:
    """All pairs (A in left, B in right) with ``|A∩B| > 0``."""
    rights = list(right)
    out: list[OverlapPair] = []
    for a in left:
        for b in rights:
            inter = intersection_years(a, b)
            if inter > 0:
                out.append(OverlapPair(a.record_id, b.record_id, inter, overlap_frac(a, b), jaccard(a, b)))
    return out


def containment_join(left: Iterable[Interval], right: Iterable[Interval]) -> list[ContainmentPair]:
    """All pairs (A in left, B in right) with A inside B (inclusive)."""
    rights = list(right)
    return [ContainmentPair(a.record_id, b.record_id) for a in left for b in rights if is_contained(a, b)]


def lag_join(left: Iterable[Interval], right: Iterable[Interval], k: int) -> list[LagPair]:
    """All pairs (A in left, B in right) with ``0 <= B.low - A.high <= k``."""
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise ValueError(f"k must be a non-negative int, got {k!r}")
    rights = list(right)
    out: list[LagPair] = []
    for a in left:
        for b in rights:
            lag = lag_years(a, b)
            if 0 <= lag <= k:
                out.append(LagPair(a.record_id, b.record_id, lag))
    return out


# ---------------------------------------------------------------- circular dating


def is_circular(record_id: str, dependencies: Mapping[str, str | None], other_side: Iterable[str] = ()) -> bool:
    """True if following ``dating_dependency`` links from ``record_id`` reaches
    ``other_side`` or returns to ``record_id``, over a chain of any length.

    A chain that enters a cycle not containing ``record_id`` (A -> C -> D -> C) is
    also treated as circular, since A's date then rests on a circularly dated claim.
    Dangling links (dependency ID with no entry in ``dependencies``) end the chain.
    """
    targets = set(other_side)
    seen: set[str] = set()
    node = dependencies.get(record_id)
    while node is not None:
        if node == record_id or node in targets or node in seen:
            return True
        seen.add(node)
        node = dependencies.get(node)
    return False


def circular_records(left: Sequence[Interval], right: Sequence[Interval],
                     extra_dependencies: Mapping[str, str | None] | None = None) -> set[str]:
    """IDs of records on either side of a join that are circularly dated.

    ``extra_dependencies`` adds links for claims that are not themselves in the join.
    """
    deps: dict[str, str | None] = dict(extra_dependencies or {})
    for iv in (*left, *right):
        deps[iv.record_id] = iv.dating_dependency
    left_ids = {iv.record_id for iv in left}
    right_ids = {iv.record_id for iv in right}
    out = {iv.record_id for iv in left if is_circular(iv.record_id, deps, right_ids)}
    out |= {iv.record_id for iv in right if is_circular(iv.record_id, deps, left_ids)}
    return out


# --------------------------------------------------------------------- Monte Carlo


@dataclass(frozen=True)
class MonteCarloResult:
    """Values of a statistic over dating draws. Draws are simulated data."""

    seed: int
    n_draws: int
    values: tuple[Any, ...]
    excluded: frozenset[str] = field(default_factory=frozenset)
    record_origin: str = "simulated"


def draw_dates(intervals: Sequence[Interval], rng: random.Random) -> dict[str, int]:
    """One uniform integer draw (astronomical year) per interval, in input order."""
    return {iv.record_id: rng.randint(iv.a_low, iv.a_high) for iv in intervals}


def monte_carlo(intervals: Sequence[Interval], statistic: Callable[[dict[str, int]], Any],
                n_draws: int, seed: int = DEFAULT_SEED,
                exclude: Iterable[str] = ()) -> MonteCarloResult:
    """Resample dates uniformly within their intervals and evaluate ``statistic``.

    ``statistic`` receives ``{record_id: astronomical_year}`` per draw. Records in
    ``exclude`` (e.g. from :func:`circular_records`) are dropped before sampling.
    Reproducible for a fixed seed and input order.
    """
    if not isinstance(n_draws, int) or n_draws < 1:
        raise ValueError(f"n_draws must be a positive int, got {n_draws!r}")
    excluded = frozenset(exclude)
    kept = [iv for iv in intervals if iv.record_id not in excluded]
    rng = random.Random(seed)
    values = tuple(statistic(draw_dates(kept, rng)) for _ in range(n_draws))
    return MonteCarloResult(seed=seed, n_draws=n_draws, values=values, excluded=excluded)
