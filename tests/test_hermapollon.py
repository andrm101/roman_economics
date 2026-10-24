from fractions import Fraction

import pytest

from romeco.m0 import hermapollon as H


def _scen(reading, interp):
    r = H.load_total_readings()[reading]
    return H.derive(r, interp)


def test_reproduces_wilson_2009_n6_figures():
    # Wilson 2009: 217 n. 6 (after Rathbone): HS 6,926,852 after duty -> HS 9,235,803 before; state c. HS 2,308,951.
    s = _scen("RD-HERM-TOTAL-HS1985", "residual_three_quarters")
    assert s.stated_dr == 6_926_852
    assert round(s.in_sestertii("gross_assessed_dr")) == 9_235_803
    assert round(s.in_sestertii("tax_liability_dr")) == 2_308_951


def test_morelli_reading_scenario():
    s = _scen("RD-HERM-TOTAL-MORELLI", "residual_three_quarters")
    assert s.stated_dr == 6_911_852
    assert round(float(s.gross_assessed_dr)) == 9_215_803


def test_reading_choice_matters_less_than_interpretation_choice():
    a = _scen("RD-HERM-TOTAL-HS1985", "residual_three_quarters").gross_assessed_dr
    b = _scen("RD-HERM-TOTAL-MORELLI", "residual_three_quarters").gross_assessed_dr
    c = _scen("RD-HERM-TOTAL-HS1985", "whole_taxable_base").gross_assessed_dr
    reading_gap = abs(a - b) / a
    interp_gap = abs(a - c) / a
    assert reading_gap < Fraction(1, 400)   # < 0.25 %
    assert interp_gap == Fraction(1, 4)     # exactly 25 %


def test_residual_identity():
    for s in H.scenario_grid():
        assert s.residual_dr == s.gross_assessed_dr * (1 - s.tau)


def test_item_sum_equals_morelli_total_exactly():
    # Circular by construction: the reconstruction was solved to hit this total.
    assert H.reported_items_sum_dr() == H.load_total_readings()["RD-HERM-TOTAL-MORELLI"].total_dr


@pytest.mark.parametrize("commodity", ["gangetic_nard", "malabathron", "tortoise_shell"])
def test_items_recompute_exactly(commodity):
    c = next(c for c in H.item_checks() if c.commodity == commodity)
    assert c.residual_dr == 0


@pytest.mark.parametrize("commodity", ["ivory_sound", "schidai", "pepper"])
def test_items_with_talent_adjustment_have_small_documented_residuals(commodity):
    # Non-zero residuals are expected until the fractions are checked on the page image.
    c = next(c for c in H.item_checks() if c.commodity == commodity)
    assert abs(c.residual_dr / c.reported_dr) < Fraction(5, 10000)


def test_pepper_whole_cargo_mass_range():
    t = [float(H.pepper_whole_cargo_tonnes(r)) for r in ("CR-WT-EG-001", "CR-WT-EG-002", "CR-WT-EG-003")]
    assert 540 < min(t) and max(t) < 565


def test_listed_cargo_mass_and_camel_loads():
    m = float(H.listed_cargo_mass_tonnes())          # valuated (three-quarter) quantities, excl. nard
    assert 460 < m < 475
    whole = m * 4 / 3
    assert H.camel_loads(whole, 200) == pytest.approx(whole * 5)
