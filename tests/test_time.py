"""Tests for romeco.time (T-WP10-001, T-WP10-002; spec 02_ontology_and_data.md section 4, D033, D034).

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
    monte_carlo_join,
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
    rights = [iv("lag0", 10, 15), iv("lag1", 11, 15), iv("lag5", 15, 20), iv("lag6", 16, 20),
              iv("before", 5, 20)]
    got = {p.b_id: p.lag for p in lag_join([a], rights, k=5)}
    # D034: 1 <= lag <= k, inclusive at both ends; lag 0 (shared year) and B before A ends excluded
    assert got == {"lag1": 1, "lag5": 5}


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


# ------------------------------------------------------- T-WP10-002 hardening


def test_d034_lag_join_disjoint_from_overlap_join_planted():
    a = iv("A", 100, 110)
    b_shared, b_next = iv("B", 110, 120), iv("B1", 111, 120)
    assert [p.b_id for p in overlap_join([a], [b_shared])] == ["B"]
    assert lag_join([a], [b_shared], k=10) == []
    (pair,) = lag_join([a], [b_next], k=10)
    assert (pair.b_id, pair.lag) == ("B1", 1)
    assert overlap_join([a], [b_next]) == []


def test_d034_no_pair_in_both_joins_randomised():
    import random

    rng = random.Random(DEFAULT_SEED)
    years = [y for y in range(-40, 41) if y != 0]  # historical years, no year 0
    left, right = [], []
    for i in range(150):
        for side, out in (("L", left), ("R", right)):
            lo, hi = sorted(rng.sample(years, 2)) if rng.random() < 0.8 else [rng.choice(years)] * 2
            out.append(iv(f"{side}{i}", lo, hi))
    for k in (0, 1, 5, 30):
        ov = {(p.a_id, p.b_id) for p in overlap_join(left, right)}
        lg = lag_join(left, right, k=k)
        assert ov.isdisjoint({(p.a_id, p.b_id) for p in lg})
        assert all(1 <= p.lag <= k for p in lg)
    assert ov  # the fixture actually produces overlap pairs
    assert lag_join(left, right, k=30)  # ... and lag pairs


def test_monte_carlo_auto_excludes_planted_circular_pair():
    ivs = [iv("A", 1, 10, dep="B"), iv("B", 1, 10, dep="A"), iv("C", 1, 10)]
    res = monte_carlo(ivs, lambda d: tuple(sorted(d)), n_draws=3)  # no `exclude` passed
    assert res.circular == {"A", "B"}
    assert res.excluded == {"A", "B"}
    assert set(res.values) == {("C",)}


def test_monte_carlo_auto_excludes_longer_and_downstream_cycles():
    ivs = [iv("A", 1, 10, dep="X"), iv("D", 1, 10, dep="Y"), iv("C", 1, 10, dep="Q")]
    deps = {"X": "Z", "Z": "A", "Y": "W", "W": "Y"}  # A->X->Z->A; D->Y->W->Y; Q dangling
    res = monte_carlo(ivs, lambda d: tuple(sorted(d)), n_draws=2, extra_dependencies=deps)
    assert res.circular == {"A", "D"}
    assert set(res.values) == {("C",)}


def test_monte_carlo_flat_list_keeps_acyclic_chain():
    # A depends on B, B is not circular: no join sides, so A is not excluded.
    ivs = [iv("A", 1, 10, dep="B"), iv("B", 1, 10)]
    res = monte_carlo(ivs, lambda d: tuple(sorted(d)), n_draws=2)
    assert res.circular == frozenset()
    assert set(res.values) == {("A", "B")}


def test_monte_carlo_join_auto_excludes_other_side():
    left = [iv("A", 1, 10, dep="B"), iv("L2", 1, 10)]
    right = [iv("B", 5, 15), iv("R2", 5, 15)]
    res = monte_carlo_join(left, right, lambda d: tuple(sorted(d)), n_draws=2)
    assert res.circular == {"A"}  # A's date rests on B, which is on the other side
    assert set(res.values) == {("B", "L2", "R2")}
    assert res.record_origin == "simulated"


def test_monte_carlo_caller_exclude_is_unioned():
    ivs = [iv("A", 1, 10, dep="B"), iv("B", 1, 10, dep="A"), iv("C", 1, 10), iv("E", 1, 10)]
    res = monte_carlo(ivs, lambda d: tuple(sorted(d)), n_draws=2, exclude={"E"})
    assert res.excluded == {"A", "B", "E"} and res.circular == {"A", "B"}
    assert set(res.values) == {("C",)}


def test_duplicate_record_ids_raise():
    dup = [iv("A", 1, 10), iv("A", 20, 30)]
    with pytest.raises(ValueError, match="duplicate"):
        monte_carlo(dup, _mean, n_draws=1)
    with pytest.raises(ValueError, match="duplicate"):
        monte_carlo_join([iv("A", 1, 10)], [iv("A", 20, 30)], _mean, n_draws=1)
    import random

    from romeco.time import draw_dates

    with pytest.raises(ValueError, match="duplicate"):
        draw_dates(dup, random.Random(DEFAULT_SEED))


@pytest.mark.parametrize("bad", [True, False, 0, -1, 1.0, "3", None])
def test_n_draws_must_be_positive_int_not_bool(bad):
    ivs = [iv("A", 1, 10)]
    with pytest.raises(ValueError):
        monte_carlo(ivs, _mean, n_draws=bad)
    with pytest.raises(ValueError):
        monte_carlo_join(ivs, [iv("B", 1, 10)], _mean, n_draws=bad)


def test_seed_42_default_draws_unchanged_by_hardening():
    # Same draws as a plain seeded RNG over the same intervals: auto-exclusion with
    # no dependencies must not change the sampling stream.
    import random

    ivs = [iv("A", -50, 50), iv("B", 100, 200), iv("C", 1, 1)]
    rng = random.Random(42)
    expected = tuple(_mean({v.record_id: rng.randint(v.a_low, v.a_high) for v in ivs}) for _ in range(5))
    assert monte_carlo(ivs, _mean, n_draws=5).values == expected
