"""Command-line entry points.

    python -m romeco.cli audit      # Hermapollon reading/interpretation audit
    python -m romeco.cli e000       # M0 anchor-consistency experiment -> experiments/E000_*/outputs
    python -m romeco.cli cq         # build evidence DB in memory and run competency queries
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from romeco import __version__
from romeco.evidence_db import build, competency_queries, dangling_evidence, run_query
from romeco.m0 import fiscal, hermapollon

ROOT = Path(__file__).resolve().parents[2]
E000 = ROOT / "experiments" / "E000_m0_anchor_consistency"


def cmd_audit() -> pd.DataFrame:
    rows = [dict(reading=s.reading_id, interpretation=s.interpretation,
                 stated_dr=float(s.stated_dr), gross_assessed_HS=float(s.in_sestertii("gross_assessed_dr")),
                 tetarte_HS=float(s.in_sestertii("tax_liability_dr")))
            for s in hermapollon.scenario_grid()]
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print(f"\nSum of six reconstructed item values (De Romanis 2012): {float(hermapollon.reported_items_sum_dr()):,.1f} dr")
    for c in hermapollon.item_checks():
        print(f"  {c.commodity:15s} reported {float(c.reported_dr):>12,.1f}  recomputed {float(c.recomputed_dr):>12,.1f}"
              f"  residual {float(c.residual_dr):>8,.1f}  [{c.talent_adjustment}]")
    for rid in ("CR-WT-EG-001", "CR-WT-EG-002", "CR-WT-EG-003"):
        print(f"Whole-cargo pepper under {rid}: {float(hermapollon.pepper_whole_cargo_tonnes(rid)):.1f} t")
    return df


def cmd_e000(write: bool = True) -> dict:
    params = yaml.safe_load((ROOT / "config" / "parameters.yaml").read_text(encoding="utf-8"))["parameters"]
    tau = params["tau"]["baseline"]
    out_rows, bound_rows = [], []
    N_vals = np.array([10, 20, 40, 60, 80, 100, 120])
    lam_vals = np.round(np.linspace(*params["lam"]["bounds"], 15), 3)
    kap_vals = np.array(params["kappa"]["bounds"])
    for a_name, A_H in params["A_H"]["alternatives"].items():
        for O in params["O"]["bounds"]:
            for c in params["c"]["bounds"] + [params["c"]["baseline"]]:
                for p in params["p"]["bounds"] + [params["p"]["baseline"]]:
                    fi = fiscal.FiscalInputs(A_H=A_H, tau=tau, O=O, c=c, p=p)
                    b = fiscal.receipts_bounds(fi, N_max=params["N"]["bounds"][1], lam_max=params["lam"]["bounds"][1],
                                               kappa_min=kap_vals[0], kappa_max=kap_vals[1])
                    bound_rows.append(dict(A_H_variant=a_name, A_H=A_H, O=O, c=c, p=p, **b))
        g = fiscal.fiscal_grid(fiscal.FiscalInputs(A_H=A_H, tau=tau), N_vals, lam_vals, kap_vals)
        g.insert(0, "A_H_variant", a_name)
        out_rows.append(g)
    grid = pd.concat(out_rows, ignore_index=True)
    bounds = pd.DataFrame(bound_rows)
    A_base = params["A_H"]["baseline"]
    naive = fiscal.naive_receipts(A_base, N=120, tau=tau)
    headline = dict(
        naive_receipts_HS=naive,
        naive_implied_multiple_vs_50M=120 * A_base / 50_000_000,
        baseline_bounds=fiscal.receipts_bounds(
            fiscal.FiscalInputs(A_H=A_base, tau=tau, O=50_000_000, c=params["c"]["baseline"], p=params["p"]["baseline"]),
            N_max=120, lam_max=params["lam"]["bounds"][1], kappa_min=kap_vals[0], kappa_max=kap_vals[1]),
        envelope_receipts_min_HS=float(bounds["receipts_min_HS"].min()),
        envelope_receipts_max_HS=float(bounds["receipts_max_HS"].max()),
    )
    if write:
        outdir = E000 / "outputs"
        outdir.mkdir(parents=True, exist_ok=True)
        grid.to_csv(outdir / "fiscal_grid.csv", index=False)
        bounds.to_csv(outdir / "receipts_bounds.csv", index=False)
        cfg_bytes = (ROOT / "config" / "parameters.yaml").read_bytes()
        manifest = dict(
            experiment="E000_m0_anchor_consistency", run_date=str(date.today()), romeco_version=__version__,
            parameters_sha256=hashlib.sha256(cfg_bytes).hexdigest(), stochastic=False,
            python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
            record_origin_of_outputs="project_derivation (conditional calculation; not historical estimates)",
            headline=headline)
        (outdir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=float), encoding="utf-8")
    print(json.dumps(headline, indent=2, default=float))
    return headline


def cmd_cq() -> None:
    con = build()
    missing = dangling_evidence(con)
    if missing:
        print("DANGLING EVIDENCE IDS:", missing)
        sys.exit(1)
    with pd.option_context("display.width", 200, "display.max_colwidth", 70):
        for name in competency_queries():
            print(f"\n== {name}")
            print(run_query(con, name, doc="DOC-PVINDOB-G40822").to_string(index=False))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="romeco")
    ap.add_argument("command", choices=["audit", "e000", "cq"])
    args = ap.parse_args(argv)
    {"audit": cmd_audit, "e000": cmd_e000, "cq": cmd_cq}[args.command]()


if __name__ == "__main__":
    main()
