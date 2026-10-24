import math

import pytest

from romeco.m0.voyage import (Commodity, VoyageParams, breakeven_sale_multiple, expected_outcomes,
                              maritime_breakeven_rate, run_voyage)


def base_params(**kw) -> VoyageParams:
    cs = (
        Commodity("pepper", 400_000, 2.0, 10.0, 12.0, spoilage_rate=0.02),
        Commodity("malabathron", 50_000, 4.0, 25.0, 30.0, spoilage_rate=0.05, extra_levy_rate=0.0),
        Commodity("ivory", 3_000, 60.0, 300.0, 320.0, extra_levy_rate=0.0025),
    )
    defaults = dict(commodities=cs, ship_cost_dr=400_000, camel_cost_per_load_dr=40,
                    nile_cost_dr_per_kg=0.2, other_fees_dr=10_000, loan_principal_dr=500_000,
                    loan_rate=0.25, outbound_cargo_value_dr=300_000, outbound_cargo_sold_in_india_dr=450_000)
    defaults.update(kw)
    return VoyageParams(**defaults)


def test_physical_ledger_balances():
    r = run_voyage(base_params(), survives=True)
    for c, led in r.physical.items():
        assert led["loaded"] == pytest.approx(led["spoiled"] + led["lost_at_sea"] + led["arrived"])
        assert led["arrived"] == pytest.approx(led["to_state"] + led["to_merchant"])


def test_goods_vanish_only_through_loss_states():
    r = run_voyage(base_params(), survives=False)
    assert all(led["arrived"] == 0 and led["lost_at_sea"] == led["loaded"] for led in r.physical.values())


def test_monetary_flows_have_counterparties():
    for survives in (True, False):
        r = run_voyage(base_params(), survives=survives)
        agents = {a for p, q, _, _ in r.flows for a in (p, q)}
        assert math.isclose(sum(r.net(a) for a in agents), 0.0, abs_tol=1e-6)


@pytest.mark.parametrize("mode", ["in_kind", "cash"])
def test_liability_equals_collected_plus_evaded(mode):
    r = run_voyage(base_params(tax_mode=mode, collection_efficiency=0.8))
    s = r.summary
    assert s["tax_liability_dr"] == pytest.approx(s["tax_collected_assessed_dr"] + s["tax_evaded_dr"])


def test_residual_is_three_quarters_with_full_collection():
    s = run_voyage(base_params(collection_efficiency=1.0)).summary
    assert s["residual_assessed_dr"] == pytest.approx(0.75 * s["gross_assessed_dr"])


def test_cash_and_in_kind_equivalent_when_sale_equals_assessment():
    cs = tuple(Commodity(c.name, c.mass_loaded_kg, c.india_price_dr_per_kg, c.assessment_price_dr_per_kg,
                         c.assessment_price_dr_per_kg, c.spoilage_rate) for c in base_params().commodities)
    a = run_voyage(base_params(commodities=cs, tax_mode="in_kind")).summary["merchant_net_dr"]
    b = run_voyage(base_params(commodities=cs, tax_mode="cash")).summary["merchant_net_dr"]
    assert a == pytest.approx(b)


def test_zero_tax_limit():
    with_tax = run_voyage(base_params(tax_mode="cash")).summary
    no_tax = run_voyage(base_params(tax_mode="cash", tau=0.0)).summary
    assert no_tax["tax_collected_assessed_dr"] == 0
    assert no_tax["merchant_net_dr"] - with_tax["merchant_net_dr"] == pytest.approx(with_tax["tax_collected_assessed_dr"])


def test_maritime_vs_ordinary_loan_risk_allocation():
    m = run_voyage(base_params(loan_type="maritime"), survives=False).summary
    o = run_voyage(base_params(loan_type="ordinary"), survives=False).summary
    assert m["lender_net_dr"] == pytest.approx(-500_000)          # lender bears sea risk
    assert o["lender_net_dr"] == pytest.approx(500_000 * 0.25)     # borrower repays regardless
    assert o["merchant_net_dr"] < m["merchant_net_dr"]


def test_maritime_breakeven_rate():
    assert maritime_breakeven_rate(0.0) == 0.0
    assert maritime_breakeven_rate(0.2) == pytest.approx(0.25)


def test_breakeven_multiple_rises_with_loss_risk():
    lo = breakeven_sale_multiple(base_params(p_ship_loss=0.01))
    hi = breakeven_sale_multiple(base_params(p_ship_loss=0.15))
    assert 0 < lo < hi < math.inf


def test_expected_merchant_net_is_mixture():
    p = base_params(p_ship_loss=0.1)
    e = expected_outcomes(p)
    assert e["merchant_net_dr"] == pytest.approx(0.9 * e["merchant_net_if_survives_dr"] + 0.1 * e["merchant_net_if_lost_dr"])
