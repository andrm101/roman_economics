# Competency questions (WP9.1, registered 2026-10-24 before the ontology was expanded)

The ontology is only as large as these questions require.

- **CQ1–CQ5** run as SQL over the DuckDB evidence store (`schema/competency_queries.sql`, WP0).
- **CQ6–CQ11** run as SPARQL over the RDF graph (`ontology/queries/*.rq`).

The *expected answers* below are written from the registers before the graph exists. `tests/test_semantic.py` checks the queries against them.

| ID | Question | Why it matters | Expected answer (golden test) |
|---|---|---|---|
| CQ1 | Which parameters ultimately depend on a given ancient document? | Exclude-one-document reruns | `A_H`, `merchant_talent_litrai`, `pepper_price_dr_per_mina`, `tax_mode` depend on DOC-PVINDOB-G40822 (unchanged from WP0) |
| CQ2 | Which parameters rest on claims the project has not inspected directly? | Access honesty | non-empty; includes `pepper_price_dr_per_mina` (machine-summary interpretations) |
| CQ3 | How many independent primary documents underlie each parameter? | Independence | `A_H` → 1 |
| CQ4 | Which sources feeding parameters were never inspected? | Acquisition priorities | unchanged |
| CQ5 | Which contested claims feed parameters? | Sensitivity targets | unchanged |
| **CQ6** | Which conversion rules (and code) produced this value? | Traceability of transformations | `A_H` ← CR-MON-EG-001 (talent→drachma) and CR-MON-EG-003 (drachma→sestertius, nominal), by `romeco.m0.hermapollon.derive` under INT-HERM-01; `camel_capacity_kg` ← CR-WT-MOD-001 (lb avoirdupois→kg); `route_desert_km` ← CR-LEN-ROM-001 |
| **CQ7** | Which claims and parameters need review if a place identification changes? | Identifications are assertions too | changing the identification of Iuliopolis/Nikopolis (Pleiades 727131) affects CTX-GC-JULIOPOLIS-COPTOS → parameter `route_nile_km` |
| **CQ8** | What loses support if one interpretation is excluded? | Exclude-one-interpretation reruns | excluding INT-HERM-01 removes the support of `A_H`, and through it experiments E000 and E003 |
| **CQ9** | For a parameter's inputs, which questions are contested, what positions exist, and which was selected by which decision? | Rival interpretations must survive and stay visible | `A_H`: Q-HERM-TOTAL (selected RD-HERM-TOTAL-MORELLI, D008; rival RD-HERM-TOTAL-HS1985) and Q-HERM-SCOPE (selected INT-HERM-01, D009; rivals INT-HERM-02, INT-HERM-03) |
| **CQ10** | Which unreviewed extraction candidates bear on a registered anchor? | Turning WP4 output into review work, without promoting it | ANC-PLINY-DESERT (257 mp) has a matching quantity candidate in Adams 2007 (printed p. 39) and in Mayhoff Pliny; every match is `rx:ExtractionCandidate`, never evidence |
| **CQ11** | How many modern citations rest on how many ancient documents? | "Many authors citing one papyrus are not many observations" | DOC-PVINDOB-G40822 is cited in ≥ 2 of the parsed modern works (Adams 2007, Nappo 2018) |

**Acceptance test of the semantic foundation** (brief: "provenance and competing interpretations survive ingestion and querying"):

1. **Lossless round trip.** Every assertion, reading and interpretation in the DuckDB store appears in the graph with the same `record_origin`, `epistemic_status`, `review_status` and source attribution.
2. **Rivals survive.** All positions in every question are present. None is overwritten, and rejected or superseded ones keep that status.
3. **SHACL.** The real graph conforms. Deliberately broken graphs must fail:
   - a candidate used as parameter evidence;
   - an assertion without attribution;
   - a synthetic record in the evidence layer;
   - a question with no selected position and no "open" status.
4. **CQ6–CQ11 return the expected answers above.**
