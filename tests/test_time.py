"""Tests for romeco.time (T-WP10-001; spec 02_ontology_and_data.md section 4, D033).

All intervals here are planted test fixtures: record_origin = "synthetic".
"""

from fractions import Fraction

import pytest

from romeco.time import (
    DEFAULT_SEED,
    Interval,
    circular_records,
    containment_join,
    from_astronomical,
    is_circular,
    jaccard,
    lag_join,
    monte_carlo,
    overlap_frac,
    overlap_join,
    to_astronomical,
)

SYN = "synthetic"


def iv(rid: str, lo: int, hi: int, dep: str | None = None) -> Interval:
    return Interval(rid, lo, hi, dating_dependency=dep, record_origin=SYN)


# ---------------------------------------------------------------- conversion


def test_astronomical_conversion_acceptance():
    assert to_astronomical(-1) == 0  # 1 BCE
    assert to_astronomical(1) == 1  # 1 CE
    assert to_astronomical(-2) == -1  # 2 BCE
    assert iv("A", -1, 1).length == 2  # (1 BCE, 1 CE) spans 2 years, not 3


def test_year_zero_rejected():
    with pytest.raises(ValueError):
        to_astronomical(0)
    with pytest.raises(ValueError):
        iv("A", 0, 5)


@pytest.mark.parametrize("year", [-500, -2, -1, 1, 2, 14, 476])
def test_roundtrip(year):
    assert from_astronomical(to_astronomical(year)) == year


def test_interval_validation():
    with pytest.raises(ValueError):
        iv("A", 10, 5)
    with pytest.raises(ValueError):
        Interval("A", 1, 2, t_resolution="fortnight", record_origin=SYN)
    assert iv("A", 5, 5).length == 1


# ---------------------------------------------------------------------- joins


def test_overlap_frac_and_jaccard():
    a, b = iv("A", 1, 10), iv("B", 6, 25)  # |A|=10, |B|=20, |A∩B|=5, |A∪B|=25
    assert overlap_frac(a, b) == Fraction(1, 2)
    assert overlap_frac(b, a) == Fraction(1, 4)  # asymmetric
    assert jaccard(a, b) == jaccard(b, a) == Fraction(1, 5)


def test_overlap_across_bce_ce():
    a, b = iv("A", -10, -1), iv("B", -1, 5)  # astro A=[-9,0], B=[0,5]
    (pair,) = overlap_join([a], [b])
    assert pair.overlap_years == 1
    assert pair.overlap_frac == Fraction(1, 10)
    assert pair.jaccard == Fraction(1, 10 + 6 - 1)


def test_overlap_join_excludes_disjoint_and_adjacent():
    a = iv("A", 1, 10)
    assert overlap_join([a], [iv("B", 11, 20)]) == []
    assert [p.b_id for p in overlap_join([a], [iv("C", 10, 20)])] == ["C"]


def test_containment_inclusive():
    b = iv("B", 1, 100)
    pairs = containment_join([iv("eq", 1, 100), iv("in", 10, 20), iv("start", 1, 5),
                              iv("finish", 90, 100), iv("out", -1, 50)], [b])
    assert {p.a_id for p in pairs} == {"eq", "in", "start", "finish"}


def test_lag_join_boundaries():
    a = iv("A", 1, 10)
    rights = [iv("lag0", 10, 15), iv("lag5", 15, 20), iv("lag6", 16, 20), iv("before", 5, 20)]
    got = {p.b_id: p.lag for p in lag_join([a], rights, k=5)}
    assert got == {"lag0": 0, "lag5": 5}  # inclusive at both ends; B before A ends excluded


def test_lag_join_across_year_zero():
    a = iv("A", -5, -1)  # astro high = 0
    (pair,) = lag_join([a], [iv("B", 1, 3)], k=1)
    assert pair.lag == 1  # 1 BCE -> 1 CE is one year


def test_lag_join_rejects_negative_k():
    with pytest.raises(ValueError):
        lag_join([iv("A", 1, 2)], [iv("B", 3, 4)], k=-1)


# ------------------------------------------------------------- circular dating


def test_planted_two_cycle_is_circular():
    deps = {"A": "B", "B": "A"}
    assert is_circular("A", deps)
    assert is_circular("B", deps)


def test_longer_cycle_and_other_side():
    assert is_circular("A", {"A": "C", "C": "B", "B": "A"})
    assert is_circular("A", {"A": "C", "C": "B"}, other_side={"B"})
    assert not is_circular("A", {"A": "C", "C": "D"}, other_side={"B"})
    assert not is_circular("A", {"A": "X"})  # dangling link ends chain


def test_cycle_downstream_is_circular():
    assert is_circular("A", {"A": "C", "C": "D", "D": "C"})


def test_circular_records_in_join():
    left = [iv("A", 1, 10, dep="B"), iv("L2", 1, 10)]
    right = [iv("B", 5, 15, dep="A"), iv("R2", 5, 15, dep="Z")]
    assert circular_records(left, right) == {"A", "B"}
    assert circular_records(left[1:], right[1:], extra_dependencies={"Z": "L2"}) == {"R2"}


# ----------------------------------------------------------------- Monte Carlo


def _mean(draw: dict[str, int]) -> float:
    return sum(draw.values()) / len(draw)


def test_monte_carlo_reproducible_for_fixed_seed():
    ivs = [iv("A", -50, 50), iv("B", 100, 200), iv("C", 1, 1)]
    r1 = monte_carlo(ivs, _mean, n_draws=200, seed=7)
    r2 = monte_carlo(ivs, _mean, n_draws=200, seed=7)
    r3 = monte_carlo(ivs, _mean, n_draws=200, seed=8)
    assert r1.values == r2.values
    assert r1.values != r3.values
    assert r1.seed == 7 and r1.record_origin == "simulated"
    assert monte_carlo(ivs, _mean, n_draws=5).seed == DEFAULT_SEED == 42


def test_monte_carlo_draws_within_bounds_and_uniform_support():
    a = iv("A", -2, 2)  # astro [-1, 2]: 4 years, year 0 = 1 BCE included
    res = monte_carlo([a], lambda d: d["A"], n_draws=2000, seed=DEFAULT_SEED)
    assert set(res.values) == {-1, 0, 1, 2}
    counts = [res.values.count(y) for y in (-1, 0, 1, 2)]
    assert min(counts) > 400  # expected 500 each under uniform draws


def test_monte_carlo_excludes_records():
    ivs = [iv("A", 1, 10, dep="B"), iv("B", 1, 10, dep="A"), iv("C", 1, 10)]
    excl = circular_records(ivs[:1], ivs[1:])
    res = monte_carlo(ivs, lambda d: tuple(sorted(d)), n_draws=3, exclude=excl)
    assert res.excluded == {"A", "B"}
    assert set(res.values) == {("C",)}
