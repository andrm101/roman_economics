"""WP9 acceptance tests: lossless round trip, rival survival, SHACL (positive and negative), CQ6-CQ11 goldens."""

import csv
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import RDF, Graph, Literal

from romeco import evidence_db
from romeco.semantic import build as B

ROOT = Path(__file__).resolve().parents[1]
RX, RXV, RXD, S = B.RX, B.RXV, B.RXD, B.short


@pytest.fixture(scope="module")
def core():
    return B.build_graph()


@pytest.fixture(scope="module")
def full():
    return B.build_graph(with_candidates=True)


@pytest.fixture(scope="module")
def shapes():
    return Graph().parse(ROOT / "ontology" / "shapes.ttl"), Graph().parse(ROOT / "ontology" / "romeco.ttl")


def conforms(g, shapes):
    sh, ont = shapes
    ok, _, txt = validate(g, shacl_graph=sh, ont_graph=ont, inference="rdfs", allow_warnings=True)
    return ok, txt


# ------------------------------------------------------------------ 1. lossless round trip
def test_round_trip_assertions(core):
    con = evidence_db.build()
    rows = con.execute("SELECT assertion_id, record_origin, epistemic_status, review_status, asserted_by, reported_in FROM assertion").fetchall()
    assert len(rows) > 50
    for aid, origin, epi, rev, by, rep in rows:
        n = B.node("claim", aid)
        assert (n, RX.recordOrigin, B.concept("origin", origin)) in core, aid
        assert (n, RX.epistemicStatus, B.concept("epistemic", epi)) in core, aid
        assert (n, RX.reviewStatus, B.concept("review", rev)) in core, aid
        if rep:
            assert (n, RX.reportedIn, B.node("source", rep)) in core, aid
        attributed = set(core.objects(n, RX.attributedTo)) | set(core.objects(n, RX.attributedToLabel))
        assert attributed or rep, aid


def test_dependencies_survive(core):
    con = evidence_db.build()
    for frm, to in con.execute("SELECT from_id, to_id FROM dependency WHERE relation='depends_on'").fetchall():
        assert (B.node("claim", frm), RX.dependsOn, B.node("claim", to)) in core


# ------------------------------------------------------------------ 2. rivals survive
def test_all_question_positions_present_with_status(core):
    for q in csv.DictReader(open(ROOT / "data" / "curated" / "semantic" / "questions.csv", encoding="utf-8")):
        qn = B.node("question", q["question_id"])
        positions = {S(str(p)) for p in core.objects(qn, RX.hasPosition)}
        assert positions == set(B._split(q["positions"])), q["question_id"]
        for p in positions:   # every position is a real claim with a status, not a dangling IRI
            assert next(core.objects(B.node("claim", p), RX.epistemicStatus), None) is not None, p


def test_rivals_are_considered_not_support(core):
    a_h = B.node("param", "A_H")
    support = {S(str(o)) for o in core.objects(a_h, RX.derivedFrom)}
    considered = {S(str(o)) for o in core.objects(a_h, RX.considered)}
    assert "INT-HERM-01" in support and "RD-HERM-TOTAL-MORELLI" in support
    assert {"INT-HERM-03", "RD-HERM-TOTAL-HS1985"} <= considered
    assert not support & considered
    assert (B.node("claim", "INT-HERM-03"), RX.epistemicStatus, B.concept("epistemic", "rejected")) in core
    assert (B.node("claim", "RD-HERM-TOTAL-HS1985"), RX.epistemicStatus, B.concept("epistemic", "superseded")) in core


# ------------------------------------------------------------------ 3. SHACL
def test_real_graph_conforms(full, shapes):
    ok, txt = conforms(full, shapes)
    assert ok, txt


def _broken(core, mutate):
    g = Graph()
    for t in core:
        g.add(t)
    mutate(g)
    return g


def test_candidate_as_parameter_evidence_fails(core, shapes):
    def m(g):
        c = RXD["cand/TEST"]
        g.add((c, RDF.type, RX.ExtractionCandidate))
        g.add((B.node("param", "A_H"), RX.derivedFrom, c))
    assert not conforms(_broken(core, m), shapes)[0]


def test_unattributed_claim_fails(core, shapes):
    def m(g):
        n = B.node("claim", "ANC-PLINY-DESERT")
        g.remove((n, RX.attributedTo, None)); g.remove((n, RX.attributedToLabel, None)); g.remove((n, RX.reportedIn, None))
    assert not conforms(_broken(core, m), shapes)[0]


def test_synthetic_claim_fails(core, shapes):
    def m(g):
        n = B.node("claim", "ANC-PLINY-DESERT")
        g.remove((n, RX.recordOrigin, None)); g.add((n, RX.recordOrigin, RXV["origin-synthetic"]))
    assert not conforms(_broken(core, m), shapes)[0]


def test_resolved_question_without_selection_fails(core, shapes):
    def m(g):
        q = B.node("question", "Q-HERM-TOTAL")
        g.remove((q, RX.selectedPosition, None)); g.remove((q, RX.selectedBy, None))
    assert not conforms(_broken(core, m), shapes)[0]


def test_candidate_with_epistemic_status_fails(shapes):
    g = B.build_graph(with_candidates=True, candidate_limit=50)
    c = next(g.subjects(RDF.type, RX.ExtractionCandidate))
    g.add((c, RX.epistemicStatus, B.concept("epistemic", "accepted_working")))
    assert not conforms(g, shapes)[0]


# ------------------------------------------------------------------ 4. competency questions
def test_cq6_rules(core):
    rows = B.query(core, "CQ6", target="param/A_H")
    assert {S(r["rule"]) for r in rows} == {"CR-MON-EG-001", "CR-MON-EG-003"}
    assert "INT-HERM-01" in {S(r["usedClaim"]) for r in rows}
    assert all("romeco.m0.hermapollon.derive" in r["code"] for r in rows)
    assert {S(r["rule"]) for r in B.query(core, "CQ6", target="param/camel_capacity_kg")} >= {"CR-WT-MOD-001"}
    assert {S(r["rule"]) for r in B.query(core, "CQ6", target="param/route_desert_km")} == {"CR-LEN-ROM-001"}


def test_cq7_place_change(core):
    rows = B.query(core, "CQ7", place="place/727131")
    assert ("CTX-GC-JULIOPOLIS-COPTOS", "route_nile_km") in {(S(r["claim"]), S(r["param"])) for r in rows}


def test_cq8_exclude_interpretation(core):
    rows = B.query(core, "CQ8", excluded="claim/INT-HERM-01")
    assert "A_H" in {S(r["param"]) for r in rows}
    exps = {S(r["experiment"]).split("_")[0] for r in rows if r["experiment"]}
    assert {"E000", "E003"} <= exps


def test_cq9_contested_inputs(core):
    rows = B.query(core, "CQ9", param="param/A_H")
    by_q = {}
    for r in rows:
        by_q.setdefault(S(r["question"]), set()).add((S(r["position"]), S(r["selected"]), S(r["decision"])))
    assert {p for p, _, _ in by_q["Q-HERM-TOTAL"]} == {"RD-HERM-TOTAL-MORELLI", "RD-HERM-TOTAL-HS1985"}
    assert {s for _, s, _ in by_q["Q-HERM-TOTAL"]} == {"RD-HERM-TOTAL-MORELLI"}
    assert "D008" in {d for _, _, d in by_q["Q-HERM-TOTAL"]}
    assert {p for p, _, _ in by_q["Q-HERM-SCOPE"]} == {"INT-HERM-01", "INT-HERM-02", "INT-HERM-03"}
    assert {s for _, s, _ in by_q["Q-HERM-SCOPE"]} == {"INT-HERM-01"}
    assert "D009" in {d for _, _, d in by_q["Q-HERM-SCOPE"]}


def test_cq10_candidates_for_anchor(full):
    rows = B.query(full, "CQ10", claim="claim/ANC-PLINY-DESERT")
    srcs = {S(r["source"]) for r in rows}
    assert {"SRC-ADAMS-2007", "SRC-PLINY-NH-MAYHOFF"} <= srcs
    assert "39" in {r["page"] for r in rows if S(r["source"]) == "SRC-ADAMS-2007"}
    for r in rows:   # leads stay candidates: never typed as claims, never parameter support
        n = RXD["cand/" + S(r["cand"])]
        assert (n, RDF.type, RX.ExtractionCandidate) in full
        assert not list(full.subjects(RX.derivedFrom, n))


def test_cq11_shared_document(full):
    rows = {S(r["doc"]): r for r in B.query(full, "CQ11")}
    works = {S(w) for w in rows["DOC-PVINDOB-G40822"]["works"].split()}
    assert {"SRC-ADAMS-2007", "SRC-NAPPO-2018"} <= works
    assert int(rows["DOC-PVINDOB-G40822"]["nWorks"]) >= 2
    assert "SRC-STRABO-GEOG" not in rows["DOC-STRABO-GEOG"]["works"]   # an edition is not a citation of itself


def test_committed_core_graph_is_current(core):
    p = ROOT / "data" / "derived" / "graph" / "core.ttl"
    assert p.exists(), "run: python -m romeco.cli graph"
    assert len(Graph().parse(p)) == len(core)
