# Roman Economic Systems Lab

Evidence-constrained modelling of Roman economic mechanisms. **Pilot P1:** Roman Egypt, the Red Sea and India, c. 50–200 CE.

The aim is not to reconstruct a precise Roman GDP or trade volume. The aim is to test which mechanisms the surviving evidence can distinguish, and to report bounds where that is all the evidence supports.

**Start here:** [`docs/research_design.md`](docs/research_design.md) (research design v0.1: audit, research questions, models, work plan).

## Layout

| Path | Contents |
|---|---|
| `docs/` | Research design and model specifications |
| `registers/` | Source, rights, documents, search log, hypotheses, contradictions, decisions, experiments, research log |
| `config/` | `project.yaml` (scope, seed, paths) and `parameters.yaml` (parameter register with status and bounds) |
| `data/curated/` | Reviewed evidence tables (readings, interpretations, anchors) with provenance columns |
| `data/raw/` | Acquired files, local only (git-ignored), except the CC BY papyri.info snapshot in `data/raw/idp_data/` |
| `schema/` | DuckDB evidence schema and competency queries |
| `src/romeco/` | `units` (scoped conversion rules), `evidence_db`, `ingest.epidoc` (EpiDoc reader), `m0` (Hermapollon audit, papyrus arithmetic, voyage accounting, fiscal bounds), `cli` |
| `tests/` | Unit, accounting-identity, reproduction and schema tests |
| `experiments/` | Pre-registered manifests and run outputs |
| `bib/` | Working BibTeX library (only verified fields) |

## Usage

```bash
pip install -e ".[dev]"          # Python >= 3.11; versions pinned in pyproject.toml
pytest                            # 52 tests
python -m romeco.cli audit        # Hermapollon readings x interpretations
python -m romeco.cli e000         # M0 anchor-consistency experiment -> experiments/E000_*/outputs
python -m romeco.cli cq           # build evidence DB (in memory) and run competency queries
python -m romeco.cli extract-pvindob  # line-anchored numerals of P.Vindob. G 40822 from the DDbDP snapshot
python -m romeco.cli mass         # E001: Hermapollon pepper mass under rival readings
```

## Conventions

- Every number carries provenance. Any conversion uses a named rule in `romeco.units`; there is no universal drachma, talent or purchasing-power relation.
- `record_origin` (what a record is) is kept separate from `epistemic_status` (how far it is trusted) and from `review_status` (how the project accessed it).
- Material seen only via abstracts or machine summaries is labelled `machine_summary_only` and cannot feed calibration.
- Synthetic or simulated records cannot enter the evidence tables (enforced by a schema constraint).
- Do not commit acquired full texts unless `registers/rights_register.csv` allows redistribution.
