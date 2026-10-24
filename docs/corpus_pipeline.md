# Corpus pipeline (WP4), v0.2 — 2026-10-24

**Status: pilot implemented and benchmarked.** The WP4 acceptance test (error rates by stratum; every claim anchored) is met **provisionally**: the gold set was annotated by the assistant that wrote the extractors and awaits the researcher's review (`benchmark/gold_review_sheet.csv`).

Run end to end (resumable; re-runs skip unchanged files):

```bash
python -m romeco.cli corpus      # acquire -> parse -> extract -> discover -> export
ROMECO_TESSDATA=/path/to/tessdata_fast python -m romeco.cli benchmark
```

## 1. Architecture

| Stage | Module | Input → output | Committed? |
|---|---|---|---|
| WP4.1 registry | `romeco.corpus.registry` | — → `registers/corpus/{items,relations,pipeline_state,acquisition_log}.csv` | yes |
| WP4.2 acquisition | `romeco.corpus.acquire` | `config/corpus_queue.yaml` → content-addressed cache `data/raw/corpus/<sha[:2]>/<sha>` | registry only (cache git-ignored) |
| WP4.3 parsing | `romeco.corpus.parse` | file → anchored units `data/interim/corpus/<item>/units.jsonl` | summary `registers/corpus/parse_manifest.csv` (text git-ignored) |
| WP4.4 extraction | `romeco.corpus.extract` | units → candidate quantities / ancient citations / author–date citations | `data/derived/corpus/extractions.csv` (snippets only where the rights register allows) |
| WP4.5 discovery | `romeco.corpus.discover` | bibliography pages → candidate works, citation resolution | `registers/corpus/discovery_candidates.csv`, `data/derived/corpus/citation_resolution.csv` |
| export | `romeco.corpus.export` | registers → `bib/library.{csl.json,bib}`, `bib/discovered.csl.json` | yes |
| WP4.6 benchmark | `romeco.corpus.benchmark` | seeded samples + gold → error rates | `benchmark/` |

**Pipeline states.** Eight states are tracked independently per source: discovered, screened, eligible, acquired, parsed, extracted, reviewed, unavailable (unavailable must carry a reason). `registry.validate()` blocks inconsistent states (e.g. parsed without acquired). Discovery never sets acquired; acquisition never sets reviewed.

**Rights gate.** Every item carries `rights_id` and `redistribute_text` (derived from the rights register).

- Parsed full text stays in git-ignored `data/interim/`.
- Committed extractions from non-redistributable sources (Adams 2007, Bowman & Wilson 2009) carry only the matched value, offsets and a SHA-1 of the context. Test-enforced; 2,837 such rows.
- The OpenEdition volume is logged as `blocked_by_environment`: its bot check is not bypassed.

## 2. Parse routes and anchors

| Route | Sources | Anchor | How it is validated |
|---|---|---|---|
| `pdf_text_layer` | Adams 2007, de Soto et al. 2025 | PDF page + printed page (folio offset fitted; Adams −15, 307 pages agree) | page images: **15/15 correct** across both benchmark samples, incl. a blank page and an unnumbered chapter opener |
| `pdf_ocr` | same, rasterised (300 dpi, tesseract 5.3.4 `eng`) | same | mean word confidence 94–95 % on born-digital pages; **no real degraded scan tested yet** |
| `flattened_text` | Nappo 2018, Bowman & Wilson 2009 (Project text extractions, no page breaks) | printed page, or **page range** where folios are missing (chapter openers) | contents-list headings: Nappo 14/16 exact; Bowman & Wilson 5/8 within range, 1/8 exact (headings sit on unnumbered openers). Not image-verifiable |
| `tei_cts` / `tei_milestone` | Mayhoff Pliny, Strabo (grc, en), Josephus, Tacitus | canonical locus (Pliny cited book.section, e.g. 6.102) + print-edition page breaks where encoded (Pliny v.1.p.473) | spot checks of loci used in the parameter register |
| `epidoc` | DDbDP TM 27666 | side.column.line | — |

## 3. What the benchmark shows (held-out, extractor v0.2 frozen)

Pooled over strata (excluding the OCR re-score), with Wilson 95% intervals. Small N throughout:

| Measure | Value | 95% CI | n gold |
|---|---|---|---|
| Quantity precision | 0.78 | 0.45–0.94 | 9 predicted |
| Quantity recall | 0.54 | 0.29–0.77 | 13 |
| Citation precision | 0.85 | 0.58–0.96 | 13 predicted |
| Citation recall | 0.48 | 0.29–0.67 | 23 |
| Page labels (image-checked) | 6/6 held-out, 15/15 overall | | |

The development set scores 1.0 after tuning. That is a fit, not an estimate.

**Error classes still open (v0.3 backlog, in order of impact):**

1. **Citations.**
   - Authors and series outside the lists: Procopius, Eusebius, *P. Ups. Frid.*, *P. Panop. Beatty*, *P. Mich. inv.*
   - List syntax: "PME, 21, 24" is two chapters.
   - A footnote number bleeding into a locus ("VI, 144.⏎114" → 6.144.114).
2. **Pliny's numerals.** The Perseus TEI keeps overlines inconsistently and drops the frame bars marking hundreds of thousands, so figures such as 4,765 or 1,300 miles cannot be recovered from the encoding (K22). Two gold values are reading-dependent and flagged.
3. **Quantity phrasing.** "10 silver talents" (adjective between numeral and unit); Latin number words.
4. **OCR.** It roughly halves citation recall on Adams pages (sigla damaged).

## 4. Consequences for using the corpus (D024)

- **Extractions are candidates, not evidence.** With held-out recall around 0.5, a missing extraction says nothing about absence in the source.
- **No numeric value enters `config/parameters.yaml` from an extraction without direct review** of the page image or edition. Pliny's distances in particular must be read from the printed edition.
- **Discovery is usable for literature mapping.**
  - 1,737 reference entries across 4 documents, giving 1,560 candidate works.
  - 58 works are cited by ≥2 of the 4 documents: the shared core.
  - In-text author–date citations resolve against the document's own bibliography at 85% (Nappo) and 81% (Bowman & Wilson).
  - Bibliographic-entry parsing accuracy is **not yet benchmarked**.

## 5. Not done in this pilot

- Crossref/OpenAlex enrichment and forward citation chaining (APIs not reachable from this environment).
- GROBID.
- Table structure extraction (Harper and Hanson are parsed as datasets in `romeco.context.manual`, not through this pipeline).
- A real poor-quality scan stratum.
- A multilingual OCR test (Italian, Greek or Latin models are installed but untested).
- Entity resolution of places and persons.
- **Independent human review of the gold set**, which is required for acceptance.
