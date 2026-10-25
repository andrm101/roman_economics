from fractions import Fraction

import pytest

from romeco.units import RULES, convert, money_to_drachmas, talents_drachmas, weight_talent_kg


def test_money_talent_and_split_roundtrip():
    dr = money_to_drachmas(1154, 2852)
    assert dr == 6_926_852
    assert talents_drachmas(dr) == (1154, 2852)


def test_obol_rule_is_document_scoped():
    r = RULES["CR-MON-EG-002"]
    assert r.factor == 6
    assert "only" in r.scope  # guard against silent reuse outside the papyrus
    assert money_to_drachmas(0, 0, 3) == Fraction(1, 2)


def test_notional_hs_equivalence_is_flagged_as_nominal():
    r = RULES["CR-MON-EG-003"]
    assert r.factor == 1
    assert "not a bullion or purchasing-power" in r.note


def test_weight_talents_in_kg():
    assert float(weight_talent_kg("CR-WT-EG-001")) == pytest.approx(30.666, abs=1e-3)
    assert float(weight_talent_kg("CR-WT-EG-002")) == pytest.approx(31.473, abs=1e-3)
    assert float(weight_talent_kg("CR-WT-EG-003")) == pytest.approx(31.524, abs=1e-3)


def test_unknown_rule_raises():
    with pytest.raises(KeyError):
        convert(1, "CR-DOES-NOT-EXIST")


def test_every_rule_has_source_and_status():
    for r in RULES.values():
        assert r.source_id and r.status in {"documented_in_source", "scholarly_convention", "project_assumption", "modern_definition"}


def test_expansion_candidates_are_not_registered_as_read():
    """D031: brainstormed sources stay unverified until registered with an honest status."""
    import csv
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    rows = list(csv.DictReader(open(root / "registers" / "expansion_source_candidates.csv", encoding="utf-8")))
    assert rows and all(r["access_status"] == "unverified_candidate" for r in rows)
    assert len({r["cand_id"] for r in rows}) == len(rows)
