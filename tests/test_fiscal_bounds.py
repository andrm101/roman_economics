import numpy as np
import pytest

from romeco.m0 import fiscal


def test_naive_receipts_product():
    assert fiscal.naive_receipts(9_235_803, N=120, tau=0.25) == pytest.approx(277_074_090)


def test_lower_bound_does_not_depend_on_hermapollon():
    # R_min = tau * kappa_min * M_min * O : the Hermapollon cancels out.
    kw = dict(N_max=120, lam_max=1.5, kappa_min=0.7, kappa_max=1.0)
    a = fiscal.receipts_bounds(fiscal.FiscalInputs(A_H=9_235_803), **kw)
    b = fiscal.receipts_bounds(fiscal.FiscalInputs(A_H=6_911_852), **kw)
    assert a["receipts_min_HS"] == pytest.approx(b["receipts_min_HS"])
    assert a["receipts_min_HS"] == pytest.approx(0.25 * 0.7 * fiscal.m_min(0.25, 0.5, 0.05) * 50_000_000)


def test_upper_bound_scales_with_hermapollon():
    kw = dict(N_max=120, lam_max=1.5, kappa_min=0.7, kappa_max=1.0)
    a = fiscal.receipts_bounds(fiscal.FiscalInputs(A_H=9_000_000), **kw)
    b = fiscal.receipts_bounds(fiscal.FiscalInputs(A_H=4_500_000), **kw)
    assert a["receipts_max_HS"] == pytest.approx(2 * b["receipts_max_HS"])


def test_infeasible_region_detected():
    b = fiscal.receipts_bounds(fiscal.FiscalInputs(A_H=1_000_000, O=500_000_000),
                               N_max=10, lam_max=1.0, kappa_min=0.7, kappa_max=1.0)
    assert b["feasible"] is False


def test_observational_equivalence_ridge_is_flat():
    fi = fiscal.FiscalInputs(A_H=9_235_803)
    ridge = fiscal.iso_receipt_ridge(100_000_000, fi, kappa=0.9, N_values=[20, 60, 120])
    r = [fiscal.receipts(n, l, 0.9, fi.A_H, fi.tau) for n, l in zip(ridge.N, ridge.lam)]
    assert np.allclose(r, 100_000_000)
