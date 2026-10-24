"""Build the evidence database (DuckDB) from version-controlled CSV/YAML.

The database is a derived artefact: delete it and rebuild at any time.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import duckdb
import yaml

from romeco.units import RULES

ROOT = Path(__file__).resolve().parents[2]


def _rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _num(x: str):
    x = (x or "").strip()
    return float(x) if x else None


def _int(x: str):
    x = (x or "").strip()
    return int(x) if x else None


def build(db_path: str | Path = ":memory:", root: Path = ROOT) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(db_path))
    con.execute((root / "schema" / "evidence.sql").read_text(encoding="utf-8"))

    for r in _rows(root / "registers" / "rights_register.csv"):
        con.execute("INSERT INTO rights VALUES (?,?,?,?,?,?,?,?)",
                    [r["rights_id"], r["license_or_terms"], r["private_research_use"], r["tdm_permitted"],
                     r["redistribute_full_text"], r["redistribute_derived_data"], r["checked_on"], r["evidence"]])

    for r in _rows(root / "registers" / "source_register.csv"):
        con.execute("INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?,?)",
                    [r["source_id"], r["kind"], r["creators"], r["year"], r["title"], r["container_or_series"],
                     r["identifiers"], r["access_status"], r["rights_id"], r["cited_via"]])
        for cited in filter(None, (s.strip() for s in r["cited_via"].split(";"))):
            con.execute("INSERT OR IGNORE INTO dependency VALUES (?,?,'cites')", [cited, r["source_id"]])

    for r in _rows(root / "registers" / "documents.csv"):
        con.execute("INSERT INTO document VALUES (?,?,?,?,?,?,?,?)",
                    [r["document_id"], r["designation"], r["aliases"], r["kind"], _int(r["date_low_ce"]),
                     _int(r["date_high_ce"]), r["place"], r["edition_inspected"]])

    cur = root / "data" / "curated"
    ins = ("INSERT INTO assertion VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
    for r in _rows(cur / "anchors.csv"):
        con.execute(ins, [r["anchor_id"], r["document_id"] or None, r["ancient_locus"], r["quantity_concept"],
                          _num(r["value_low"]), _num(r["value_high"]), r["unit"], r["known_problems"],
                          None, r["accessed_via"], r["page"], r["record_origin"], r["epistemic_status"],
                          r["review_status"]])

    reading_ids = []
    for r in _rows(cur / "hermapollon_total_readings.csv"):
        total = int(r["talents"]) * 6000 + float(r["drachmas"])  # CR-MON-EG-001; display value only
        con.execute(ins, [r["reading_id"], r["document_id"], r["locus"], r["quantity_concept"], total, total,
                          "drachma_EG", r["note"], r["read_by"], r["reported_in"], r["reported_page"],
                          r["record_origin"], r["epistemic_status"], r["review_status"]])
        reading_ids.append(r["reading_id"])

    for r in _rows(cur / "hermapollon_interpretations.csv"):
        doc = "DOC-PVINDOB-G40822" if r["interpretation_id"].startswith("INT-HERM") else "DOC-STRABO-GEOG"
        status = "inspected" if r["review_status"] == "inspected" else r["review_status"]
        con.execute(ins, [r["interpretation_id"], doc, r["applies_to"], "interpretation", None, None, None,
                          r["claim"], r["asserted_by"], r["asserted_in"], r["page"],
                          "scholarly_reconstruction", r["epistemic_status"], status])
        if r["interpretation_id"].startswith("INT-HERM"):
            for rid in reading_ids:
                con.execute("INSERT OR IGNORE INTO dependency VALUES (?,?,'depends_on')",
                            [r["interpretation_id"], rid])

    params = yaml.safe_load((root / "config" / "parameters.yaml").read_text(encoding="utf-8"))["parameters"]
    for pid, p in params.items():
        lo, hi = (p.get("bounds") or [None, None])
        con.execute("INSERT INTO parameter VALUES (?,?,?,?,?,?,?)",
                    [pid, p.get("definition"), p.get("unit"), p.get("baseline"), lo, hi, p["status"]])
        for ev in p.get("evidence") or []:
            con.execute("INSERT OR IGNORE INTO dependency VALUES (?,?,'derived_from')", [pid, ev])

    for r in RULES.values():
        con.execute("INSERT INTO conversion_rule VALUES (?,?,?,?,?,?,?,?,?)",
                    [r.rule_id, r.from_unit, r.to_unit, float(r.factor), r.scope, r.source_id,
                     r.locus, r.status, r.note])
    return con


def competency_queries(root: Path = ROOT) -> dict[str, str]:
    text = (root / "schema" / "competency_queries.sql").read_text(encoding="utf-8")
    out = {}
    for block in re.split(r"^-- name: ", text, flags=re.M)[1:]:
        name, body = block.split("\n", 1)
        out[name.strip()] = body.strip().rstrip(";")
    return out


def run_query(con, name: str, **params):
    sql = competency_queries()[name].format(**params)
    return con.execute(sql).fetchdf()


def dangling_evidence(con) -> list[str]:
    """Parameter evidence IDs that do not resolve to an assertion (must be empty)."""
    return [r[0] for r in con.execute(
        "SELECT to_id FROM dependency WHERE relation='derived_from' "
        "AND to_id NOT IN (SELECT assertion_id FROM assertion)").fetchall()]
