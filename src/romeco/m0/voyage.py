"""M0 voyage-level feasibility and accounting model.

Scope: one Egypt -> India -> Egypt venture, valued in the Alexandrian money of
account (drachma_EG). It establishes feasibility, break-even conditions and
who-pays-whom accounting. It is *not* an equilibrium model: all prices are
exogenous inputs with bounds taken from the parameter register.

Stocks and flows are kept separate:

* physical ledger (kg by commodity): loaded -> spoiled + arrived;
  arrived -> to_state (if tetarte in kind) + to_merchant;
* monetary ledger (drachma_EG): every transfer has a payer and a payee, so
  the sum over agents of net monetary flows on internal transfers is zero.

Agents (aggregate roles, not individuals): merchant, lender, state (fisc),
transport_providers (camel and Nile carriers, ship crew/owner), india_sellers
(external sector), alexandria_buyers (external to the venture).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

TaxMode = Literal["in_kind", "cash"]
LoanType = Literal["maritime", "ordinary"]


@dataclass(frozen=True)
class Commodity:
    name: str
    mass_loaded_kg: float
    india_price_dr_per_kg: float          # purchase price at the Indian port (dr-equivalent)
    assessment_price_dr_per_kg: float     # official valuation price used for the tetarte
    sale_price_dr_per_kg: float           # realised sale price at Alexandria
    spoilage_rate: float = 0.0            # fraction lost in transit given ship survives
    extra_levy_rate: float = 0.0          # e.g. arabarch levies (rate on assessed value)


@dataclass(frozen=True)
class VoyageParams:
    commodities: tuple[Commodity, ...]
    tau: float = 0.25                     # tetarte rate (ANC-TETARTE-RATE)
    tax_mode: TaxMode = "in_kind"
    collection_efficiency: float = 1.0    # share of liability actually collected
    exit_duty_rate: float = 0.025         # on outbound cargo value (ANC-EXIT-DUTY, disputed)
    outbound_cargo_value_dr: float = 0.0  # goods exported to India (valued at Alexandria)
    outbound_cargo_sold_in_india_dr: float = 0.0  # their proceeds in India (pay for purchases)
    p_ship_loss: float = 0.05             # probability the ship (and cargo) is lost
    ship_cost_dr: float = 0.0             # charter/capital service + crew + provisions
    camel_capacity_kg: float = 200.0
    camel_cost_per_load_dr: float = 0.0   # one desert crossing, one camel load
    nile_cost_dr_per_kg: float = 0.0      # Coptos -> Alexandria downstream
    other_fees_dr: float = 0.0            # tolls (e.g. Coptos tariff), port fees, guards
    loan_principal_dr: float = 0.0
    loan_rate: float = 0.0                # per voyage (not annualised)
    loan_type: LoanType = "maritime"


@dataclass
class VoyageResult:
    physical: dict[str, dict[str, float]] = field(default_factory=dict)
    flows: list[tuple[str, str, str, float]] = field(default_factory=list)  # (payer, payee, label, dr)
    summary: dict[str, float] = field(default_factory=dict)

    def net(self, agent: str) -> float:
        return sum(-v for p, _, _, v in self.flows if p == agent) + sum(v for _, q, _, v in self.flows if q == agent)


def run_voyage(p: VoyageParams, survives: bool = True) -> VoyageResult:
    """Deterministic accounting for one realisation (ship survives or is lost)."""
    r = VoyageResult()
    f = r.flows

    purchase = sum(c.mass_loaded_kg * c.india_price_dr_per_kg for c in p.commodities)
    # Pre-departure and outbound costs: paid whether or not the ship survives.
    f.append(("merchant", "state", "exit_duty_outbound", p.exit_duty_rate * p.outbound_cargo_value_dr))
    f.append(("merchant", "outbound_suppliers", "outbound_cargo_purchase", p.outbound_cargo_value_dr))
    f.append(("india_buyers", "merchant", "outbound_cargo_sale_india", p.outbound_cargo_sold_in_india_dr))
    f.append(("merchant", "india_sellers", "purchase_india", purchase))
    f.append(("merchant", "transport_providers", "ship_costs", p.ship_cost_dr))
    if p.loan_principal_dr:
        f.append(("lender", "merchant", "loan_principal", p.loan_principal_dr))

    gross_assessed = tax_liability = collected = levies = proceeds = 0.0
    state_goods_value_at_sale = 0.0
    total_arrived = 0.0
    for c in p.commodities:
        spoiled = c.mass_loaded_kg * c.spoilage_rate if survives else 0.0
        lost = 0.0 if survives else c.mass_loaded_kg
        arrived = c.mass_loaded_kg - spoiled - lost
        to_state = p.tau * p.collection_efficiency * arrived if (p.tax_mode == "in_kind") else 0.0
        to_merchant = arrived - to_state
        r.physical[c.name] = dict(loaded=c.mass_loaded_kg, spoiled=spoiled, lost_at_sea=lost,
                                  arrived=arrived, to_state=to_state, to_merchant=to_merchant)
        a = arrived * c.assessment_price_dr_per_kg
        gross_assessed += a
        tax_liability += p.tau * a
        levies += c.extra_levy_rate * a
        total_arrived += arrived
        if p.tax_mode == "in_kind":
            collected += to_state * c.assessment_price_dr_per_kg  # valued at assessment
            state_goods_value_at_sale += to_state * c.sale_price_dr_per_kg
            proceeds += to_merchant * c.sale_price_dr_per_kg
        else:
            proceeds += arrived * c.sale_price_dr_per_kg

    if p.tax_mode == "cash":
        collected = p.collection_efficiency * tax_liability
        f.append(("merchant", "state", "tetarte_cash", collected))
    # In kind: goods, not coin, move to the state. That transfer lives in the
    # physical ledger (to_state); its assessed value is reported in the summary
    # but deliberately NOT booked as a monetary flow.

    if survives:
        loads = total_arrived / p.camel_capacity_kg if p.camel_capacity_kg > 0 else 0.0
        f.append(("merchant", "transport_providers", "camel_hire", loads * p.camel_cost_per_load_dr))
        f.append(("merchant", "transport_providers", "nile_freight", total_arrived * p.nile_cost_dr_per_kg))
        f.append(("merchant", "state", "extra_levies", levies))
        f.append(("merchant", "fee_collectors", "other_fees", p.other_fees_dr))
        f.append(("alexandria_buyers", "merchant", "sale_proceeds", proceeds))

    repay = p.loan_principal_dr * (1 + p.loan_rate)
    if p.loan_principal_dr and (survives or p.loan_type == "ordinary"):
        f.append(("merchant", "lender", "loan_repayment", repay))

    r.summary = dict(
        purchase_india_dr=purchase,
        gross_assessed_dr=gross_assessed,
        tax_liability_dr=tax_liability,
        tax_collected_assessed_dr=collected,
        tax_evaded_dr=tax_liability - collected,
        residual_assessed_dr=gross_assessed - collected,
        state_goods_value_at_sale_dr=state_goods_value_at_sale,
        merchant_sale_proceeds_dr=proceeds,
        merchant_net_dr=r.net("merchant"),
        lender_net_dr=r.net("lender"),
        state_cash_net_dr=r.net("state"),
        arrived_kg=total_arrived,
    )
    return r


def expected_outcomes(p: VoyageParams) -> dict[str, float]:
    """Expectation over the ship-loss lottery (risk-neutral, single voyage)."""
    ok, lost = run_voyage(p, True), run_voyage(p, False)
    q = 1 - p.p_ship_loss
    keys = ("merchant_net_dr", "lender_net_dr", "state_cash_net_dr",
            "tax_collected_assessed_dr", "gross_assessed_dr")
    out = {k: q * ok.summary[k] + p.p_ship_loss * lost.summary[k] for k in keys}
    out["merchant_net_if_survives_dr"] = ok.summary["merchant_net_dr"]
    out["merchant_net_if_lost_dr"] = lost.summary["merchant_net_dr"]
    return out


def breakeven_sale_multiple(p: VoyageParams, tol: float = 1e-9) -> float:
    """Smallest uniform multiplier m on all sale prices with E[merchant net] >= 0.

    Closed form: E[net] is affine in m (proceeds scale with m, all else fixed).
    """
    def with_m(m: float) -> VoyageParams:
        cs = tuple(Commodity(c.name, c.mass_loaded_kg, c.india_price_dr_per_kg,
                             c.assessment_price_dr_per_kg, c.sale_price_dr_per_kg * m,
                             c.spoilage_rate, c.extra_levy_rate) for c in p.commodities)
        return VoyageParams(**{**p.__dict__, "commodities": cs})

    e0 = expected_outcomes(with_m(0.0))["merchant_net_dr"]
    e1 = expected_outcomes(with_m(1.0))["merchant_net_dr"]
    slope = e1 - e0
    if slope <= tol:
        return float("inf")
    return max(0.0, -e0 / slope)


def maritime_breakeven_rate(p_ship_loss: float) -> float:
    """Pure risk premium a risk-neutral maritime lender needs (no time value)."""
    return 1.0 / (1.0 - p_ship_loss) - 1.0
