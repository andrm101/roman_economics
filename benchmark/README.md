# WP4.6 extraction benchmark

Protocol (registered before annotation): `PROTOCOL.md`. Code: `romeco.corpus.benchmark`. Run with `ROMECO_TESSDATA=… python -m romeco.cli benchmark`.

## Files

| File | Content |
|---|---|
| `sample.csv` | development sample (seed 20261025): 42 units, 8 strata |
| `sample_heldout.csv` | held-out sample (seed 20261026): 28 units, no overlap with the development sample, drawn **after** v0.2 was frozen |
| `gold/`, `gold_heldout/` | gold annotations, one YAML per unit. PDF strata were annotated from page images, the others from text |
| `adjudication.csv` | gold corrections made after scoring: 1 so far, an annotator error in which the extractor was right |
| `results_v0.1.*` | extractor v0.1 on the development sample: the registered baseline |
| `results_v0.2_dev.*` | v0.2 on the development sample. **Optimistic: tuned on these errors** |
| `results_heldout_v0.2.*` | v0.2 on the held-out sample: **the estimate to quote** |
| `errors_*.csv` | every false positive and false negative, for inspection |
| `gold_review_sheet.csv` | **every gold item (149 rows), for the researcher's review** |

## Changes v0.1 → v0.2 (development-driven)

- **TEI overlines** kept, so Pliny's passus and milia passuum can be told apart. The "N p." default is flagged as rule `LAT_ROMAN_MP_DEFAULT`.
- **Number words:** English and Italian forms, and Greek number words with Greek unit nouns (gap of up to 4 words).
- **Citations:**
  - New series: *P. Kron.*, *PSI*, *P. Petrie*, *Chrest. W.*, *Dig.*, Gaius *Inst.*, dotted *CIL*.
  - Spaced abbreviations ("Strab . ,").
  - Ptolemy now requires *Geog.*
  - Implied-author continuation loci.

## Reviewing the gold set (needed for WP4 acceptance)

Open `gold_review_sheet.csv` and fill `reviewer_verdict` for each row with `ok`, `wrong` or `missing_item`. Put a corrected value or key in `reviewer_correction` and your initials in `reviewer`.

Priority rows are those whose `item_note` says **READING-DEPENDENT**: Pliny NH 6.156 and 6.27, which need the printed Mayhoff or Rackham.

The scorer will then be re-run against the reviewed gold.
