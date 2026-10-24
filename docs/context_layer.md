# Context layer: legions, cities, roads, prices/inflation (v0.2, 2026-10-24)

Purpose: track four families of conditioning variables requested by the researcher. They enter the pilot as **constraints, confounders and deflators** for RQ1; they do not open a new research question (D012).

Claim tags: **[sourced]**, **[calculated]**, **[assumption]**. All derived tables are in `data/derived/context/`, rebuilt with `python -m romeco.cli fetch && python -m romeco.cli context`.

## 1. What was acquired (pinned, checksummed)

| Track | Dataset | Route | Status | Licence |
|---|---|---|---|---|
| Cities, forts, stations, roads (gazetteer) | Pleiades GIS tables (commit `6df2361`) | GitHub | fetched, 40 MB | CC BY 3.0 |
| Roads, urban footprints, provinces | AWMC geodata (Barrington-derived; commit `7ecf8bc`) | GitHub | fetched, 7 MB | ODbL |
| Route network (model) | ORBIS v2 sites + routes (commit `6588111`) | GitHub | fetched, 4 MB | MIT (code); data rights unclear |
| Roads (high resolution) | Itiner-e static 2024, v1.3 (DOI 10.5281/zenodo.17122148) | researcher-supplied (sha256 `1b9470aa…`) | **read, 14,769 segments** | CC BY 4.0 |
| Cities (area, status, monuments) | Hanson 2016 Cities Database (DOI 10.5287/bodleian:eqapevAn8) | researcher-supplied (sha256 `5b9fc019…`) | **read; aggregates only committed (D016)** | not stated |
| Prices / wages (Egypt) | Harper 2016 DARMC xlsx (companion to Harper 2016, *JEH* 76: 803–39) | researcher-supplied (sha256 `167a62be…`) | **read; aggregates only committed (D016)** | not stated |
| Coin fineness | Ponting et al. 2021 ISIS dataset (DOI 10.5286/ISIS.E.98003576) | ISIS | **blocked; probably raw spectra** | CC BY 4.0 |
| Legions | No open structured dataset reachable. Provisional c. 150–165 table extracted from Wikipedia (machine summary) | web | scaffold only | CC BY-SA |

Plus curated anchors read directly in the two project books (`data/curated/context/*.csv`, every page re-checked programmatically).

## 2. Legions and garrisons

**Inspected anchors (Nappo 2018) [sourced]:**
- Myos Hormos garrison of 50–100 under a *curator praesidii*, early 1st c. to c. 125 (p. 53).
- Eastern Desert praesidia of 22–24 men each (p. 57).
- II Traiana Fortis in Egypt by 128 and the sole legion of the province from Antoninus Pius (p. 80); a vexillation on the Farasan islands in 143–144 (pp. 78–80).
- Nappo places III Cyrenaica at Coptos until Caracalla (p. 55). This **conflicts** with the provisional disposition table, which puts it at Bostra c. 150–165 (K16).

**Derived [calculated]:**
- **Eastern Desert installations.** Pleiades lists 99 fort/station places in the Eastern Desert box; 58 have dated locations overlapping 100–200 CE, and 36 are undated.
- **Legion bases.** 29 of 32 provisional legion entries have a base resolved to Pleiades through a reviewed crosswalk (`place_crosswalk.csv`, status `project_match_unreviewed`).
- **Pay as a fiscal scale.** Legionary pay of HS 1,200 a year (AD 85 – Severus; Rathbone 2009: 311) turns the E000 receipts envelope (HS 14.1 m – 415.6 m) into roughly **12,000 – 346,000 soldier-years of pay** **[calculated; conditional]**. This compares fiscal receipts with the cost of a garrison whose size is **not yet sourced**.

**Why it matters for RQ1.** Garrisons and quarries draw supplies over the same desert roads. They are the main confounder for the desert-throughput test of H1a/H1b. The praesidia network is also the infrastructure whose cost Nappo and Tomber disagree about (K5).

## 3. Cities

- **Settlements.** Pleiades has 734 settlement/urban places in the Egypt box; 506–533 are dated active in the windows, 86 undated. These are gazetteer presence counts, not populations.
- **Urban footprints.** AWMC gives 95 Barrington-derived footprints. Alexandria is 1,061 ha, against Rome's 1,317 ha **[calculated from polygons]**. Footprint is not inhabited area.
- **Hanson 2016 [calculated from the database]:** 47 Aegyptus cities active in W2, 20 with an area estimate (sum 3,403 ha, median 139 ha). Alexandria 972 ha ("urban grid") — 9% below the AWMC footprint. Arsinoe 288, Oxyrhynchus 170, Hermopolis 155, Antinoopolis 138 ha. **Coptos has no area estimate**, so the Nile–desert transfer node cannot be sized from this source.
- **Role in the pilot.** Size of the Alexandria demand/transit node (M1 demand scale); Coptos and the Red Sea ports as nodes in the gazetteer (`pilot_gazetteer.csv`, 45 places, all resolved).

## 4. Roads

- **Coptos–Berenike length agrees across three sources:** Pliny 257 mp ≈ 380 km; Nappo "quasi 400 km" (p. 57); ORBIS geometry 379.5 km. They **share lineage**, so this is agreement, not confirmation.
- **Itiner-e (network shortest path, snapped graph) [calculated]:** Coptos–Berenike **402–408 km**, all segments `Conjectured` (Desert Networks lineage); Coptos–Myos Hormos **c. 182 km** (ORBIS 170). A 6–7% gap with Pliny/ORBIS (K18); `route_desert_km` bounds widened to [380, 409].
- **Pliny's Juliopolis–Coptos 309 mp (≈457 km) is physically impossible as a river distance:** the great-circle distance alone is 646 km [calculated]. Withdrawn as a parameter value (K17, D017); `route_nile_km` is now exploratory with lower bound 646.
- **Finding: ORBIS v2 road "time" is not evidence.** On every road edge `field_s` = km ÷ 30.0 and `field_e` = 1.05 × `field_s` (tested). The 12.6 "days" for Coptos–Berenike, close to Pliny's 12, is a 30 km/day assumption (D013).
- **AWMC roads:** 3,010 km of segments touch the Eastern Desert box. Nappo gives 2,000–2,200 km for the seven main desert roads (p. 55). The box also catches minor and Nile-edge roads, and AWMC roads are **undated**.
- **ORBIS identity trap:** its "Nicopolis" is the Epirote city. Edges are now selected by geography, never by label (D014).

## 5. Prices and inflation

**Inspected anchors [sourced]:**
- **Egyptian farm-gate wheat:** 6–12 dr/artaba (median 9) in the AD 80s–160s; 12–20 (median 16) in the 190s–250s (Rathbone 2009: 304–305).
- **The break between them:** an abrupt doubling at some point from the 160s to the 190s. Its link to the Antonine plague is disputed (pp. 305–306; Nappo 2018: 184).
- **Wages:** craftsmen's pay about 2 dr/day in the mid-2nd century (Mons Claudianus; Rathbone 2009: 312–313).
- **Empire-wide rates:** under 1% a year before the break (Nappo 183); about 4% a year for 150–300 per Temin (Nappo 185).
- **Debasement path:** silver coinage about 1% fine c. 270; Aurelian's 274 reform, then a price surge (Nappo 184–185).
- **Denarius fineness:** two inconsistent series in the same volume (K15). Hitchner (p. 282) gives 94 → 88% from Nero to Pius, then 78 / 74 / 55 / 51 / 45%. Ponting (p. 274) measures 80% in heart-metal after the 64 reform.

**E002 re-derivation on Harper's database [calculated]:** 33 dated wheat prices, 1–275 CE. A two-regime step model gives ratio **c. 2.1** (bootstrap 5–95%: 1.79–2.50; 26 tightly dated items: 1.65–2.39) and reproduces the band medians 9 and 16 dr/art. The break is **only located to 160–187**: no observation falls in that interval, so every candidate τ in it fits equally. Harper and Rathbone draw on the same papyri, so this is a re-derivation, not independent confirmation.

**Consequences for the pilot [calculated / assumption]:**
- W1 (from the 70s) and the Hermapollon (126–175) fall in the **same stable price band**. Nominal comparisons between them need no deflator. Augustan–Neronian evidence before the 70s has no Egyptian price anchor here.
- With uniform dating assumptions, the probability that the Hermapollon post-dates the break is **0.06**.
- Denarius debasement is **not** an Egyptian price index. Egypt ran a closed billon-tetradrachm system, so the denarius series is empire context only.

## 6. Gaps and next actions

1. **Done:** Itiner-e, Hanson, Harper received and integrated. Outstanding: Itiner-e field description docx (certainty/date field definitions); licences for Hanson and Harper before any row-level release.
5. **Nile distance (K17):** find a sourced Juliopolis–Coptos river distance or a reading/unit explanation of Pliny's 309 mp.
2. **Legion dispositions:** replace the Wikipedia scaffold with a scholarly list. The best primary anchor is the c. AD 165 inscription listing legions by province (ILS 2288), plus a modern disposition table.
3. **Egypt garrison size:** needed before the pay-scale comparison means anything. Candidate sources are cited by Nappo (Daris 2000; Cuvigny; Bagnall 1986).
4. **Tetradrachm fineness series** for Egypt (closed currency): not found in reachable open data.
