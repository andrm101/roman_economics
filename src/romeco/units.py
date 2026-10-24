"""Scoped unit and conversion rules.

Design rule: there is no global "drachma" or "talent". Each conversion is a
:class:`ConversionRule` with an ID, a scope (place, period, document), a source
and an epistemic status. Callers must name the rule they rely on, so every
derived number can be traced back to the convention that produced it.

Exact arithmetic (``fractions.Fraction``) is used for accounting units so that
reproductions of ancient sums are not polluted by floating-point error.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ConversionRule:
    rule_id: str
    from_unit: str
    to_unit: str
    factor: Fraction  # 1 from_unit = factor * to_unit
    scope: str
    source_id: str
    locus: str
    status: str  # documented_in_source | scholarly_convention | project_assumption | modern_definition (exact by statute)
    note: str = ""


# ---------------------------------------------------------------------------
# Rule registry. Source IDs refer to registers/source_register.csv.
# Loci marked "machine-summary" were read through an automated summary of the
# PDF, not by direct inspection of the page; see the source register.
# ---------------------------------------------------------------------------
RULES: dict[str, ConversionRule] = {
    r.rule_id: r
    for r in [
        ConversionRule(
            "CR-MON-EG-001", "talent_money_EG", "drachma_EG", Fraction(6000),
            scope="Roman Egypt, Greek documentary accounting, 1st-2nd c. CE",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note="Money talent of 6,000 drachmas as used in P.Vindob. G 40822 verso.",
        ),
        ConversionRule(
            "CR-MON-EG-002", "drachma_EG", "obol_EG", Fraction(6),
            scope="P.Vindob. G 40822 verso only",
            source_id="SRC-DEROMANIS-2012", locus="n. 20; units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note=("Document-scoped. Other Roman-Egyptian contexts reckon 7 obols to the "
                  "drachma; do NOT reuse this rule outside the papyrus without review."),
        ),
        ConversionRule(
            "CR-MON-EG-003", "drachma_EG", "sestertius_notional", Fraction(1),
            scope="Roman Egypt, Julio-Claudian to Antonine; nominal tariffing only",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note=("Notional equivalence (tetradrachm tariffed at a denarius). A nominal "
                  "accounting equivalence, not a bullion or purchasing-power relation. "
                  "Wilson 2009: 217 n. 6 applies the same 1:1 equivalence."),
        ),
        ConversionRule(
            "CR-WT-EG-001", "talent_weight_tetarte_official", "libra_roman", Fraction(95),
            scope="P.Vindob. G 40822 verso, quarter-tax valuation",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note="De Romanis's reconstruction; contested metrology.",
        ),
        ConversionRule(
            "CR-WT-EG-002", "talent_weight_ivory_recalc", "libra_roman", Fraction(195, 2),
            scope="P.Vindob. G 40822 verso, ivory recalculation",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
        ),
        ConversionRule(
            "CR-WT-EG-003", "talent_weight_pepper_recalc", "libra_roman", Fraction(9766, 100),
            scope="P.Vindob. G 40822 verso, pepper recalculation",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note="Reported as 97.66 lb in the summary; exact fraction unverified.",
        ),
        ConversionRule(
            "CR-WT-ROM-001", "libra_roman", "kg", Fraction(3228, 10000),
            scope="Roman pound, modern metrological estimate",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
            note="322.8 g; other estimates (c. 323-327 g) exist; treat as sensitivity input.",
        ),
        ConversionRule(
            "CR-WT-GEN-001", "talent_weight_any", "mina", Fraction(60),
            scope="Generic Greek weight subdivision",
            source_id="SRC-DEROMANIS-2012", locus="units table p. 101 (machine-summary)",
            status="scholarly_convention",
        ),
        ConversionRule(
            "CR-LEN-ROM-001", "mille_passus", "km", Fraction(148, 100),
            scope="Roman mile, conventional modern value",
            source_id="PROJECT", locus="-",
            status="project_assumption",
            note="c. 1.48 km; used only for order-of-magnitude route lengths.",
        ),
        ConversionRule(
            "CR-WT-MOD-001", "lb_avoirdupois", "kg", Fraction(45359237, 100000000),
            scope="modern international avoirdupois pound (to convert modern authors' 'lbs')",
            source_id="PROJECT", locus="-",
            status="modern_definition",
            note="Exact by definition (international yard and pound, 1959). Used for Adams 2007: 80 '400 lbs'.",
        ),
    ]
}


def rule(rule_id: str) -> ConversionRule:
    try:
        return RULES[rule_id]
    except KeyError as exc:  # pragma: no cover - defensive
        raise KeyError(f"Unknown conversion rule {rule_id!r}; register it in RULES first") from exc


def convert(value: Fraction | int | float, rule_id: str, inverse: bool = False) -> Fraction:
    """Apply a named rule. ``inverse=True`` converts to_unit -> from_unit."""
    r = rule(rule_id)
    v = Fraction(value)
    return v / r.factor if inverse else v * r.factor


def talents_drachmas(total_dr: Fraction | int) -> tuple[int, Fraction]:
    """Split a drachma total into (talents, drachmas) under CR-MON-EG-001."""
    per = rule("CR-MON-EG-001").factor
    t = int(Fraction(total_dr) // per)
    return t, Fraction(total_dr) - t * per


def money_to_drachmas(talents: int | Fraction, drachmas: int | Fraction = 0, obols: int | Fraction = 0) -> Fraction:
    """Talents/drachmas/obols -> drachmas, using the papyrus-scoped obol rule."""
    return (convert(talents, "CR-MON-EG-001")
            + Fraction(drachmas)
            + convert(obols, "CR-MON-EG-002", inverse=True))


def weight_talent_kg(talent_rule_id: str) -> Fraction:
    """kg per weight talent defined by ``talent_rule_id`` (via Roman pound)."""
    return convert(convert(1, talent_rule_id), "CR-WT-ROM-001")
