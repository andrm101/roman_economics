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

## 2026-10-24 — Session 4 (researcher-supplied datasets)

- Connected the researcher's folder C:/Users/andre/Desktop/Sandbox/Roman Econ System/Data (granted). Received: Itiner-e roads gpkg, Hanson 2016 Cities DB xlsx, Harper 2016 prices/wages/rents xlsx. Checksums registered (config/datasets.lock.yaml).
- Wrote `romeco.context.manual`: GeoPackage decoder (EPSG:3395 inverse ellipsoidal Mercator), Itiner-e road graph (networkx), Harper loaders and break analysis (E002), Hanson summaries.
- Results: Itiner-e Coptos–Berenike 402–408 km (all 'Conjectured'; K18); Coptos–Myos Hormos c. 182 km. Harper wheat: doubling confirmed (ratio c. 2.1; boot 1.79–2.50) but break only located to 160–187. Hanson: 47 Aegyptus cities in W2 (20 with area; Alexandria 972 ha vs AWMC footprint 1,061 ha; Coptos no area).
- Source-criticism: Pliny's Juliopolis–Coptos 309 mp is shorter than the great circle (646 km) → withdrawn as a distance (K17, D017).
- Licence policy for unlicensed datasets: aggregates only (D016).

## 2026-10-24 — Session 5 (legions, Adams 2007, Itiner-e paper, K12)

- **Legions replaced (D018).** Primary texts read verbatim from Perseus TEI: Strabo 17.1.12 (3 legions, 9 cohorts, 3 alae; Augustan), Tacitus Ann. 4.5 (AD 23: 25 legions, Egypt 2), Josephus BJ 2.387/2.494 (AD 66: two legions at Alexandria), 6.238 (AD 70). Dio 55.23–24 only as a machine summary. Nappo pp. 80–81 n. 305 contradicts his own p. 55: K16 resolved for W2. New derived tables: `legion_snapshots.csv`, `egypt_legion_series.csv`. Parameters egypt_legions_W1/W2.
- **Adams 2007 inspected (PDF supplied).** Camel load 6 artabas ≈ 400 lb (pp. 79–80) → camel_capacity_kg 181 [150, 200], now evidence-backed. Hire 4 dr/day (BGU III 921) and Western Desert freight 7.5 dr/talent (BGU III 697) give ≥45–48 dr per camel for Coptos–Berenike (p. 231; lower end). Supply confounders: Berenike c. 2,000 loads/month (Ruffing via Adams), Mons Claudianus c. 150 wheat loads/month (p. 209). Adams uses the superseded HS 7 m cargo value (K19).
- **Itiner-e paper inspected.** Eastern Desert roads are Desert Networks least-cost paths calibrated on modern caravan itineraries: the 402–408 km is a model output, not a survey length. Haversine route length matches the dataset's Shape_Leng (402.4 vs 402.1 km). The supplied gpkg declares EPSG:3395 (the paper describes EPSG:4326 for the main release).
- **K12.** Still present upstream (idp.data 41a1c87). Report drafted in docs/upstream_reports/; GitHub API access was refused in-session, so the researcher must file it. Proceeding with overrides (D019).

## 2026-10-24 — Session 6 (WP2: desert throughput, E003)

- Pliny NH 6.101–106 read in Mayhoff's text (Perseus TEI) with apparatus. Nile leg CCCVIIII, var. CCCIII: K17 is a transmitted-text problem. Desert stations and 257 mp (var. 258/254). Departure from India Tybi 1 – Mechir 6 (36-day spread). Pliny anchors upgraded from inspected_in_secondary to inspected.
- No sourced camel stock, water capacity or traffic count exists in the corpus (Adams, Nappo, Pliny searched). The WP2 criterion is not evaluable (D020). E003 was re-registered before running as descriptive partial identification.
- E003 results [calculated]:
  - H1a (N*lambda = 120) needs 128k–499k loads per season, and 3.5k–444k camels in continuous service depending on window, terminal and reading.
  - Monthly traffic is 5–208× Ruffing's Berenike supply estimate.
  - The desert freight lower bound is 0.5–2% of cargo value: desert cost does not bind for high-value cargo, but physical scale might.
  - All four pre-stated expectations held.
- Correction D021: Morelli whole cargo 213–219 t (not 195 t).
- K21 logged (Berenike supply 200–500 vs 2,000 loads/month).

## 2026-10-24 — Session 7 (WP2 follow-up: looking for a traffic count)

- Brun et al. (eds) 2018 (Collège de France, OpenEdition) read in the researcher's built-in browser (automated fetch is blocked by Anubis; not bypassed). From Reddé, Ast, Tomber:
  - Didymoi cistern storage grew from 120 to >380 m³ (storage, not yield).
  - Imports were assessed and stored at the ports by the paralemptes (supports E003's storage window).
  - Cameldrivers were organised in dekaniai (24 dekanoi in O.Berenike 3).
  - Traffic was controlled by passes.
  - No traffic count.
- HGV inventory (`romeco.ingest.hgv_inventory`, idp.data 41a1c87): 2,630 Eastern Desert documents. The trade-port archives are 1st-century; the W2 record is quarry and fort ostraca. Only 73 W2 documents are month-dated. D022: no documentary route to the H1a capacity criterion.

## 2026-10-24 — Session 8 (WP4 corpus pilot)

- **Built `romeco.corpus`.** Registry (8 independent states, rights gate), resumable content-addressed acquisition (13 items; OpenEdition logged as blocked), parsing over 5 routes with page, page-range or locus anchors, rule-based extractors (v0.1 → v0.2), offline citation-chaining discovery, and CSL-JSON/BibTeX export. CLI: `corpus`, `benchmark`.
- **Corpus outputs.**
  - 6,007 extraction candidates; 2,837 from all-rights-reserved sources carry no text.
  - 1,737 bibliography entries → 1,560 candidate works, 58 cited by ≥2 documents.
  - In-text citations resolve against the document's own bibliography at 85% (Nappo) and 81% (Bowman & Wilson).
- **Benchmark (E004).**
  - Protocol registered before annotation; development sample of 42 units and held-out sample of 28 (disjoint, drawn after freezing v0.2).
  - Held-out: quantity recall 0.54, citation recall 0.48; page labels 15/15 on image-checked pages.
  - One gold error was found in adjudication: the extractor was right.
- **Findings.**
  - Overline and frame encoding defects in Perseus Mayhoff (K22).
  - Periplus list-syntax and footnote-bleed citation errors (v0.3 backlog).
  - Bowman & Wilson chapter openers are unnumbered, so pages there are anchored as ranges.
- **Decisions:** D023–D025. WP4 acceptance is provisional pending review of `benchmark/gold_review_sheet.csv`.

## 2026-10-24 — Session 9 (WP9 semantic foundation)

- Competency questions CQ6–CQ11 registered with golden answers before the graph existed (`docs/competency_questions.md`).
- Minimal ontology (`ontology/romeco.ttl`, 0.1.0) reusing PROV-O and SKOS. Alignment to CIDOC CRM 7.1.3, CRMinf 1.2.1 and OWL-Time documented, not imported (D026).
- SHACL shapes for claims, parameters, questions, candidates, place identifications, derivations, file items and rules.
- Curated `questions.csv` (8 points of contention), `derivations.csv` (9 derivations, 3 experiments) and `document_keys.csv` (14 documents).
- New conversion rule CR-WT-MOD-001 (avoirdupois lb → kg, exact) and status `modern_definition`.
- Builder `romeco.semantic.build` and CLI `graph`. The DuckDB store stays canonical (D027). Support vs considered is split by question selection (D028). Candidates link only via `possiblyBearsOn` (D029).
- Acceptance: 17 tests (round trip, rivals, SHACL positive + 5 negatives, CQ6–CQ11). All CQ answers matched the pre-registered expectations after two query fixes: subclass typing without inference, and editions excluded from CQ11 citation counts. Suite: 128 passed.
- Date correction D030.

## 2026-10-25 — Session 10 (expansion brainstorm and documentation)

- Researcher request: expand to a "digital twin" of the Roman world, covering wars, plagues, temperature, barbarian and enemy accounts, and technology, as documentation for a future Claude Code agentic deployment.
- Pushback recorded (D031): evidence twin, not digital twin; ingestion gated per domain.
- Wrote `docs/expansion/00–05`:
  - charter;
  - domain map (9 domains, link register L01–L08);
  - ontology 0.2.0 draft, time model and storage;
  - question bank RQ-X1–X8, with RQ-X1 recommended;
  - agent roles AG-* with gates and guardrails;
  - roadmap WP10–WP18.
- 32 candidate sources recalled from knowledge and registered as `unverified_candidate` only. None is inspected.
- Not done: Claude Code configuration (Part 2).

## 2026-10-25 — Session 11 (Part 2: Claude Code agent harness, WP11)

- Read the current Claude Code docs (sub-agents, hooks, skills, permissions) and wrote the configuration against them:
  - 11 subagents;
  - 5 skills;
  - `settings.json` with one PreToolUse hook, deny rules and bypass mode disabled;
  - the policy file;
  - task template plus two proposed tasks (T-WP11-001 dry run; T-WP10-001 time model);
  - review-decision and rights-proposal registers;
  - review-packet generator;
  - `agents-check` CLI.
- `agents-check` caught unquoted YAML in all 11 agent files (`description: Acquisition: …`). Claude Code would have skipped those files silently. Fixed.
- `tests/test_agents.py`: 52 tests. Planted violations are denied: unapproved promotion, access-status upgrade, human-only paths for every role, held-out peeks (Read/Grep/Bash), force-push, destructive git, commit on main, network without grant, shell writes to human-only paths. Legitimate actions pass.
- Not done: no live Claude Code run of the subagents or hook; manifest-before-run is not hook-enforced (D032; `06_claude_code_deployment.md` §3).
