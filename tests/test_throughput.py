"""E003 desert-throughput identities and pre-registered expectations."""

import pytest

from romeco.m0 import throughput as T


def test_accounting_identity_camels_times_cycles_equals_loads():
    r = T.required(M_t=200, load_kg=181, one_way=12, turnaround=2, window=120, n_lambda=50)
    assert r["camels_required"] * r["crossings_per_camel"] == pytest.approx(r["loads_per_season"])
    assert r["loads_per_30d"] * 120 / 30 == pytest.approx(r["loads_per_season"])
    assert r["loads_per_season"] == pytest.approx(50 * 200_000 / 181)


def test_capacity_per_1000_camels_is_inverse_of_requirement():
    r = T.required(M_t=600, load_kg=150, one_way=14, turnaround=4, window=36, n_lambda=1)
    # 1000 camels move hermapollons_per_1000_camels cargoes; one cargo needs camels_required camels
    assert r["hermapollons_per_1000_camels"] * r["camels_required"] == pytest.approx(1000)


def test_mass_readings_and_correction_of_195t():
    dr, mo = T.whole_mass_t("DeRomanis_6"), T.whole_mass_t("Morelli_24")
    assert dr == pytest.approx(624.0, abs=0.5)
    assert 213 < mo < 220          # the earlier "c. 195 t" mixed whole pepper with valuated other goods (D021)
    assert 2.8 < dr / mo < 3.2     # pre-registered expectation


def test_preregistered_expectations_hold():
    g = T.grid()
    tight = g[g.window_days <= 120]
    assert (tight.x_Berenike_supply_Ruffing > 1).all()            # H1a above every port-supply anchor
    assert g.freight_share_min.max() < 0.05                       # desert freight lower bound < 5% of value
    w = g.groupby("window_days").camels_required.median()
    assert 9 < w[36] / w[365] < 11                                # storage scenario ~10x


def test_constants_match_parameter_register():
    import yaml
    from romeco.m0.throughput import ROOT
    P = yaml.safe_load(open(ROOT / "config" / "parameters.yaml"))["parameters"]
    assert T.A_H_DR == P["A_H"]["baseline"]
    assert T.FREIGHT_DR_PER_LOAD_MIN == P["desert_freight_dr_per_camel_trip"]["bounds"][0]
    assert T.FODDER_ART_PER_CAMEL_YEAR == P["camel_fodder_art_per_year"]["baseline"]
    assert sorted(T.GRID["window_days"]) == sorted(P["return_window_days"]["scenarios"].values())
    assert {ld for ld in T.GRID["camel_load_kg"]} == {*P["camel_capacity_kg"]["bounds"], P["camel_capacity_kg"]["baseline"]}
    ow = {(t, d) for t, d in T.GRID["terminal_one_way"]}
    assert {d for t, d in ow if t == "Berenike"} == set(P["desert_days_coptos_berenike"]["bounds"])
    assert {d for t, d in ow if t == "MyosHormos"} == set(P["desert_days_coptos_myos_hormos"]["bounds"])
    assert set(T.GRID["turnaround_days"]) == set(P["camel_turnaround_days"]["bounds"])
