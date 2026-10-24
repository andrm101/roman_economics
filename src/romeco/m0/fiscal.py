"""Aggregate fiscal and anchor-consistency bounds (experiment E000).

Question: given the anchors usually combined in the literature -- Strabo's 120
ships, the Hermapollon valuation, Pliny's >= 50 million HS outflow -- how
tightly do they jointly constrain annual tetarte receipts?

Model (all symbols in config/parameters.yaml):

    G   = N * lam * A_H                gross assessed value of India imports / yr
    R   = tau * kappa * G               tetarte collected (assessed value) / yr
    M   = G / O                         implied gross-assessed / outflow multiple
    feasible  iff  M >= M_min,  M_min = (1 + c) / ((1 - tau) * (1 - p))

where N = India-bound sailings per year, lam = mean gross assessed value per
sailing relative to the Hermapollon, kappa = collection efficiency, O = annual
outflow to India, c = non-purchase costs as a share of purchase cost, p = ship
loss probability. M_min treats the Alexandrian assessment price as a proxy for
the realised sale price -- an explicit simplification.

Everything returned is a *conditional calculation*, not an estimate of a
historical quantity.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FiscalInputs:
    A_H: float                 # Hermapollon gross assessed value (HS, nominal)
    tau: float = 0.25
    O: float = 50_000_000.0    # Pliny NH 6.101 lower bound
    c: float = 0.5
    p: float = 0.05


def m_min(tau: float, c: float, p: float) -> float:
    return (1.0 + c) / ((1.0 - tau) * (1.0 - p))


def receipts(N: float, lam: float, kappa: float, A_H: float, tau: float) -> float:
    return tau * kappa * N * lam * A_H


def fiscal_grid(fi: FiscalInputs, N_values, lam_values, kappa_values) -> pd.DataFrame:
    rows = []
    mmin = m_min(fi.tau, fi.c, fi.p)
    for N, lam, kappa in itertools.product(N_values, lam_values, kappa_values):
        G = N * lam * fi.A_H
        M = G / fi.O
        rows.append(dict(N=N, lam=lam, kappa=kappa, gross_assessed_HS=G,
                         receipts_HS=receipts(N, lam, kappa, fi.A_H, fi.tau),
                         implied_multiple=M, m_min=mmin, feasible=M >= mmin))
    return pd.DataFrame(rows)


def receipts_bounds(fi: FiscalInputs, N_max: float, lam_max: float,
                    kappa_min: float, kappa_max: float) -> dict[str, float]:
    """Closed-form bounds on R over the feasible set.

    Lower bound: the smallest Hermapollon-equivalent volume compatible with the
    outflow anchor, N*lam >= M_min * O / A_H, at the lowest collection rate.
    Upper bound: the largest volume allowed by N_max and lam_max.
    """
    mmin = m_min(fi.tau, fi.c, fi.p)
    vol_min = mmin * fi.O / fi.A_H
    vol_max = N_max * lam_max
    if vol_min > vol_max:
        return dict(feasible=False, vol_min=vol_min, vol_max=vol_max)
    return dict(
        feasible=True,
        m_min=mmin,
        hermapollon_equivalents_min=vol_min,
        hermapollon_equivalents_max=vol_max,
        receipts_min_HS=fi.tau * kappa_min * vol_min * fi.A_H,
        receipts_max_HS=fi.tau * kappa_max * vol_max * fi.A_H,
        ratio_max_over_min=(kappa_max * vol_max) / (kappa_min * vol_min),
    )


def naive_receipts(A_H: float, N: float = 120, tau: float = 0.25) -> float:
    """The 'every ship is a Hermapollon, every ship goes to India, full collection' product."""
    return tau * N * A_H


def iso_receipt_ridge(R_target: float, fi: FiscalInputs, kappa: float, N_values) -> pd.DataFrame:
    """Combinations (N, lam) that yield the same R: the observational-equivalence ridge."""
    N = np.asarray(list(N_values), dtype=float)
    lam = R_target / (fi.tau * kappa * N * fi.A_H)
    return pd.DataFrame(dict(N=N, lam=lam, kappa=kappa, receipts_HS=R_target))
