"""E003: desert throughput required by the RQ1 hypotheses (M0, deterministic).

The pre-registered WP2 criterion needs a sourced desert *capacity*, which no
inspected source provides (D020). This module computes the *required* scale:
the camel loads, the camel stock in continuous service and the monthly traffic
implied by N*lambda Hermapollon-equivalent cargoes. It then compares them with
sourced scale anchors (port supply traffic, firm sizes). Nothing here is fitted.

Identities (see experiments/E003_desert_throughput/manifest.yaml):
    L  = M / load                 loads per ship
    S  = N*lambda * L             loads per season
    RT = 2*one_way + turnaround   camel cycle, days
    C  = S * RT / W               camels in continuous service during W
    m  = S * 30 / W               loads per 30 days
"""

from __future__ import annotations

import csv
import itertools
from fractions import Fraction as F
from pathlib import Path

import pandas as pd

from romeco.m0 import pvindob_arithmetic as P

ROOT = Path(__file__).resolve().parents[3]
KG_PER_LITRA = F(3228, 10000)                       # CR-WT-ROM-001
A_H_DR = 9_215_803                                  # whole-cargo value (parameter A_H; 1 dr = 1 HS notional, CR-MON-EG-002)
FREIGHT_DR_PER_LOAD_MIN = 45                        # desert_freight_dr_per_camel_trip lower bound (Adams 2007: 231)
FODDER_ART_PER_CAMEL_YEAR = 36                      # Adams 2007: 210 (5,400 art / 150 camels, 'at least')

GRID = dict(
    reading=list(P.PEPPER_PRICE_SCENARIOS),
    talent_litrai=[F(95), F(195, 2)],
    camel_load_kg=[150, 181, 200],
    terminal_one_way=[("Berenike", 12), ("Berenike", 14), ("MyosHormos", 5), ("MyosHormos", 7)],
    turnaround_days=[0, 4],
    window_days=[36, 120, 365],
)
WINDOW_BASIS = {36: "Pliny NH 6.106 departure spread (Tybi 1 - Mechir 6) [calculated]",
                120: "until outbound preparation [assumption]",
                365: "full port storage [upper bound]"}
COMPARATORS = {  # loads per 30 days; sourced scale anchors, NOT capacities
    "Berenike_supply_Nappo_low": 200, "Berenike_supply_Nappo_high": 500,
    "Berenike_supply_Ruffing": 2000, "MonsClaudianus_wheat": 150,
}
H1A_N_LAMBDA = 120


def weighed_talents(reading: str) -> dict[str, F]:
    """Valuated (three-quarter) quantities of the weighed items, in merchants' talents.

    Non-pepper items follow the De Romanis 2012 reconstruction
    (data/curated/hermapollon_items_deromanis2012.csv). Pepper follows the chosen
    reading of v col. i ll. 21-26 (romeco.m0.pvindob_arithmetic). Under the
    Morelli reading the De Romanis malabathron reconstruction is kept: a
    cross-reading assumption, flagged in the summary.
    """
    path = ROOT / "data" / "curated" / "hermapollon_items_deromanis2012.csv"
    out = {r["commodity"]: F(r["qty_talents"]) + F(r["qty_minae"]) / 60
           for r in csv.DictReader(open(path, encoding="utf-8")) if r["price_basis"] == "per_mina"}
    out["pepper"] = P.pepper_valued_merchant_talents(P.PEPPER_PRICE_SCENARIOS[reading])
    return out


def whole_mass_t(reading: str, talent_litrai: F = F(195, 2)) -> float:
    """Whole weighed cargo (valuated three parts x 4/3), tonnes. Lower bound (A3)."""
    t = sum(weighed_talents(reading).values(), F(0))
    return float(t * talent_litrai * KG_PER_LITRA / 1000 * F(4, 3))


def required(M_t: float, load_kg: float, one_way: float, turnaround: float, window: float,
             n_lambda: float = H1A_N_LAMBDA) -> dict:
    L = M_t * 1000 / load_kg
    S = n_lambda * L
    RT = 2 * one_way + turnaround
    C = S * RT / window
    m = S * 30 / window
    return dict(loads_per_ship=L, loads_per_season=S, cycle_days=RT, camels_required=C,
                loads_per_30d=m, crossings_per_camel=window / RT,
                fodder_artabas=C * FODDER_ART_PER_CAMEL_YEAR * window / 365,
                freight_share_min=L * FREIGHT_DR_PER_LOAD_MIN / A_H_DR,
                hermapollons_per_1000_camels=1000 * window / (RT * L))


def grid(n_lambda: float = H1A_N_LAMBDA) -> pd.DataFrame:
    rows = []
    for rd, tl, ld, (term, ow), ta, w in itertools.product(*GRID.values()):
        M = whole_mass_t(rd, tl)
        r = required(M, ld, ow, ta, w, n_lambda)
        rows.append(dict(reading=rd, talent_litrai=float(tl), camel_load_kg=ld, terminal=term, one_way_days=ow,
                         turnaround_days=ta, window_days=w, whole_mass_t=M, n_lambda=n_lambda, **r,
                         **{f"x_{k}": r["loads_per_30d"] / v for k, v in COMPARATORS.items()}))
    return pd.DataFrame(rows)


def summary(g: pd.DataFrame) -> pd.DataFrame:
    """Min / max over nuisance dimensions, per reading x terminal x window."""
    keys = ["reading", "terminal", "window_days"]
    cols = ["whole_mass_t", "loads_per_ship", "loads_per_season", "camels_required", "loads_per_30d",
            "x_Berenike_supply_Nappo_high", "x_Berenike_supply_Ruffing", "freight_share_min",
            "hermapollons_per_1000_camels"]
    s = g.groupby(keys)[cols].agg(["min", "max"])
    s.columns = [f"{a}_{b}" for a, b in s.columns]
    return s.reset_index()


def lambda_at_supply_scale(g: pd.DataFrame, comparator: str = "Berenike_supply_Ruffing") -> pd.DataFrame:
    """N*lambda at which trade loads per 30 days equal a sourced supply-traffic anchor (H1b signature)."""
    v = COMPARATORS[comparator]
    out = g.assign(n_lambda_at_anchor=lambda d: v * d.window_days / 30 / d.loads_per_ship)
    return (out.groupby(["reading", "window_days"]).n_lambda_at_anchor.agg(["min", "max"]).reset_index()
               .assign(comparator=comparator, anchor_loads_per_30d=v))
