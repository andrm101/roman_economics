"""WP9.4 Build the RDF evidence graph from the canonical registers.

The DuckDB evidence store (romeco.evidence_db) remains canonical; this graph is a derived,
validated view for provenance and argumentation queries (CQ6-CQ11).

* ``build_graph(with_candidates=False)`` -> rdflib.Graph (core: sources, documents, claims,
  questions, decisions, contradictions, places, parameters, rules, derivations, experiments)
* ``with_candidates=True`` adds WP4 extraction candidates and their unreviewed
  ``rx:possiblyBearsOn`` links (document-consistent matching only).
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, SKOS

from romeco import evidence_db
from romeco.units import RULES

ROOT = Path(__file__).resolve().parents[3]
RX = Namespace("https://github.com/andrm101/roman_economics/ontology#")
RXV = Namespace("https://github.com/andrm101/roman_economics/vocab/")
RXD = Namespace("https://github.com/andrm101/roman_economics/id/")
PLEIADES = "https://pleiades.stoa.org/places/"
CUR = ROOT / "data" / "curated" / "semantic"
GRAPH_VERSION = "0.1.0"

# Units used by anchors vs extraction candidates (same concept, different labels in the registers).
UNIT_EQUIV = {"mille_passus": "mile_roman", "days": "day", "km": "km", "artaba": "artaba", "libra_roman": "libra_roman",
              "lb_avoirdupois": "lb", "kg": "kg", "legions": "legion", "soldiers": "soldier", "ships": "ship",
              "m3": "m3", "drachma_EG": "drachma", "camels": "camel"}


def _rows(p: Path) -> list[dict]:
    return list(csv.DictReader(open(p, encoding="utf-8")))


def _split(s: str | None) -> list[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def node(kind: str, ident: str) -> URIRef:
    return RXD[f"{kind}/{re.sub(r'[^A-Za-z0-9_.:-]', '_', ident)}"]


def concept(scheme: str, value: str) -> URIRef:
    return RXV[f"{scheme}-{value}"]


def claim_class(aid: str, origin: str) -> URIRef:
    if aid.startswith("RD-"):
        return RX.Reading
    if aid.startswith("INT-"):
        return RX.Interpretation
    if origin == "project_derivation":
        return RX.ProjectDerivation
    return RX.Anchor


def _vocab(g: Graph, con) -> None:
    schemes = {"origin": ("RecordOrigin", "record_origin"), "epistemic": ("EpistemicStatus", "epistemic_status"),
               "review": ("ReviewStatus", "review_status")}
    for short, (scheme, enum) in schemes.items():
        for (v,) in con.execute(f"SELECT unnest(enum_range(NULL::{enum}))").fetchall():
            c = concept(short, v)
            g.add((c, RDF.type, SKOS.Concept)); g.add((c, SKOS.inScheme, RX[scheme])); g.add((c, SKOS.prefLabel, Literal(v)))
    for v in ("measured_input", "external_estimate", "calibrated", "exploratory"):
        c = concept("param", v)
        g.add((c, RDF.type, SKOS.Concept)); g.add((c, SKOS.inScheme, RX.ParameterStatus)); g.add((c, SKOS.prefLabel, Literal(v)))


def _unit(g: Graph, u: str | None) -> URIRef | None:
    if not u:
        return None
    n = node("unit", u)
    g.add((n, RDF.type, RX.Unit)); g.add((n, SKOS.inScheme, RX.UnitScheme)); g.add((n, SKOS.prefLabel, Literal(u)))
    eq = UNIT_EQUIV.get(u)
    if eq and eq != u:
        e = node("unit", eq)
        g.add((e, RDF.type, RX.Unit)); g.add((e, SKOS.inScheme, RX.UnitScheme)); g.add((e, SKOS.prefLabel, Literal(eq)))
        g.add((n, SKOS.exactMatch, e))
    return n


def build_graph(with_candidates: bool = False, candidate_limit: int | None = None) -> Graph:
    con = evidence_db.build()
    g = Graph()
    for p, ns in (("rx", RX), ("rxv", RXV), ("rxd", RXD), ("prov", PROV), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(p, ns)
    _vocab(g, con)

    # ---------------------------------------------------------------- sources, files, relations
    for sid, kind, creators, year, title, access in con.execute(
            "SELECT source_id, kind, creators, year, title, access_status FROM source").fetchall():
        n = node("source", sid)
        g.add((n, RDF.type, RX.Source)); g.add((n, DCTERMS.identifier, Literal(sid)))
        g.add((n, DCTERMS.title, Literal(title or ""))); g.add((n, RX.accessStatus, Literal(access)))
        if creators:
            g.add((n, DCTERMS.creator, Literal(creators)))
        if year:
            g.add((n, DCTERMS.date, Literal(year)))
        g.add((n, RX.sourceKind, Literal(kind)))
    proj = node("source", "PROJECT")
    g.add((proj, RDF.type, RX.Source)); g.add((proj, DCTERMS.title, Literal("romeco project derivation (code in this repository)")))
    g.add((proj, RX.accessStatus, Literal("inspected_full_text")))
    rel_map = {"part_of": RX.partOf, "describes": RX.describes, "derived_from": RX.sourceDerivedFrom,
               "edition_of": RX.editionOf, "translation_of": RX.translationOf, "same_work_as": RX.sameWorkAs}
    for r in _rows(ROOT / "registers" / "corpus" / "relations.csv"):
        g.add((node("source", r["subject_id"]), rel_map[r["relation"]], node("source", r["object_id"])))
    for it in _rows(ROOT / "registers" / "corpus" / "items.csv"):
        n = node("item", it["item_id"])
        g.add((n, RDF.type, RX.FileItem)); g.add((n, RX.sha256, Literal(it["sha256"])))
        g.add((n, RX.copyOf, node("source", it["source_id"]))); g.add((n, RX.mediaType, Literal(it["media_type"])))

    # ---------------------------------------------------------------- documents and citation keys
    docs = {}
    for did, desig, aliases, kind in con.execute("SELECT document_id, designation, aliases, kind FROM document").fetchall():
        n = node("doc", did)
        docs[did] = n
        g.add((n, RDF.type, RX.AncientDocument)); g.add((n, RDFS.label, Literal(desig)))
    for r in _rows(CUR / "document_keys.csv"):
        g.add((node("doc", r["document_id"]), RX.citationKey, Literal(r["citation_key"])))

    # ---------------------------------------------------------------- claims (lossless from DuckDB)
    for (aid, did, locus, concept_, lo, hi, unit, text, by, rep, page, origin, epi, rev) in con.execute(
            "SELECT * FROM assertion").fetchall():
        n = node("claim", aid)
        g.add((n, RDF.type, claim_class(aid, origin))); g.add((n, DCTERMS.identifier, Literal(aid)))
        g.add((n, RX.recordOrigin, concept("origin", origin)))
        g.add((n, RX.epistemicStatus, concept("epistemic", epi)))
        g.add((n, RX.reviewStatus, concept("review", rev)))
        if did:
            g.add((n, RX.aboutDocument, node("doc", did)))
        for p_, v in ((RX.locus, locus), (RX.quantityConcept, concept_), (RX.claimText, text), (RX.page, page)):
            if v not in (None, ""):
                g.add((n, p_, Literal(v)))
        if lo is not None:
            g.add((n, RX.valueLow, Literal(float(lo), datatype=XSD.double)))
        if hi is not None:
            g.add((n, RX.valueHigh, Literal(float(hi), datatype=XSD.double)))
        un = _unit(g, unit)
        if un is not None:
            g.add((n, RX.unit, un))
        by_ids = [b for b in _split(by) if (b == "PROJECT" or b.startswith("SRC-"))]
        for b in by_ids:
            g.add((n, RX.attributedTo, node("source", b)))
        if by and not by_ids:
            g.add((n, RX.attributedToLabel, Literal(by)))
        if rep:
            g.add((n, RX.reportedIn, node("source", rep)))
    for frm, to in con.execute("SELECT from_id, to_id FROM dependency WHERE relation='depends_on'").fetchall():
        g.add((node("claim", frm), RX.dependsOn, node("claim", to)))

    # place references carried by anchors
    for r in _rows(ROOT / "data" / "curated" / "context" / "egypt_military_anchors.csv"):
        if r.get("place_pleiades_id"):
            g.add((node("claim", r["anchor_id"]), RX.aboutPlace, node("place", r["place_pleiades_id"])))

    # ---------------------------------------------------------------- places and identifications
    for r in _rows(ROOT / "data" / "curated" / "context" / "place_crosswalk.csv"):
        pl = node("place", r["pleiades_id"])
        g.add((pl, RDF.type, RX.Place)); g.add((pl, RX.pleiades, URIRef(PLEIADES + r["pleiades_id"])))
        g.add((pl, RDFS.label, Literal(r["name"])))
        idn = node("claim", f"PID-{r['name']}-{r['pleiades_id']}")
        g.add((idn, RDF.type, RX.PlaceIdentification)); g.add((idn, RX.identifiesName, Literal(r["name"])))
        g.add((idn, RX.identifiedAs, pl)); g.add((idn, RX.recordOrigin, concept("origin", "project_derivation")))
        g.add((idn, RX.epistemicStatus, concept("epistemic", "uncertain")))
        g.add((idn, RX.reviewStatus, concept("review", "inspected")))
        g.add((idn, RX.attributedTo, proj)); g.add((idn, RX.matchStatus, Literal(r["match_status"])))

    # ---------------------------------------------------------------- questions, decisions, contradictions
    qrows = _rows(CUR / "questions.csv")
    nonselected = set()
    for q in qrows:
        qn = node("question", q["question_id"])
        g.add((qn, RDF.type, RX.Question)); g.add((qn, RDFS.label, Literal(q["text"])))
        g.add((qn, RX.questionStatus, Literal(q["status"])))
        for pos in _split(q["positions"]):
            g.add((qn, RX.hasPosition, node("claim", pos)))
            if q["selected"] and pos != q["selected"]:
                nonselected.add(pos)
        if q["selected"]:
            g.add((qn, RX.selectedPosition, node("claim", q["selected"])))
        for d in _split(q["selected_by"]):
            dn = node("decision", d)
            g.add((dn, RDF.type, RX.Decision)); g.add((qn, RX.selectedBy, dn))
        if q["contradiction_id"]:
            kn = node("contradiction", q["contradiction_id"])
            g.add((kn, RDF.type, RX.Contradiction)); g.add((qn, RX.recordedAs, kn))

    # ---------------------------------------------------------------- parameters (support vs considered)
    params = yaml.safe_load((ROOT / "config" / "parameters.yaml").read_text(encoding="utf-8"))["parameters"]
    for pid, p in params.items():
        n = node("param", pid)
        g.add((n, RDF.type, RX.Parameter)); g.add((n, DCTERMS.identifier, Literal(pid)))
        g.add((n, RX.parameterStatus, concept("param", p["status"])))
        if isinstance(p.get("baseline"), (int, float)):
            g.add((n, RX.baseline, Literal(float(p["baseline"]), datatype=XSD.double)))
        lo, hi = (p.get("bounds") or [None, None])
        if isinstance(lo, (int, float)):
            g.add((n, RX.boundLow, Literal(float(lo), datatype=XSD.double)))
        if isinstance(hi, (int, float)):
            g.add((n, RX.boundHigh, Literal(float(hi), datatype=XSD.double)))
        for ev in p.get("evidence") or []:
            g.add((n, RX.considered if ev in nonselected else RX.derivedFrom, node("claim", ev)))

    # ---------------------------------------------------------------- conversion rules
    for r in RULES.values():
        n = node("rule", r.rule_id)
        g.add((n, RDF.type, RX.ConversionRule)); g.add((n, DCTERMS.identifier, Literal(r.rule_id)))
        g.add((n, RX.scope, Literal(r.scope))); g.add((n, RX.factor, Literal(float(r.factor), datatype=XSD.double)))
        g.add((n, RX.fromUnit, _unit(g, r.from_unit))); g.add((n, RX.toUnit, _unit(g, r.to_unit)))
        g.add((n, RX.ruleStatus, Literal(r.status)))

    # ---------------------------------------------------------------- derivations and experiments
    for d in _rows(CUR / "derivations.csv"):
        n = node("activity", d["derivation_id"])
        g.add((n, RDF.type, RX.Experiment if d["kind"] == "experiment" else RX.Derivation))
        g.add((n, RX.code, Literal(d["code"])))
        for gen in _split(d["generated"]):
            tgt = node("param", gen) if gen in params else node("claim", gen)
            g.add((n, PROV.generated, tgt)); g.add((tgt, PROV.wasGeneratedBy, n))
        for c in _split(d["used_claims"]):
            g.add((n, PROV.used, node("claim", c)))
        for c in _split(d["used_params"]):
            g.add((n, PROV.used, node("param", c)))
        for c in _split(d["used_rules"]):
            g.add((n, RX.usedRule, node("rule", c))); g.add((n, PROV.used, node("rule", c)))
        for c in _split(d["used_sources"]):
            g.add((n, PROV.used, node("source", c)))
        for pl in _split(d["used_places"]):
            g.add((n, PROV.used, node("place", pl)))
            for gen in _split(d["generated"]):
                if gen not in params:
                    g.add((node("claim", gen), RX.aboutPlace, node("place", pl)))

    if with_candidates:
        add_candidates(g, con, limit=candidate_limit)
    g.add((URIRef(str(RXD)), RX.graphVersion, Literal(GRAPH_VERSION)))
    return g


def _doc_for_key(key: str, keys: list[dict]) -> str | None:
    for k in keys:
        if (k["match"] == "exact" and key == k["citation_key"]) or (k["match"] == "prefix" and key.startswith(k["citation_key"])):
            return k["document_id"]
    return None


def add_candidates(g: Graph, con, limit: int | None = None) -> None:
    """WP4 candidates + unreviewed, document-consistent links (CQ10/CQ11)."""
    keys = _rows(CUR / "document_keys.csv")
    items = {i["item_id"]: i for i in _rows(ROOT / "registers" / "corpus" / "items.csv")}
    src_kind = {r[0]: r[1] for r in con.execute("SELECT source_id, kind FROM source").fetchall()}
    edition_doc = {}                     # an edition item is 'inside' its ancient document
    for r in _rows(ROOT / "registers" / "documents.csv"):
        for s in _split(r["accessed_via"]):
            if src_kind.get(s) in ("edition", "dataset"):
                edition_doc[s] = r["document_id"]
    anchors = {}
    for aid, did, lo, hi, unit in con.execute(
            "SELECT assertion_id, document_id, value_low, value_high, unit FROM assertion WHERE value_low IS NOT NULL AND document_id IS NOT NULL").fetchall():
        anchors.setdefault(did, []).append((aid, float(lo), float(hi if hi is not None else lo), UNIT_EQUIV.get(unit, unit)))
    rows = _rows(ROOT / "data" / "derived" / "corpus" / "extractions.csv")
    if limit:
        rows = rows[:limit]
    by_unit: dict[tuple, list[dict]] = {}
    for r in rows:
        by_unit.setdefault((r["item_id"], r["unit_ref"]), []).append(r)
    for (item_id, uref), rs in by_unit.items():
        docs_here = {d for r in rs if r["kind"] == "ancient_cite" for d in [_doc_for_key(r["norm_key"], keys)] if d}
        inside = edition_doc.get(items[item_id]["source_id"])
        if inside:
            docs_here.add(inside)
        for r in rs:
            n = node("cand", r["ext_id"])
            g.add((n, RDF.type, RX.ExtractionCandidate)); g.add((n, RX.candidateFrom, node("item", item_id)))
            g.add((n, RX.anchorRef, Literal(uref))); g.add((n, RX.candidateKind, Literal(r["kind"])))
            g.add((n, RX.extractorVersion, Literal(r["extractor_version"]))); g.add((n, RX.rule, Literal(r["rule"])))
            if r["printed_page"]:
                g.add((n, RX.printedPage, Literal(r["printed_page"])))
            if r["norm_key"]:
                g.add((n, RX.normKey, Literal(r["norm_key"])))
            if r["kind"] == "ancient_cite":
                d = _doc_for_key(r["norm_key"], keys)
                if d:
                    g.add((n, RX.possiblyBearsOn, node("doc", d)))
            elif r["kind"] == "quantity":
                lo, hi, unit = float(r["value_low"]), float(r["value_high"]), r["unit"]
                g.add((n, RX.valueLow, Literal(lo, datatype=XSD.double))); g.add((n, RX.valueHigh, Literal(hi, datatype=XSD.double)))
                g.add((n, RX.candidateUnit, Literal(unit)))
                for d in docs_here:               # document-consistent value match only
                    for aid, alo, ahi, aunit in anchors.get(d, []):
                        if aunit == unit and lo <= ahi and hi >= alo:
                            g.add((n, RX.possiblyBearsOn, node("claim", aid)))


def write(path: Path | None = None, with_candidates: bool = False) -> tuple[Path, int]:
    g = build_graph(with_candidates=with_candidates)
    out = path or ROOT / "data" / "derived" / "graph" / ("full.ttl" if with_candidates else "core.ttl")
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(out, format="turtle")
    return out, len(g)


QUERY_DIR = ROOT / "ontology" / "queries"


def query(g: Graph, name: str, **bind) -> list[dict]:
    """Run ontology/queries/<name>*.rq with initial bindings (values: URIRef or str id 'kind/ident')."""
    path = next(QUERY_DIR.glob(f"{name}_*.rq"))
    init = {k: (v if isinstance(v, URIRef) else RXD[v]) for k, v in bind.items()}
    res = g.query(path.read_text(encoding="utf-8"), initBindings=init)
    return [{str(k): (str(r[k]) if r[k] is not None else None) for k in res.vars} for r in res]


def short(iri: str | None) -> str | None:
    return iri.rsplit("/", 1)[-1] if iri else iri
