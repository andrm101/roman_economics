# WP4.6 extraction benchmark: protocol (registered 2026-10-25, before annotation)

**Purpose.** Characterise extraction error by stratum (WP4 acceptance test). This is a measurement of the *pipeline*, not of the historical evidence.

## Strata and sampling frames

The sample is drawn by `romeco.corpus.benchmark.draw_sample(seed=20261025)` and written to `benchmark/sample.csv`.

| Stratum | Route | Language | Document | Frame | n |
|---|---|---|---|---|---|
| S1 | pdf_text_layer | en | monograph (Adams 2007) | printed pp. 3–291 (excl. front matter, bibliography, indices) | 6 pages |
| S2 | pdf_text_layer | en | journal article (de Soto et al. 2025) | PDF pp. 1–16 (before the reference list) | 3 pages |
| S3 | pdf_ocr | en | monograph (Adams 2007) | the S1 pages, rasterised at 300 dpi, tesseract `eng` | 6 pages |
| S4 | flattened_text | it | monograph (Nappo 2018) | units with printed page 11–180, not bibliography | 5 pages |
| S5 | flattened_text | en | edited volume (Bowman & Wilson 2009) | units with printed page ≥ 3, not bibliography | 5 pages |
| S6 | tei_cts | la | critical edition (Pliny NH, Mayhoff) | book 6 sections | 8 sections + fixed 6.102 |
| S7 | tei_cts | en | translation (Strabo, Hamilton–Falconer) | book 17 sections | 5 sections |
| S8 | tei_cts | grc | critical editions (Strabo, Josephus) | Strabo 17.1 sections | 2 sections + fixed Josephus BJ 2.387 |

Fixed inclusions (6.102, BJ 2.387) are loci used in the parameter register. They are scored with the rest but also reported separately.

## What counts (annotation guideline)

- **Quantity.** A numeral attached to a measurement, count or currency unit in the controlled list (`romeco.corpus.extract.UNITS`, plus HS).
  - The numeral may be digits, Roman numerals or number words (EN/IT/LA/GRC); the gold set records `numeral_form`.
  - A range is one item (low, high).
  - Excluded: years and dates, page/line/footnote numbers, citations, ordinals, and bare numbers with no unit.
- **Ancient citation.** A locus in an ancient author (author + work + locus) or a documentary edition siglum with a number (papyrus, ostracon, inscription). Keys use the extractor's normalisation (series lower-case without dots or spaces; Roman volume → Arabic; literary key `author.work:book.chapter.section`).
- **Page label (S1–S3).** The printed folio as seen on the page image.

## Gold annotation

- **S1–S3:** the gold is made from **page images** (300 dpi renders), not from the text layer.
- **S4–S5:** no page images exist, so the gold is made from the text. Page anchors there are **not** independently checkable and are not scored.
- **S6–S8:** annotated from the TEI text.

The annotator is the assistant that wrote the extractors, so the benchmark is **not independent**. Every gold file carries `review_status: assistant_annotated_pending_human_review`. WP4 acceptance requires the researcher to review `benchmark/review_sheet.csv`.

## Metrics

Per stratum × kind: TP/FP/FN, precision, recall and F1, with Wilson 95% intervals.

- **Quantity — strict match:** same unit and same low/high values (tolerance 1e-6).
- **Quantity — lenient match:** same values, unit ignored.
- **Citations:** exact key match.
- **Page labels:** accuracy.

Small samples: intervals are reported, and a stratum with fewer than 10 gold items is flagged as indicative only.
