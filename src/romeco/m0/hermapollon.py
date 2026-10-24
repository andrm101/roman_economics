"""Audit of the Hermapollon valuation (P.Vindob. G 40822 verso).

Keeps three things separate that are routinely conflated in secondary
literature:

* the *stated* total (a transcribed reading, with rival readings);
* its *interpretation* (residual three-quarters vs. whole taxable base);
* the *project derivation* (gross assessed value, state take), which depends
  on both choices plus a conversion rule.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from romeco.units import convert, money_to_drachmas, weight_talent_kg

ROOT = Path(__file__).resolve().parents[3]
CURATED = ROOT / "data" / "curated"


@dataclass(frozen=True)
class Reading:
    reading_id: str
    talents: int
    drachmas: Fraction
    obols: Fraction
    read_by: str
    review_status: str

    @property
    def total_dr(self) -> Fraction:
        return money_to_drachmas(self.talents, self.drachmas, self.obols)


def load_total_readings(path: Path | None = None) -> dict[str, Reading]:
    path = path or CURATED / "hermapollon_total_readings.csv"
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["reading_id"]] = Reading(
                row["reading_id"], int(row["talents"]), Fraction(row["drachmas"]),
                Fraction(row["obols"]), row["read_by"], row["review_status"],
            )
    return out


@dataclass(frozen=True)
class ValuationScenario:
    """Project derivation from one reading under one interpretation."""

    reading_id: str
    interpretation: str  # "residual_three_quarters" | "whole_taxable_base"
    tau: Fraction
    stated_dr: Fraction
    gross_assessed_dr: Fraction
    tax_liability_dr: Fraction
    residual_dr: Fraction

    def in_sestertii(self, field: str) -> Fraction:
        # Nominal equivalence only (CR-MON-EG-003); never a purchasing-power claim.
        return convert(getattr(self, field), "CR-MON-EG-003")


def derive(reading: Reading, interpretation: str, tau: Fraction = Fraction(1, 4)) -> ValuationScenario:
    s = reading.total_dr
    if interpretation == "residual_three_quarters":
        gross = s / (1 - tau)
    elif interpretation == "whole_taxable_base":
        gross = s
    else:
        raise ValueError(interpretation)
    tax = tau * gross
    return ValuationScenario(reading.reading_id, interpretation, tau, s, gross, tax, gross - tax)


def scenario_grid(tau: Fraction = Fraction(1, 4)) -> list[ValuationScenario]:
    readings = load_total_readings()
    return [derive(r, i, tau) for r in readings.values()
            for i in ("residual_three_quarters", "whole_taxable_base")]


# ---------------------------------------------------------------------------
# Item-level reconstruction (De Romanis 2012), used as an internal-consistency
# check of the extracted numbers -- NOT as independent validation: the
# reconstruction was built to sum to the stated total ("sudoku"), so the sum
# check is circular by construction.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ItemCheck:
    item_id: str
    commodity: str
    reported_dr: Fraction
    recomputed_dr: Fraction | None
    talent_adjustment: str

    @property
    def residual_dr(self) -> Fraction | None:
        return None if self.recomputed_dr is None else self.reported_dr - self.recomputed_dr


_TALENT_ADJ = {
    # Price-per-mina applied on a heavier recalculation talent than the
    # 95-lb official talent in which quantities are stated (inference from
    # the summarised unit table; to be verified on the page).
    "ivory_sound": ("CR-WT-EG-001", "CR-WT-EG-002"),
    "schidai": ("CR-WT-EG-001", "CR-WT-EG-002"),
    "pepper": ("CR-WT-EG-001", "CR-WT-EG-003"),
}


def load_items(path: Path | None = None) -> list[dict]:
    path = path or CURATED / "hermapollon_items_deromanis2012.csv"
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def item_checks() -> list[ItemCheck]:
    checks = []
    for row in load_items():
        reported = money_to_drachmas(int(row["reported_value_talents"]),
                                     Fraction(row["reported_value_drachmas"]),
                                     Fraction(row["reported_value_obols"]))
        price = Fraction(row["price_dr"])
        if row["price_basis"] == "per_container":
            recomputed, adj = Fraction(row["qty_containers"]) * price, "none"
        else:
            minae = Fraction(row["qty_talents"]) * 60 + Fraction(row["qty_minae"])
            factor = Fraction(1)
            adj = "none"
            if row["commodity"] in _TALENT_ADJ:
                light, heavy = _TALENT_ADJ[row["commodity"]]
                factor = convert(1, light) / convert(1, heavy)
                adj = f"{light}/{heavy}"
            recomputed = minae * price * factor
        checks.append(ItemCheck(row["item_id"], row["commodity"], reported, recomputed, adj))
    return checks


def reported_items_sum_dr() -> Fraction:
    return sum((c.reported_dr for c in item_checks()), Fraction(0))


def listed_cargo_mass_tonnes(talent_rule_id: str = "CR-WT-EG-001") -> Fraction:
    """Mass of the weighed items in the reconstruction (excludes nard, counted in containers).

    These are the valuated quantities (three-quarters of the cargo under
    INT-HERM-01/02); multiply by 4/3 for the whole cargo under that reading.
    """
    kg_per_t = weight_talent_kg(talent_rule_id)
    total_talents = sum((Fraction(r["qty_talents"]) + Fraction(r["qty_minae"]) / 60
                         for r in load_items() if r["price_basis"] == "per_mina"), Fraction(0))
    return total_talents * kg_per_t / 1000


def camel_loads(mass_tonnes: float, capacity_kg: float) -> float:
    """Number of camel loads needed to move ``mass_tonnes`` across the desert once."""
    return mass_tonnes * 1000 / capacity_kg


def pepper_whole_cargo_tonnes(talent_rule_id: str = "CR-WT-EG-001",
                              talents: Fraction = Fraction(17744) + Fraction(59, 60)) -> Fraction:
    """Whole-cargo pepper mass (De Romanis 2012: 85) under a chosen weight talent."""
    return talents * weight_talent_kg(talent_rule_id) / 1000
