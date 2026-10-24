# Semantic foundation (WP9)

**Status:** acceptance met 2026-10-24 (`tests/test_semantic.py`). Ontology 0.1.0, graph 0.1.0.

## What it is

There are four products, as set out in the brief. Three of them are now connected in a single RDF graph:

| Product | Where it lives | Graph classes |
|---|---|---|
| Corpus | `registers/source_register.csv`, `registers/corpus/` | `rx:Source`, `rx:FileItem`, `rx:ExtractionCandidate` |
| Evidence graph | DuckDB store (`romeco.evidence_db`), `data/curated/semantic/questions.csv` | `rx:AncientDocument`, `rx:Claim` ⊃ Reading / Anchor / Interpretation / ProjectDerivation / PlaceIdentification, `rx:Question`, `rx:Decision`, `rx:Contradiction` |
| Economic system graph | `place_crosswalk.csv` (minimal) | `rx:Place` (Pleiades), `rx:Unit` |
| Model specification | `config/parameters.yaml`, `romeco.units.RULES`, `data/curated/semantic/derivations.csv` | `rx:Parameter`, `rx:ConversionRule`, `rx:Derivation`, `rx:Experiment` (PROV activities) |

The DuckDB store is canonical. The graph is regenerated from it and never edited by hand (D027).

## Rules the graph enforces (SHACL, `ontology/shapes.ttl`)

- Every claim has exactly one evidence record origin. Synthetic and simulated records cannot be claims.
- Every claim has exactly one epistemic status and one review status, and is attributed to, or reported in, a source.
- Parameter support (`rx:derivedFrom`) must be a claim, and only the selected position of a contested question (D028). Rivals go to `rx:considered`.
- Measured, external and calibrated parameters need at least one supporting claim.
- A warning is raised when support was read only through a machine summary.
- A question has at least two positions. Once resolved, it needs one selected position and the decision that selected it.
- Extraction candidates are disjoint from claims, carry no epistemic status, and need a file item, an anchor and an extractor version (D024, D029).

## Use

```bash
python -m romeco.cli graph          # writes data/derived/graph/core.ttl (+ full.ttl), runs SHACL
```

```python
from romeco.semantic import build as B
g = B.build_graph(with_candidates=True)
B.query(g, "CQ8", excluded="claim/INT-HERM-01")      # what loses support
B.query(g, "CQ9", param="param/A_H")                 # contested inputs, positions, selection, decision
```

Node IRIs follow the pattern `https://github.com/andrm101/roman_economics/id/<kind>/<id>`. Kinds are: claim, doc, source, item, cand, param, rule, activity, question, decision, contradiction, place, unit.

## Adding things

- **A contested question:** add a row to `questions.csv`. Positions must be existing assertion IDs. Status is `open`, or `resolved_working` with `selected` and `selected_by` filled in.
- **A derivation:** add a row to `derivations.csv`, giving the code path, the claims, parameters and rules used, and the places used.
- **A document key** (so that candidates can be matched to the document): add a row to `document_keys.csv`.
- **A competency question:** register the expected answer in `docs/competency_questions.md` first, then add the `.rq` file and the test.

## Limitations

- Place identifications all carry `uncertain` status. Per-identification review is pending.
- Candidate-to-claim matching uses exact unit and value overlap only.
- Dates are integer CE bounds; OWL-Time is deferred.
- No CIDOC CRM IRIs are asserted (D026).
