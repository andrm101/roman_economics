"""WP4 corpus pipeline: registry, parsing, extraction, discovery, export, benchmark outputs."""

import csv
import json

import pytest
import yaml

from romeco.corpus import benchmark as B
from romeco.corpus import discover as D
from romeco.corpus import export as X
from romeco.corpus import extract as E
from romeco.corpus import parse as P
from romeco.corpus import registry as R


# ---------------------------------------------------------------- registry and rights
def test_registry_is_referentially_valid():
    assert R.validate() == []


def test_items_rights_flag_matches_rights_register():
    for it in R.read("items.csv"):
        assert it["redistribute_text"] == ("yes" if R.may_redistribute_text(it["rights_id"]) else "no")


def test_no_text_snippets_from_non_redistributable_sources():
    items = {i["item_id"]: i for i in R.read("items.csv")}
    rows = list(csv.DictReader(open(E.OUT / "extractions.csv", encoding="utf-8")))
    assert rows
    assert not [r for r in rows if items[r["item_id"]]["redistribute_text"] != "yes" and r["snippet"]]


def test_pipeline_states_are_monotone_and_explained():
    for r in R.read("pipeline_state.csv"):
        if r["extracted"]:
            assert r["parsed"] and r["acquired"]
        if r["unavailable"]:
            assert r["unavailable_reason"]


# ---------------------------------------------------------------- parsing (pure functions)
def test_pdf_page_offset_recovered():
    pages = ["Front matter"] * 3 + [f"{n}   Running head\nbody text\n" for n in range(1, 8)]
    labels, stats = P.label_pdf_pages(pages)
    assert stats["offset"] == -3
    assert labels[3]["printed_page"] == 1 and labels[3]["label_method"] == "detected"
    assert labels[0]["label_method"] == "none"


def test_folio_chain_ignores_chart_axis_numbers_and_ranges_gaps():
    lines = []
    for p in range(10, 16):
        lines += [f"text of page {p}"] * 20 + (["12", "10", "8", "6"] if p == 12 else []) + [str(p)]
    lines += ["text of an unnumbered opener"] * 20 + ["text of page 17"] * 20 + ["18"]
    chain = P.folio_chain(P.folio_candidates(lines))
    assert [v for _, v in chain] == [10, 11, 12, 13, 14, 15, 18]
    units, _ = P.split_flattened("\n".join(lines))
    last = units[-1]
    assert (last["page_low"], last["page_high"], last["printed_page"]) == (16, 18, None)   # range, not a guess


# ---------------------------------------------------------------- extraction (pure functions)
@pytest.mark.parametrize("text,lang,unit,lo,hi", [
    ("Coptos–Berenike 402–408 km", "en", "km", 402, 408),
    ("almost HS 7 million", "en", "sestertius", 7e6, 7e6),
    ("circa 2.000 – 2.200 km", "it", "km", 2000, 2200),
    ("1,5 km", "it", "km", 1.5, 1.5),
    ("12,5%", "it", "percent", 12.5, 12.5),
    ("600 Roman lbs", "en", "libra_roman", 600, 600),
    ("ten or twelve days’ journey", "en", "day", 10, 12),
    ("δύο δʼ ἐγκαθήμενα τῇ πόλει τάγματα", "grc", "legion", 2, 2),
])
def test_quantity_extraction(text, lang, unit, lo, hi):
    q = E.quantities(text, lang)
    assert q and (q[0]["unit"], q[0]["value_low"], q[0]["value_high"]) == (unit, lo, hi)


def test_latin_passus_vs_milia_passuum():
    q = {c["raw"]: c["value_low"] for c in E.quantities("MMp. ab Alexandria; Coptum ‾CCCVIIII‾ p.; Euphrates, VI p. intervallo", "la")}
    assert q["MMp."] == 2            # 2,000 passus
    assert q["‾CCCVIIII‾ p."] == 309  # overlined: milia passuum
    assert q["VI p."] == 6           # default milia passuum (flagged rule)


@pytest.mark.parametrize("text,key", [
    ("Plin., Nat. Hist., VI, 26", "plin.nh:6.26"),
    ("Strab . , XVI, 4, 23", "strabo:16.4.23"),
    ("P. Oxy. XXXI 2766", "poxy:31:2766"),
    ("P.Petrie II, 40", "ppetrie:2:40"),
    ("Chrest. W. 452", "wchr:452"),
    ("CIL 8.24953", "cil:8:24953"),
    ("OGIS 674", "ogis:674"),
])
def test_citation_normalisation(text, key):
    assert key in {c["norm_key"] for c in E.ancient_cites(text)}


def test_ptolemy_the_king_is_not_the_geography():
    assert not [c for c in E.ancient_cites("the harbour of Ptolemy II at Berenike") if c["norm_key"].startswith("ptol.geog")]


def test_implied_author_continuation():
    keys = {c["norm_key"] for c in E.ancient_cites("Strabo 2. 5. 12 and 17. 1. 13")}
    assert {"strabo:2.5.12", "strabo:17.1.13"} <= keys


# ---------------------------------------------------------------- discovery and export
@pytest.mark.parametrize("entry,first,year,title_start", [
    ("Wallace, S.L. 1938. Taxation in Egypt. New York.", "Wallace", "1938", "Taxation in Egypt"),
    ("Bagnall, R. S. (1993). Egypt in Late Antiquity. Princeton.", "Bagnall", "1993", "Egypt in Late Antiquity"),
    ("Amelotti, M. and L. Migliardi, ‘Una società di trasporto nella Grande Oasi’, Studi (Genoa, 1969), 167–96.", "Amelotti", "1969", "Una società"),
    ("Cuntz, O. Die Grundlagen der Peutingerschen Tafel. Hermes 29, 586–596 (1894).", "Cuntz", "1894", "Die Grundlagen"),
    ("Whitcomb, D.S. e Johnson, J.H. 1982b. “1982 season of excavation at Quseir al-Qadim.” ARCE 120, 24-30.", "Whitcomb", "1982b", "1982 season"),
])
def test_bibliography_entry_styles(entry, first, year, title_start):
    d = D.parse_entry(entry, "")
    assert (d["first_author"], d["year"]) == (first, year) and d["title"].startswith(title_start)


def test_ditto_author_inherits_previous():
    assert D.parse_entry("—— (2006). ‘The transition’, EHR 59: 435–80.", "Wrigley, E. A.")["authors"] == "Wrigley, E. A."


def test_export_keeps_name_particles_and_access_status():
    assert X._names("Pau de Soto")[0] == {"family": "de Soto", "given": "Pau"}
    lib = json.load(open(R.ROOT / "bib" / "library.csl.json", encoding="utf-8"))
    assert all("access_status=" in r["note"] for r in lib)
    dis = json.load(open(R.ROOT / "bib" / "discovered.csl.json", encoding="utf-8"))
    assert all("not acquired, not read" in r["note"] for r in dis)


# ---------------------------------------------------------------- benchmark outputs
def test_benchmark_held_out_is_disjoint_and_gold_pending_review():
    dev = {(r["stratum"], r["unit_key"]) for r in csv.DictReader(open(B.BENCH / "sample.csv", encoding="utf-8"))}
    ho = {(r["stratum"], r["unit_key"]) for r in csv.DictReader(open(B.BENCH / "sample_heldout.csv", encoding="utf-8"))}
    assert dev and ho and not (dev & ho)
    for d in ("gold", "gold_heldout"):
        for f in (B.BENCH / d).glob("*.yaml"):
            assert yaml.safe_load(f.read_text(encoding="utf-8"))["review_status"] == "assistant_annotated_pending_human_review"


def test_benchmark_reports_heldout_estimate_with_intervals():
    r = json.load(open(B.BENCH / "results_heldout_v0.2.json", encoding="utf-8"))
    p = r["pooled"]
    assert p["gold_quantities"] >= 10 and p["gold_cites"] >= 10
    lo, hi = p["c_recall_ci"]
    assert lo <= p["c_recall"] <= hi
    assert r["gold_status"] == "assistant_annotated_pending_human_review"


def test_wilson_interval():
    lo, hi = B.wilson(7, 13)
    assert 0.29 < lo < 0.30 and 0.76 < hi < 0.78
