"""Context layer: legions, cities, roads, prices/inflation."""

from pathlib import Path

import pandas as pd
import pytest

from romeco import context as C
from romeco.evidence_db import build, dangling_evidence

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data" / "derived" / "context"
RAW_OK = (ROOT / "data" / "raw" / "context" / "pleiades").exists()


def test_haversine_one_degree_latitude():
    assert C.haversine_km(32.0, 25.0, 32.0, 26.0) == pytest.approx(111.2, abs=0.3)


def test_post_break_probability_default_and_monotone():
    assert C.hermapollon_post_break_share()["p_after_break"] == pytest.approx(0.06)
    assert C.hermapollon_post_break_share(break_from=150)["p_after_break"] > 0.06


def test_deflator_post_break_index_is_median_ratio():
    d = pd.read_csv(DER / "egypt_price_deflators.csv").set_index("scenario")
    assert d.loc["post_break_central", "index_vs_pre_break"] == pytest.approx(16 / 9)


def test_gazetteer_fully_resolved_and_in_place():
    g = pd.read_csv(DER / "pilot_gazetteer.csv")
    assert g.resolved.all()
    nik = g[g.name == "Iuliopolis/Nikopolis"].iloc[0]
    assert C._in_bbox(nik.representative_longitude, nik.representative_latitude, C.EGYPT_BBOX)


def test_legion_snapshots_primary_sources():
    snap = pd.read_csv(DER / "legion_snapshots.csv")
    tac = snap[snap.snapshot == "AD23_Tacitus"]
    assert tac.n_legions.sum() == 25                      # Ann. 4.5 regional counts
    assert tac.set_index("region").loc["Aegyptus", "n_legions"] == 2
    assert (tac.review_status == "inspected").all()
    dio = snap[snap.snapshot == "c229_Dio"]
    assert (dio.review_status == "machine_summary_only").all()   # never promoted without verbatim text
    assert "III Cyrenaica" in dio.set_index("region").loc["Arabia", "legions"]


def test_egypt_legion_series_and_k16_resolution():
    eg = pd.read_csv(DER / "egypt_legion_series.csv")
    w1 = eg[eg.date_from_ce.between(23, 70)]
    assert set(w1.value_low) == {2}
    assert eg[eg.anchor_id == "MIL-EG-LEG-PIUS"].value_low.item() == 1
    m = pd.read_csv(C.CUR / "egypt_military_anchors.csv").set_index("anchor_id")
    assert m.loc["MIL-COPTOS-LEGIO-III", "epistemic_status"] == "disputed"
    assert not (C.CUR / "legions_c150_provisional.csv").exists()    # Wikipedia scaffold retired (D018)


def test_orbis_edges_selected_by_geography_not_label():
    e = pd.read_csv(DER / "orbis_pilot_edges.csv")
    assert "Naupactus" not in set(e.to_site) | set(e.from_site)   # Epirote Nicopolis trap


def test_orbis_road_time_is_constant_speed_transform():
    e = pd.read_csv(DER / "orbis_pilot_edges.csv")
    roads = e[e.route_type == "road"]
    assert roads.km_per_field_s.between(29.8, 30.4).all()
    assert (roads.field_e / roads.field_s).between(1.049, 1.051).all()


def test_eastern_desert_summary_consistent():
    s = pd.read_csv(DER / "eastern_desert_military_summary.csv")
    assert (s.active + s.inactive + s.undated == s.total).all()


def test_context_anchors_in_evidence_db():
    con = build()
    assert dangling_evidence(con) == []
    v = con.execute("SELECT value_low FROM assertion WHERE assertion_id='PL-EG-DOUBLING'").fetchone()[0]
    assert v == 2
    n = con.execute("SELECT count(*) FROM assertion WHERE assertion_id LIKE 'CF-%'").fetchone()[0]
    assert n >= 10


@pytest.mark.skipif(not RAW_OK, reason="raw context datasets not fetched (python -m romeco.cli fetch)")
def test_rebuild_matches_committed_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "OUT", tmp_path)
    C.build_all()
    for name in ("pilot_gazetteer", "orbis_pilot_edges", "eastern_desert_military_summary", "context_assertions"):
        a = pd.read_csv(tmp_path / f"{name}.csv")
        b = pd.read_csv(DER / f"{name}.csv")
        pd.testing.assert_frame_equal(a, b, check_dtype=False)


def test_eastern_desert_inventory_supports_d022():
    s = pd.read_csv(DER / "eastern_desert_documents_summary.csv").set_index("site")
    assert s.documents.sum() > 2000
    assert "Dios" not in s.index or s.loc["Dios", "documents"] < 50          # Diospolis (Thebes) excluded
    assert s.loc["Berenike", "mid_in_100_200"] < 10                           # trade-port archive is 1st-century
    assert s.loc["Myos Hormos", "mid_in_100_200"] == 0
    assert s.month_precise_in_100_200.sum() < 0.1 * s.mid_in_100_200.sum()   # W2 seasonality not estimable
