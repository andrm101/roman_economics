# Research Design v0.1 — Pilot P1: Roman Egypt, the Red Sea and India (c. 50–200 CE)

*Status: proposal + implemented baseline; WP1 substantially done (see §9). Date: 2026-10-24. Author of record: Andrei Manoloiu; drafted with Claude.*

Claim tags: **[sourced]** = traceable to a registered source and locus; **[calculated]** = produced by code in this repo (reproducible with `python -m romeco.cli …`); **[assumption]** = a project choice or exploratory bound. "Inspected" always means the text was read; machine summaries and abstracts are labelled as such (see `registers/source_register.csv`, column `access_status`).

---

## 0. Summary and recommendation

**Recommended first question (RQ1).** *Which joint configurations of fleet size, cargo-value distribution, venture costs, losses and tax collection are consistent with the documented anchors of the Egypt–India trade, what bounds do they imply for annual quarter-tax receipts and merchant break-even margins, and which single additional observation would shrink those bounds most?*

This narrows the provisional first question (information/credit frictions vs. a transport-and-tax equilibrium). The audit below shows that the pilot evidence contains **no matched price series across the route and one surviving loan contract**. That evidence cannot discriminate information or credit mechanisms, so per the brief the contribution moves to feasibility bounds and identification. The friction question stays alive as a methodological M1/M2 comparison (§7), not as a historical estimate.

**First results already in the repo (conditional, not historical estimates):**

- The canonical Hermapollon figures (Wilson 2009: 217 n. 6, after Rathbone) reproduce exactly: residual HS 6,926,852 → gross HS 9,235,803 → quarter-tax HS 2,308,951 **[calculated]**. After WP1 the baseline uses the principal-edition reading 1,151 T 5,852 dr → gross HS 9,215,803 (D008).
- Choosing between the two transcribed readings of the total moves gross value by 0.22 %. Choosing between interpretations (residual three-quarters vs. whole taxable base) moves it by exactly 25 % **[calculated]**. Interpretation dominates reading uncertainty.
- Combining Strabo's 120 ships, the Hermapollon and Pliny's ≥ HS 50 million outflow bounds annual quarter-tax receipts only to an envelope of **c. HS 14 million to HS 416 million** (factor ≈ 29) across the registered parameter bounds **[calculated]**. The naive "120 Hermapollons" product, HS 277 million, is one point inside it.
- Structural result: the **lower** bound equals τ·κ_min·M_min·O. It is pinned by Pliny's outflow and the cost structure, and the Hermapollon cancels out. The Hermapollon enters only the **upper** bound, through an unsupported assumption about how typical it was (λ) **[calculated]**.
- A physical test can discriminate. Under De Romanis's reading the Hermapollon's weighed cargo is c. 468 t as valuated, c. 624 t whole, or c. 3,100 camel loads at an exploratory 200 kg per load; under Morelli's reading it is c. 213–219 t (c. 1,100 loads at 200 kg; corrected from 'c. 195 t', D021) — see §9 and D011. "120 Hermapollon-size cargoes per season" implies c. 374,000 desert camel loads per season. A modern estimate of Berenike's own supply traffic is 200–500 loads per month (Nappo 2018: 58–59) **[calculated / sourced / assumption]**. Desert throughput is therefore the most promising discriminating evidence (WP2).

---

## 1. Scientific objective and possible original contributions

**Objective, restated.** Determine which mechanisms can jointly reproduce a small set of independent evidence patterns for the Egypt–India trade, which of those mechanisms the surviving evidence can tell apart, and where only conditional bounds are defensible. This is not a reconstruction of trade volume or of "Roman GDP".

**Candidate contributions, ranked by defensibility:**

| # | Contribution | Why it could be original | Main risk |
|---|---|---|---|
| C1 | Formal accounting of the Red Sea fiscal–commercial chain that separates stated valuation, residual value, tax base, liability, collection and outflow, plus a partial-identification analysis of the anchors usually multiplied together in the literature | Makes explicit an inference that is usually done informally (ships × cargo × rate). Produces a testable physical constraint (desert throughput) | Prior revenue calculations (e.g. Wilkinson 2021, Cobb 2018, De Romanis 2020) may already do part of this. **Not yet checked; WP3 is a hard gate before any originality claim** |
| C2 | Reusable, lineage-explicit evidence base for the Egypt–India documentary corpus (P.Vindob. G 40822, O.Berenike, Nikanor archive, Coptos tariff, Periplus) | Distinguishes readings, interpretations and project derivations; counts independent primary documents per parameter | Valuable infrastructure, but not a scholarly contribution on its own |
| C3 | Matched M1/M2 comparison of the monsoon-imposed one-season information lag | Natural, historically grounded friction; well-defined limiting case (lag → 0) | Likely ends in observational equivalence given the data. Acceptable if reported as such |

The following are explicitly **not** contributions: choosing a new region, building a larger corpus, or using an ABM.

---

## 2. Feasibility audit of the supplied material

### 2.1 What was actually supplied

| Project doc | Actually is | Access | Rights | Relevance |
|---|---|---|---|---|
| `Roman Trade Economics_Red Sea + Far East.pdf` | **Nappo, D. 2018.** *I porti romani nel Mar Rosso da Augusto al Tardoantico.* FedOAPress (Clio 20). ISBN 978-88-6887-034-8, DOI 10.6093/978-88-6887-034-8 | Full text; sections pp. 13, 40–48, 58–59, 86–92 read | CC BY 4.0 (front matter) | High: the port system, taxation (tetarte, arabarchs, Coptos tariff) and the Nikanor archive, with full Greek and Latin citations |
| `Quantifying the Roman Economy_ Methods and Problems.pdf` | **Bowman, A. and Wilson, A. (eds.) 2009.** *Quantifying the Roman Economy: Methods and Problems.* OUP. ISBN 978-0-19-956259-6 | Full text; Wilson ch. 9 pp. 216–217 and Rathbone ch. 15 pp. 316–318 read | All rights reserved; private research use | Methods. Red Sea material is incidental but important (the HS 9.2 m gross-up) |

**Critical gap.** The brief repeatedly refers to an "uploaded synthesis" with a "threefold Muziris cargo-valuation disagreement". **That document is not in the project.** Both files are primary scholarly books, not a synthesis. The threefold claim therefore cannot be audited directly. What can be established from inspected material **[calculated]**:

- The two transcribed readings of verso col. ii l. 29 differ by 15,000 dr (0.22 %): 1,154 T 2,852 dr (editio princeps, as reported by Nappo 2018: 88 n. 332) vs. 1,151 T 5,852 dr (Morelli's reading as used by De Romanis 2012: 77; machine summary only).
- Residual-vs-whole-base interpretation changes gross value by exactly 25 %.
- The drachma↔HS step is a nominal 1:1 convention (CR-MON-EG-003), so it cannot create a factor of 3.
- **Residual value ÷ quarter-tax = 0.75/0.25 = 3 exactly** (6,926,852 / 2,308,951 = 3.000). A synthesis that compared the residual cargo value with the state's take as if both were "cargo valuations" would show a spurious threefold disagreement. This is a hypothesis about the missing document, not a finding.
- **Stronger candidate (WP1):** the two published readings of the pepper entry (Morelli 24 dr/mina vs De Romanis 6 dr/mina plus a lost myriad) leave cargo *value* unchanged but change whole weighed cargo *mass* by ≈2.85× (c. 219 t vs c. 624 t; D021) **[calculated; malabathron term approximate]**. A synthesis reporting this as a 'valuation' disagreement would misstate a mass disagreement.

### 2.2 Evidence inventory for the pilot (inspected vs. cited)

| Evidence | What it can bear on | Project access | Note |
|---|---|---|---|
| P.Vindob. G 40822 (= SB XVIII 13167), recto | Financing, logistics chain Muziris→Red Sea port→Coptos→Alexandria, agents | Via Nappo's quotation only | One contract: tells us a structure, not a population distribution |
| P.Vindob. G 40822, verso | One cargo's valuation, tax base, commodity mix, official weight talents | Via Nappo (total, 3 items) and a machine summary of De Romanis 2012 (6 items) | Item-level reconstruction is partly conjectural (pepper, malabathron reconstructed; tortoise-shell price proposed from Diocletian's Edict) |
| Strabo 2.5.12; 17.1.13; 17.1.45 | Fleet size (120), "double" duties, route to Coptos | Via Nappo's Greek text and translation | Augustan, i.e. before the pilot window: requires a transfer assumption |
| Pliny *NH* 6.101–104; 12.84 | Outflow (HS 50 m; HS 100 m), itinerary (309 mp / 12 d; 257 mp / 12 d), sailing season | Via Nappo's Latin text | Moralising; numerals not checked against a critical edition |
| Periplus Maris Erythraei 19 | 25 % at Leuke Kome | Via Nappo | Casson 1989 not inspected |
| OGIS II 674 (Coptos tariff, 10 May 90 CE) | Tolls on persons/animals; arabarch collection at Coptos | Via Nappo | Tolls on movement, not on cargo value |
| Nikanor archive (O.Petr. 220–304 etc., 6 BCE–62 CE) | Camel transport to Berenike and Myos Hormos | Via Nappo (counts) | Nappo argues it is unusable as trade-volume evidence |
| O.Berenike (c. 260 published ostraka in Bagnall et al. 2000, 2005; a fiscal subset are passes for goods **exported** from Berenike, mostly 1st c. CE) | Outbound consignments, departure seasonality, customs procedure (duties paid in the valley, control at the Berenike gate) | Via Nappo 2018: 92–94 only; editions **not inspected**; O.Berenike 4 landing page blocked by bot protection | Priority dataset; likely in idp.data. Bears on the outbound leg, not return cargoes |
| Berenike/Myos Hormos excavation reports | Assemblages, phasing, Indian presence | Cited only; popular summary (Smithsonian 2024) logged | Small excavated fraction: an observation-model issue |
| Harper 2016 price/wage geodatabase (DARMC) | Egyptian wheat, wage, rent, land prices | Abstract + summary | Local Egyptian prices, not India-trade commodity prices |
| Modern models: ORBIS; Gal et al. 2023 sailing mobility; Copeland 2022 gravity model | Route costs/times; wind feasibility | Metadata / summary | Model outputs ≠ trade observations |

### 2.3 Contradictions and lineage issues found (see `registers/contradiction_register.md`)

K1 rival readings of the total; K2 Nappo's "imponibile" wording vs. the three-quarters residual reading; K3 popular "140 t of pepper" vs. c. 544 t whole-cargo pepper implied by De Romanis 2012's reconstruction; K4 unsourced "10–33 % of tax revenue" claim; K5 Nappo (heavy state investment in desert infrastructure) vs. Tomber 2018 as summarised by BMCR (little investment in port infrastructure), probably a difference of scope; K6 Nappo's 11.29 % share for the three surviving items vs. 11.33–11.36 % recomputed; K7 Rathbone 2000 cited as 2001; K8 literary port primacy vs. the Nikanor archive trend; K9 ambiguity in Strabo's 120 ships; K10 single vs. double 25 % levy.

**Independence warning.** Wilson 2009, Rathbone 2000, De Romanis 2012/2020, Nappo 2018 and the Smithsonian article all rest on **one** papyrus for cargo value. `CQ3` returns `n_primary_documents = 1` for `A_H`.

---

## 3. Three tractable research questions

| Rank | Question | Tractability | Evidence that can bear on it | Model rung |
|---|---|---|---|---|
| **1 (recommended)** | RQ1 — fiscal–commercial consistency and bounds (see §0) | High | P.Vindob. G 40822; Strabo; Pliny; Coptos tariff; O.Berenike; desert-route capacity | M0 → M1 |
| 2 | RQ2 — Berenike vs. Myos Hormos: do transport time/seasonality (windward sailing up the Red Sea vs. longer desert road) explain shifting port use, or are institutional/military factors needed? | Medium | Literary port mentions; Nikanor counts; O.Berenike; excavation phasing; Gal et al. 2023 Red Sea sailing metrics | M0 with routing; observation model is decisive |
| 3 | RQ3 — credit and seasonal liquidity: under which interest, collateral and loss conditions does financing bind participation? | Low–medium | One loan contract; general maritime-loan practice (outside region → transfer assumption) | M0 finance block → M2 credit ablation |

Deferred: commercial information frictions as a *historical* hypothesis. There are no matched price observations.

### 3.1 Hypothesis matrix for RQ1

| Field | H1a "Hermapollon-typical fleet" | H1b "Hermapollon-exceptional" |
|---|---|---|
| Mechanism | Many large ventures; trade volume and receipts scale with N ≈ Strabo's order of magnitude, λ ≈ 1 | Few very large ventures plus many smaller ones; λ ≪ 1 |
| Scope / unit | Egyptian Red Sea ports, sailing season, 2nd c. CE (papyrus date) with transfer to 1st c. flagged | same |
| Empirical signature | Receipts of order 10⁸ HS; c. 3,000+ camel loads per return cargo; seasonal desert traffic of order 10⁵ loads | Receipts of order 10⁷ HS; desert traffic compatible with port-supply-scale caravans |
| Needed evidence | Camel capacity and hire (Adams 2007); caravan sizes; outbound pass counts as a lower bound on desert traffic (O.Berenike, 1st c.: transfer assumption); harbour capacity; ship-size evidence | same; plus any second cargo valuation |
| Implementation | M0 `fiscal` + desert-throughput constraint | same, with a λ distribution |
| Discrimination criterion | Reject H1a if the sourced desert-throughput capacity over the return window < required loads for N·λ near its upper range | Reject H1b only if a lower bound on receipts from an independent fiscal source exceeds its range |
| Confounders | Myos Hormos as a second terminal; Nile/desert capacity shared with the Mons Claudianus/Porphyrites quarry supply; multi-crossing camels; mass ≠ value (λ scales value, not weight) | same |
| Historical hypothesis vs. modelling convenience | λ is a historical quantity; the uniform λ is a convenience | — |

**Pre-registration (before fitting):** desert-throughput evidence is reserved for evaluation and is not used to set λ. O.Berenike seasonality is reserved for M1/M2 evaluation. Revisions go in `registers/decision_log.md`.

---

## 4. Pilot specification

| Item | Default | Rationale |
|---|---|---|
| Region / nodes | Muziris (aggregate Malabar supply), Red Sea passage, Berenike, Myos Hormos, Coptos, Alexandria; external: Indian sellers, Mediterranean buyers | Matches the recto's logistics chain [sourced: Nappo 2018: 87] |
| Period | 50–200 CE, analysed as **two evidence windows**: W1 c. 30 BCE–90 CE (Strabo, Periplus, Nikanor, Pliny, most O.Berenike passes, Coptos tariff of 90 CE at the boundary) and W2 c. 100–200 CE (P.Vindob. G 40822) | The evidence does not support an annual series. The return-cargo valuation (W2) and the outbound passes (W1) are a century apart: combining them needs a stated transfer assumption |
| Temporal resolution | Sailing season: one India round trip per ship per year; outbound around midsummer | Pliny *NH* 6.103 [sourced]; Nappo 2018: 41 n. 136 [sourced] |
| Agents (aggregate roles) | Ventures (ship-voyage), lenders, fisc (tetarte at Alexandria; arabarch collectors), carriers (camel, Nile, ship), external sellers/buyers | Avoids assuming modern firms; legal status of crews/carriers is a later extension |
| Commodities | Pepper, malabathron, Gangetic nard, ivory (+ schidai, tortoise shell); outbound goods and coin as one aggregate | The six verso items; outbound evidence via Cobb 2015b (cited only) |
| Boundary | Indian prices exogenous (M0) / supply schedule (M1); Mediterranean demand exogenous (M0) / schedule (M1); tax receipts exit to a state sink; no feedback to the Egyptian grain economy except through shared transport capacity | Partial equilibrium only |
| Money of account | Alexandrian drachma; HS only via the nominal rule CR-MON-EG-003 | No purchasing-power claims |

---

## 5. Acquisition plan

| Tier | Items | Route | Rights |
|---|---|---|---|
| A — structured datasets | idp.data (EpiDoc: SB XVIII 13167, O.Berenike, O.Petr.); Pleiades exports; Gal et al. 2023 sailing data; Harper/DARMC price geodatabase; ORBIS (licence TBD) | Official bulk downloads / GitHub; pin commit hashes | idp.data and Pleiades CC BY 3.0; Gal et al. CC BY 4.0; others TBD |
| B — permitted full-text extraction | Nappo 2018 (CC BY 4.0); open theses/OA monographs (Cobb thesis at UWTSD; Seland 2010 on Fulcrum; O.Berenike 4 on Propylaeum, if OA) | Download → SHA-256 → GROBID (born-digital) / OCR (scans) → passage anchors | Check each item separately |
| C — manual review (library/licensed) | De Romanis 2020; Brughmans & Wilson 2022; Wilson & Bowman 2018 (Tomber, Nappo, Adams chapters); Rathbone 2000; Harrauer & Sijpesteijn 1985; Casson 1989; Bagnall et al. 2000/2005; Adams 2007; Evers 2017; Cobb 2018; Peacock & Blue 2006/2011; Sidebotham 2011 | Researcher's library access; extract facts + loci only | Private research use; no redistribution |
| D — unavailable now | The "synthesis" referenced by the brief; Wilkinson 2021 thesis (robots-blocked); O.Berenike 4 page (bot protection) | Ask the researcher / manual download | — |

Discovery for scale-up (WP4): Crossref + OpenAlex APIs and citation chaining seeded from Nappo's bibliography, which is CC BY and parseable. Every query is logged in `registers/search_log.csv`.

---

## 6. Minimal evidence schema, ontology outline, architecture

**Implemented** (`schema/evidence.sql`, `src/romeco/evidence_db.py`): `source`, `document`, `assertion`, `parameter`, `dependency`, `conversion_rule`, `rights`. Design points:

- `record_origin` (transcribed reading / literary statement / scholarly reconstruction / project derivation …) and `epistemic_status` (accepted_working / uncertain / disputed / unresolved / rhetorical / rejected) are separate.
- `review_status` records **how** the project accessed a claim. It is not a reliability score.
- A `CHECK` constraint makes it impossible to insert synthetic or simulated records into evidence tables (tested).
- Rival readings and interpretations are separate assertions linked by `depends_on`. Nothing is overwritten.

**Competency queries, implemented and passing:** CQ1 parameters depending on a document; CQ2 parameters resting on unverified access; CQ3 independent primary documents per parameter; CQ4 critical uninspected sources; CQ5 contested inputs. **Planned:** CQ6 "which conversion rules produced this value?"; CQ7 "which claims change if a place identification changes?" (needs Pleiades IDs); CQ8 "rerun excluding all claims derived from one interpretation".

**Ontology outline** (candidate mappings; to be checked against pinned versions before adoption):

| Project class | Scope | Candidate mapping |
|---|---|---|
| Document | Ancient object/text/archive | CIDOC CRM E22 Human-Made Object / E33 Linguistic Object |
| Reading | A transcription of a locus by a named reader | E33 Linguistic Object + prov:wasAttributedTo |
| Assertion | Addressable claim with provenance | CRMinf belief/proposition classes; prov:Entity |
| Interpretation | Assertion about the meaning of a reading | CRMinf inference/argumentation classes |
| ProjectDerivation | Computed value | prov:Entity, prov:wasDerivedFrom, prov:Activity (code version) |
| ConversionRule | Scoped unit relation | SKOS concept + custom properties (scope, status) |
| Place | Port, station, route node | Pleiades URI |
| TimeSpan | Interval with uncertainty | OWL-Time interval |
| Parameter | Model input with status and bounds | project vocabulary |

Adoption rule: map to PROV-O first (cheap, high value), then to CRMinf for argumentation only where queries need it. Do not import whole standards.

**Architecture**

```
registers/*.csv  config/*.yaml  data/curated/*.csv     (git: human-reviewed, diffable)
        │                 │                │
        └────────► romeco.evidence_db ◄────┘           (DuckDB, rebuilt on demand)
                          │  competency queries (lineage, independence, rights)
                          ▼
                 parameter construction (status + bounds)
                          ▼
         M0 feasibility ─► M1 spatial PE ─► M2 ABM (gated)
                          ▼
                 observation model (latent flows → surviving traces)
                          ▼
     experiments/E*/ (manifest: config hash, versions, seed) ─► reports

acquisition (WP4): discovery (Crossref/OpenAlex, citation chaining) → queue (per-domain policy,
backoff, state machine) → permitted fetch → file_copy + SHA-256 → GROBID / OCR → passage anchors
→ LLM-proposed extractions → human review → assertions
```

---

## 7. M0 baseline, matched M1/M2, parameter–evidence map, observation model, validation

### 7.1 M0 (implemented: `src/romeco/m0/`)

Voyage ledger for one venture *v* and commodities *c*, in drachma_EG:

- Physical: `loaded_c = spoiled_c + lost_c + arrived_c`; `arrived_c = to_state_c + to_merchant_c` (in-kind tetarte).
- Assessed value `A = Σ_c a_c·arrived_c`; liability `T = τA`; collected `κT`; evaded `(1−κ)T`; residual `A − κT`.
- Merchant net (ship survives) = proceeds − Indian purchase − ship costs − camel − Nile − levies − fees − exit duty + outbound sales + loan − repayment.
- A maritime loan is repaid only if the ship survives; an ordinary loan is repaid regardless. Risk-neutral break-even maritime premium: `r* = 1/(1−p) − 1`.
- Expected values mix over ship loss with probability *p*. Break-even sale multiple has a closed form (net is affine in the sale price).

Aggregate block (`fiscal.py`): `G = N·λ·A_H`, `R = τ·κ·G`, `M = G/O`, feasibility `M ≥ M_min = (1+c)/((1−τ)(1−p))`.

**Known simplifications:** assessment price is used as a proxy for sale price in `M_min`; Pliny's O is treated as purchase cost (if O is bullion only, the lower bound rises); λ scales value, not mass. No equilibrium is claimed.

### 7.2 Experiment E000 (run 2026-10-24)

Grid over the A_H variants (4), O ∈ {50 m, 100 m}, c ∈ {0.2, 0.5, 1.5}, p ∈ {0.01, 0.05, 0.15}, N ≤ 120, λ ∈ [0.1, 1.5], κ ∈ [0.7, 1.0]. All 72 bound configurations are feasible. Receipts envelope HS 14.1 m–415.6 m. At baseline (c = 0.5, p = 0.05, O = 50 m): M_min = 2.11, ≥ 11.4 Hermapollon-equivalents per year, receipts HS 18.4 m–415.6 m **[calculated]**. Outputs and manifest: `experiments/E000_m0_anchor_consistency/outputs/`.

### 7.3 Matched M1 / M2 design

| Element | M1 spatial partial equilibrium | M2 agent-based exchange |
|---|---|---|
| Geography / commodities / taxes / costs | identical to M0 | identical to M0 |
| Agents | aggregate supply (India) and demand (Mediterranean) per commodity | ventures with capital endowments; lenders; carriers; fisc |
| Prices | market clearing with complementarity: `P^A_c(1−τ)(1−p) ≤ P^I_c + t_c`, `x_c ≥ 0`, equality where `x_c > 0`; capacity `Σ_c x_c ≤ N·K` with shadow price μ | posted prices at Muziris and Alexandria, revised by excess demand; sequential matching; rationing; unsold stock carried with storage cost and spoilage |
| Information | full, contemporaneous | **Alexandrian prices known with one-season lag** (news returns with the ships); departure decided in July on last season's prices |
| Credit | none, or the same exogenous financing cost as in M2's limiting case | maritime loans with rate *r*, collateral = cargo, lender capital limit |
| Closure | Indian supply elastic (η bounds) or perfectly elastic; Mediterranean demand `D_c = B_c P^{−ε}` (ε bounds); receipts exit; numeraire drachma_EG; **not GE** | same external closure |
| Limiting-case test | — | lag → 0 and unconstrained credit ⇒ M2 should approach M1 (tested, not assumed) |
| Ablations | — | lag on/off; credit cap on/off; one mechanism at a time |
| Common targets | receipts bounds; desert-throughput seasonality; O.Berenike pass seasonality (reserved); price dispersion only if a price series is found | same, through the same observation model |

Expected outcome, stated now: with the current evidence M1 and M2 will be **observationally equivalent** on all available targets. The M2 lag predicts boom–bust (cobweb-type) alternation in sailings and Alexandrian prices, which no current dataset can observe. Report it as such.

### 7.4 Parameter–evidence map (from `config/parameters.yaml`; CQ3)

| Parameter | Status | Primary documents | Comment |
|---|---|---|---|
| τ | measured_input | P.Vindob. G 40822; Strabo | Rival "double tetarte" kept as a scenario (0.4375) |
| A_H | measured_input | **1** (P.Vindob. G 40822) | Baseline HS 9,215,803 (principal edition, three-quarters scope read in the text); 1985 reading as sensitivity; whole-base variants rejected (D009) |
| merchant_talent_litrai | measured_input | 1 | Identified from the papyrus's rounding: (97.497, 97.510] |
| pepper_price_dr_per_mina | external_estimate | 1 | 6 vs 24: changes mass ×4, value unchanged |
| tax_mode | measured_input | 1 | In kind (quarter shares listed); 'money' kept open by De Romanis 2014 |
| N | exploratory | Strabo | Augustan, one port, ambiguous |
| O | measured_input | Pliny | Literary, moralising |
| route_nile_km | exploratory (lower bound 646 km) | Pliny withdrawn (K17) | Pliny's 309 mp is shorter than the great circle |
| route_desert_km | measured_input [380, 409] | Pliny; ORBIS; Itiner-e | Sources share lineage; Itiner-e is a least-cost model (K18) |
| camel_capacity_kg | external_estimate 181 [150, 200] | Adams 2007: 79–80 | Fayum loads; desert loads may differ |
| desert_freight_dr_per_camel_trip | external_estimate ≥ 45 | Adams 2007: 231 | lower bound only |
| λ, κ, c, p, camel_capacity_kg | exploratory | **0** | Drive almost all of the receipts range; λ is the key unidentified quantity |

### 7.5 Observation model (latent process → surviving traces)

| Trace | Generating process to model | How it may be compared |
|---|---|---|
| Hermapollon valuation | One draw from the cargo-value distribution, with unknown selection (large loans more likely to be documented?) | As a single observation with a selection parameter. Never as the mean |
| O.Berenike passes | Outbound consignments × issuance rule × ostrakon discard × survival × excavated fraction × publication | Presence and seasonal shares of outbound traffic only; not volumes, and not return cargoes |
| Nikanor archive | One firm's contracts × archive survival | Firm-level behaviour only (Nappo 2018: 47–48) |
| Indian coin finds | Outflow composition × hoarding/deposition × recovery × reporting | Presence/chronology; separate observation model (later, for the "decline vs. bias" hypothesis) |
| Literary figures | Author's information × rhetoric | Bounds only; flagged `rhetorical` where appropriate |

### 7.6 Validation plan

Done: unit and conversion tests; accounting identities (physical balance, counterparties, liability = collected + evaded, cash ≡ in-kind when sale = assessment, zero-tax limit, loan risk allocation); exact reproduction of published arithmetic (42 tests passing).

Next:
1. Desert-throughput consistency test (WP2), using sourced capacity inputs as **held-out** evidence.
2. Global sensitivity (Morris screening, then Sobol) over exploratory parameters.
3. M1 parameter-recovery on clearly labelled synthetic data (software validation, not historical validation).
4. M2 → M1 convergence test.
5. Report the iso-receipt ridge (observational equivalence) explicitly rather than choosing a point.

---

## 8. Phased work plan

| WP | Content | Acceptance test |
|---|---|---|
| WP0 ✅ | Repo, registers, schema, M0, E000 | `pytest` green; CQ1–CQ5 run; E000 manifest written |
| **WP1 (substantially done)** | **Hermapollon documentary audit.** Pull idp.data; extract the SB XVIII 13167 EpiDoc; verify the total reading(s) and the six item quantities; read De Romanis 2020 on the verso; resolve INT-HERM-03 against Nappo | Every assertion feeding `A_H` has review_status ∈ {inspected, human_reviewed}; CQ2 empty for `A_H`; item residuals explained or documented with page references. **Status:** readings inspected; nard/ivory/schidai exact; INT-HERM-03 rejected; open: INT-HERM-02 and pepper/tax-mode interpretations (machine summary only) need direct reading of De Romanis 2014/2020 or your review |
| WP2 | Desert-throughput test (Adams 2007; O.Berenike; Coptos tariff; Nikanor) | `camel_capacity_kg` and a return-window capacity become `external_estimate` with loci; H1a either rejected or retained under stated bounds |
| WP3 | Novelty audit (Brughmans & Wilson 2022; De Romanis 2020; Wilkinson 2021; Cobb 2018; Evers 2017; Copeland 2022) | Comparison table; contribution statement C1 revised or replaced |
| WP4 ◐ | Corpus pilot: discovery + permitted acquisition + parser benchmark on 20 stratified documents | Extraction error rates by stratum; every claim anchored to page/locus — **met provisionally 2026-10-24** (E004; gold pending researcher review; see docs/corpus_pipeline.md) |
| WP5 | M1 specification + implementation | Comparative statics reproduce M0 bounds as a special case |
| WP6 | M2 (gated by WP5 + an identified target) | Limiting-case convergence test; ablation table |
| WP7 | Synthetic-data framework | Origin labels survive joins/exports (tests); recovery experiments documented as software validation |
| WP8 | Paper-style account | Third party can trace every number to code, parameters, assertions and sources |
| WP9 ✅ | Semantic foundation (appended; the brief's 'Semantic foundation' milestone): minimal ontology, assertion graph, SHACL shapes, competency queries | Provenance and competing interpretations survive ingestion and querying: lossless round trip, rivals survive, SHACL positive + 5 negative cases, CQ6–CQ11 golden answers (`tests/test_semantic.py`) — **met 2026-10-24** |

**Decision with the largest effect on validity:** treating λ (how typical the Hermapollon was) as unidentified and testing it through desert throughput, rather than assuming λ ≈ 1. **Decisions that can safely wait:** graph database, ABM framework, full CIDOC CRM mapping, cloud infrastructure.

---

## Assumptions, limitations, next step

- **Assumptions:** nominal dr = HS; De Romanis's metrology (95-lb official talent; 322.8 g pound); all exploratory bounds listed in `config/parameters.yaml`.
- **Limitations:** De Romanis 2012 was read through a machine summary, not directly. Ancient texts were accessed only through Nappo's quotations. Novelty against the 2018–2022 literature is unverified. E000 is a bounds calculation, not an estimate.
- **Single most useful next step:** WP1. Verify the Hermapollon inputs against the EpiDoc text and De Romanis 2020, because every fiscal number in the project currently rests on that one document.

---

## 9. WP1 results (session 2, 2026-10-24)

**Source.** SB XVIII 13167 = P.Vindob. G 40822 = TM 27666, DDbDP EpiDoc (idp.data commit `f03d0f3…`, SHA-256 in `data/raw/idp_data/ATTRIBUTION.md`). The encoded text is the principal edition in *Tyche* 26 (2011), a full re-edition of the verso. HGV dates the papyrus to the mid-2nd century (126–175 CE, low precision), provenance unknown **[sourced]**. All numerals are extracted by code into `data/curated/pvindob_g40822_numerals.csv`.

**What the text itself establishes [sourced: DDbDP lines cited]:**

1. Total = 1,151 T 5,852 dr (v ii 29), stated as the value of **three parts** of the cargo (v ii 27). The whole-cargo-base interpretation is rejected (D009).
2. Column i lists whole quantities and the quarter removed: nard 20 boxes (of 80); ivory 105 T 13 min, quarter 26 T 18¼, removed 26 T 30; schidai 17 T 33, quarter 4 T 23¼, removed 4 T 46. The tetarte was taken **in kind**, plus a small surplus.
3. The 'arabarch rates' of 0.25 % and 2.88 % are ratios of these surpluses (11¾ and 22¾ minae) to listed weights, not statutory rates (K14).
4. The recto lists borrower-borne costs until the tetarte: camel driver, desert freight (*phoretron*), Nile freight. It gives the creditor the right to collect the tetarte and dispose of the three parts on default. **No interest rate survives** in the transcribed text, so RQ3 has no in-region rate evidence.

**What the project derived [calculated; `romeco.m0.pvindob_arithmetic`, tests in `tests/test_pvindob_arithmetic.py`]:**

- The valuation procedure, reproduced exactly for ivory and schidai: remove the surplus, convert at 95 litrai per talent, truncate to whole litrai (7,478; 1,214), re-express in the merchants' talent, truncate to whole minae (76 T 41; 12 T 27), price (100 and 70 dr/mina), add the surplus. Every intermediate figure in v ii 4–26 matches.
- The merchants' talent (lost in the lacuna at v ii 9) is pinned by the two truncations to **(97.497, 97.510] litrai**, which includes the 97.5 used by De Romanis.
- Pepper: the value 771 T 4,632 dr (v i 25–26) is preserved. At Morelli's 24 dr/mina it gives exactly 3,215 T 43 min, the numeral at v i 21; at De Romanis's 6 dr/mina (with a myriad lost in the lacuna) it gives four times as much. E001: whole pepper c. **135 t vs c. 540 t**; whole weighed cargo c. 213–219 t vs c. 608–624 t **[calculated; D021 correction; malabathron reconstruction kept across readings]**.

**Consequences.** Fiscal bounds (E000) are unaffected, because they depend on value, which both readings share. The desert-throughput test (WP2) must be run under both readings (D011). Two DDbDP encoding issues were found and are overridden in code (K12). Reporting them upstream requires your papyri.info account and is your call.

**Still open for WP1 closure:** direct reading of De Romanis 2014 (open access, but blocked to this environment) and 2020, plus the Tyche 2011 article, to move INT-HERM-02/04/05 and INT-TET-03 out of `machine_summary_only`.

---

## 10. Context layer (session 3)

Legions, cities, roads and prices/inflation are now tracked as conditioning variables (D012). They act as constraints, confounders, node scales and deflators; they are not a new research question. See [`docs/context_layer.md`](context_layer.md). The results that bear on RQ1:

- W1 (from the 70s) and the Hermapollon fall in the same stable Egyptian price band. Nominal comparisons between them need no deflator.
- Garrison and quarry supply traffic is the main confounder for the WP2 desert-throughput test. The praesidia network is mapped (58 installations active in 100–200 CE per Pleiades).
- ORBIS v2 road "time" is a constant-speed transform of length and is not evidence of travel time (D013).


---

## 11. WP2 result: desert throughput (E003, 2026-10-24)

**Status.** Executed as descriptive partial identification. The pre-registered rejection criterion is **not evaluable** (D020): no inspected source gives the Eastern Desert's camel stock, hydreuma water capacity or a traffic count. Manifest: `experiments/E003_desert_throughput/manifest.yaml`, written before running.

**Model [calculated].** For N·λ Hermapollon-equivalents, with M the whole weighed cargo:

- loads per season: S = N·λ·M / load
- camels in continuous service: C = S·RT / W
- RT = 2 × one-way days + turnaround
- W = the window over which a season's inbound cargo must cross the desert

The grid has 288 cells: 2 readings × 2 weight talents × 3 loads (150/181/200 kg) × 2 terminals × 2 transit times × 2 turnarounds × 3 windows (36 d from Pliny's departure spread; 120 d assumed; 365 d with full port storage).

| Reading | Whole cargo (t) | Loads/ship | H1a loads/season (N·λ = 120) | Camels (W = 36 / 120 / 365 d) | × Ruffing's 2,000 loads/month |
|---|---|---|---|---|---|
| De Romanis (6 dr/mina) | 608–624 | 3,040–4,160 | 365k–499k | 101k–444k / 30k–133k / 10k–44k | 152–208 / 46–62 / 15–21 |
| Morelli (24 dr/mina) | 213–219 | 1,070–1,460 | 128k–175k | 36k–156k / 11k–47k / 3.5k–15k | 53–73 / 16–22 / 5.3–7.2 |

**Readings of the result.**

1. **The two hypotheses imply desert traffic one to two orders of magnitude apart.** Traffic at the highest sourced scale of Berenike's supply (2,000 loads/month) moves only 0.6–23 Hermapollon-equivalents per season. So any sourced count of desert traffic or camels would discriminate H1a from H1b. This is the most valuable missing evidence.
2. **Under H1a the desert is cheap but large.** Freight at Adams's lower bound is 0.5–2% of cargo value. The constraint is physical scale (camels, drivers, water, fodder), not cost.
3. **The return window dominates uncertainty (×10).** Whether goods were stored at the ports and moved year-round matters more than the pepper reading (×2.85) or the camel load (×1.33).
4. **Myos Hormos halves the camel requirement relative to Berenike**, but not the monthly traffic. Strabo's 120 ships are reported for Myos Hormos.

**Limitations.**
- Mass is assumed to scale with value (A1). Smaller ventures carrying bulkier goods would need more loads.
- Outbound traffic is assumed to ride on the return legs (A2).
- Masses exclude nard and unweighed goods.
- The Morelli case keeps De Romanis's malabathron reconstruction.
- The comparators are scholarly estimates whose derivations are not inspected, and they disagree by 4–10× (K21).

**Evidence that would make the criterion evaluable (priority order).**
1. Counts of camels or loads passing Coptos or the desert praesidia per month, e.g. the Coptos tariff (OGIS 674 = I. Portes 67) with any associated receipts, or O. Krokodilô / Myos Hormos road ostraca.
2. Hydreuma water capacities from the excavation reports (Sidebotham; Cuvigny, *La route de Myos Hormos*).
3. Camel registration totals for Upper Egypt.

**Follow-up (D022): no open documentary traffic count exists for 100–200 CE.**
- HGV lists 2,630 Eastern Desert documents (`data/derived/context/eastern_desert_documents_summary.csv`). Berenike's 523 and Myos Hormos's 73 are almost entirely 1st-century, and only 73 of the 1,421 W2 documents are month-dated.
- Documents bound attested activity from below only, so they cannot reject H1a.
- Ast (2018) documents assessment and storage of imports at the ports, which makes E003's storage window (W ≫ 36 d) the more plausible case.
- The remaining discriminating evidence is physical capacity (well yields: Cuvigny et al. 2011, *Didymoi*), currently not accessible.

## 12. WP4 result: corpus pilot (2026-10-24)

The pipeline (`romeco.corpus`, `docs/corpus_pipeline.md`) acquires, parses, anchors, extracts and discovers over 13 items in 5 parse routes.

**Held-out benchmark, v0.2 frozen (E004):**

| Measure | Value | 95% CI | n gold |
|---|---|---|---|
| Quantity precision | 0.78 | 0.45–0.94 | |
| Quantity recall | 0.54 | 0.29–0.77 | 13 |
| Citation precision | 0.85 | 0.58–0.96 | |
| Citation recall | 0.48 | 0.29–0.67 | 23 |
| Page labels | 15/15 correct | | image-checked |

**Consequences (D024):**
- Extractions are review candidates only.
- Pliny's numerals must come from the printed edition (K22).
- Discovery already gives a usable literature map: 58 works shared across the four documents.

**Acceptance** is provisional until the researcher reviews the 149-row gold sheet. **Next:** the semantic foundation (minimal ontology and assertion graph), which can now ingest anchored candidates without promoting them to evidence. Done: see §13.


## 13. WP9 result: semantic foundation (2026-10-24)

`ontology/romeco.ttl` (v0.1.0), `ontology/shapes.ttl`, `ontology/queries/CQ6–CQ11`, builder `romeco.semantic.build`, CLI `romeco graph`. See `docs/semantic_foundation.md`.

| Product | Content |
|---|---|
| Core graph (`core.ttl`, committed) | 3,046 triples: 98 claims (5 readings, 8 interpretations, 76 anchors, 9 project derivations), 45 place identifications, 8 questions, 33 parameters, 10 conversion rules, 9 derivations, 3 experiments |
| Full graph (`full.ttl`, regenerated) | + 6,007 extraction candidates, 220 unreviewed `possiblyBearsOn` links |
| SHACL | Conforms; 4 warnings, all correct: `pepper_price_dr_per_mina` (2), `egypt_legions_W2`, `tax_mode` rest partly on machine-summary claims |

**What the graph answers that the tables did not** [calculated]:
- CQ8: dropping INT-HERM-01 removes the support of `A_H` and hence E000 and E003. Every fiscal and throughput result is conditional on one interpretation of one papyrus.
- CQ11: P.Vindob. G 40822 is cited in all three parsed modern works. Strabo and Pliny likewise. Three modern works citing it are one observation, not three.
- CQ10: Pliny's 257 mp for Coptos–Berenike is found as a candidate in Adams 2007 (p. 39) and Mayhoff 6.103. These are a review lead, not independent support: Adams reports Pliny.

**Limitations.** Q-HERM-SCOPE's INT-HERM-01 and -02 are compatible readings (both "three-quarters"), so the question records a scholarly framing difference, not a contradiction. Place identifications are generated from the crosswalk with uniform `uncertain` status; per-identification review is not yet done. The `possiblyBearsOn` matcher is value-and-unit only and will miss rounded or converted figures. Time is kept as integer bounds (OWL-Time deferred, D026).
