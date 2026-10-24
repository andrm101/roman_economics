# Research log

## 2026-10-24 — Session 1 (WP0)

- Repository was empty; created the scaffold, registers, schema, M0 package, tests and experiment E000.
- Identified the two project PDFs: Nappo 2018 (CC BY 4.0) and Bowman & Wilson (eds.) 2009 (OUP, all rights reserved). The "synthesis" referenced in the project brief is **not** present.
- Read Nappo pp. 13, 40–48, 58–59, 86–94; Wilson 2009 pp. 216–217; Rathbone 2009 pp. 316–318.
- Read De Romanis 2012 only through an automated summary of the PDF (labelled accordingly).
- Reproduced Wilson 2009: 217 n. 6 exactly (HS 9,235,803 gross; HS 2,308,951 tax). Found that the six-item reconstruction sums exactly to Morelli's reading (circular by construction).
- E000: receipts envelope HS 14.1 m–415.6 m; the lower bound is independent of the Hermapollon.
- Corrected an initial misstatement: the O.Berenike passes concern **exports** from Berenike and are mostly 1st c. CE.
- Blocked: O.Berenike 4 landing page (bot protection), Wilkinson 2021 thesis (robots). Both need manual retrieval.
- Next: WP1 (Hermapollon documentary audit against EpiDoc + De Romanis 2020).

## 2026-10-24 — Session 2 (WP1: Hermapollon documentary audit)

- Partial clone of papyri/idp.data (commit f03d0f3…); located SB XVIII 13167 = TM 27666 (DDbDP/27/27666.xml; HGV28/27666.xml). Snapshot committed with checksums (CC BY 3.0).
- Wrote `romeco.ingest.epidoc` (line-anchored text + encoded numerals) and generated `data/curated/pvindob_g40822_numerals.csv` (91 numerals, 86 lines).
- Inspected readings: total 1,151 T 5,852 dr (v ii 29); 'value of three parts' (v ii 27); quarter shares listed in v col. i. HGV date: mid-2nd c. (126–175, low precision).
- Reproduced the papyrus's own procedure exactly for nard, ivory and schidai (surcharge, litrai truncation, merchants' talent, truncation to minae). Lost merchants' talent identified from rounding: (97.497, 97.510] litrai.
- 'Arabarch rates' (0.25 %, 2.88 %) are ratios of surplus quantities, not statutory rates (K14).
- Pepper: value preserved; price disputed (6 vs 24 dr/mina, De Romanis 2014 via machine summary). Morelli's price reproduces the DDbDP numeral at v i 21 exactly. Pepper mass ×4; whole weighed cargo c. 625 t vs c. 195 t (≈×3.2) — the most likely source of the brief's 'threefold disagreement' (K3).
- Two DDbDP encoding issues logged (K12); code overrides them and tests will flag upstream fixes.
- WP1 acceptance: primary readings now `inspected`; 4 interpretive assertions remain `machine_summary_only` (De Romanis 2012/2014). Blocked: shell access to ISAW Papers 8 (allowlist). Needs direct reading or researcher review before WP1 can be closed.
- E000 rerun with rejected interpretation excluded: baseline receipts HS 18.4 m–414.7 m; envelope unchanged (HS 14.1 m–415.6 m). E001 added (pepper mass scenarios).

## 2026-10-24 — Session 3 (context layer: legions, cities, roads, prices/inflation)

- Researcher asked to track legions, cities, roads and inflation. Only GitHub is reachable from this environment; Zenodo, OxREP, DARMC, Wikidata, Pleiades site, ISAW are blocked.
- Fetched with pins and checksums: Pleiades GIS tables (CC BY 3.0), AWMC geodata (ODbL), ORBIS v2 (MIT). Registered Itiner-e, Hanson Cities DB, Harper price DB, ISIS silver data as manual downloads.
- Read and anchored (pages re-verified by code): Rathbone 2009 Tables 15.1–15.2 and pp. 305–313; Ponting 2009 pp. 273–277; Hitchner 2009 p. 282; Nappo 2018 pp. 53–57, 78–80, 182–187. Corrected four page numbers during verification.
- Built `romeco.context`: pilot gazetteer (45 places, all resolved), Eastern Desert military installations (99; 58 active 100–200 CE), Egypt settlements, AWMC road lengths, ORBIS pilot edges, urban footprints, legion bases (29/32 joined), price deflators.
- Findings: ORBIS v2 road time = km/30 (not evidence; D013); ORBIS 'Nicopolis' identity trap (D014); W1 (70s on) and Hermapollon in one stable price band; P(Hermapollon after price break) ≈ 0.06 [assumption-dependent]; Hitchner vs Ponting fineness conflict (K15); III Cyrenaica location conflict (K16).
- Tests: 62 passing.
