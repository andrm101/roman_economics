# Cross-domain question bank

**Status:** brainstorm. These are candidates, not registered hypotheses. A question enters `registers/hypothesis_register.md` only when its evidence and its rejection or discrimination criterion are registered before any fitting. IDs `RQ-X*` are stable; on promotion a question gets the next `RQn`.

Each entry gives the mechanism, the rival, distinct signatures, the evidence, the main confounders and a feasibility rating.

## Ranking

| Rank | ID | One-line question | Feasibility | Why this rank |
|---|---|---|---|---|
| 1 | RQ-X1 | What explains the 160–187 Egyptian price-level break: mortality, money or document composition? | **High** | Data partly in hand (E002); the rivals predict *different relative-price patterns*, so they can in principle be discriminated |
| 2 | RQ-X3 | Do Greenland lead, coin fineness and documented campaigns move together, and in which order? | Medium | Annual ice-core series exist; the fineness data and an event register must be built |
| 3 | RQ-X8 | Did the 536+ cooling and the 541+ plague leave a signal in 6th-c. Egyptian documents beyond what the change in archive survival explains? | Medium | Rich 6th-c. archives; an observation model is decisive |
| 4 | RQ-X4 | Is hoard non-recovery a usable proxy for insecurity once deposition and finding are modelled? | Medium | Large dataset; mainly a methodological contribution |
| 5 | RQ-X6 | How much of the "adoption curve" of water mills is excavation visibility? | Medium | Methodological, needs an installation register |
| 6 | RQ-X2 | Can Nile-flood shocks be traced in Roman-era fiscal documents? | Low–medium | Sparse flood series; transfer from Ptolemaic work needs a stated assumption |
| 7 | RQ-X5 | Do conditions in Parthia, Aksum and India explain Red Sea trade timing beyond RQ1's transport-and-tax factors? | Low | Outsider evidence too thin for 50–200 CE |
| 8 | RQ-X7 | Can any combination of climate, plague, war and debasement be *discriminated* as the cause of the 3rd-century crisis? | Low | Observational equivalence likely; keep only as a demonstration of non-identifiability |

---

## RQ-X1 — The 160–187 price break (recommended first cross-domain question)

**Pattern.** E002 [calculated] confirms an approximate doubling of the Harper (2016) Egyptian price level. The break is located within 160–187 (tied), in data used privately (D016).

| Mechanism | Predicted signature |
|---|---|
| **M-labour** (Antonine plague mortality) | Real wages rise against wheat. Rents and land prices fall relative to wages. Labour-intensive goods rise more than land-intensive ones. Lease terms shift towards tenants |
| **M-money** (monetary or fiscal change: tetradrachm fineness, war spending) | A broadly uniform nominal rise across all prices and wages, with **relative prices roughly stable**. Timing follows the fineness change, if any |
| **M-record** (change in which documents survive or are published: archives, nomes, genres) | The break disappears or shifts when the analysis is restricted to a stable composition of archives, nomes and document types |

These three are not exclusive. The test asks which components are *needed*, and whether relative prices can separate them.

**Evidence needed.**
- Harper 2016 rows (have) with commodity, nome, archive and genre.
- A wage subset.
- A rent and lease subset (HGV/DDbDP, have via idp.data).
- Alexandrian tetradrachm fineness by regnal year (candidate: published metallurgical analyses; not in hand).

**Identification.** The test runs on relative prices within documents and within archives, which differences out the money level. The composition-stable subsample tests M-record. The dating Monte Carlo (§4 of `02_ontology_and_data.md`) handles regnal-year intervals.

**Confounders.**
- The Antonine wars (fiscal), which overlap in time.
- Small-N wage data.
- Commodity quality changes.

**Rejection criteria (draft).**
- M-money alone is rejected if relative wage/wheat prices shift beyond the dating-resampled null.
- M-labour alone is rejected if relative prices are stable within the composition-stable subsample.

**Honest prior.** The wage and rent subsets may be too small to discriminate. In that case the contribution is a demonstration that the existing debate (Scheidel vs. Bruun et al.) is not identified by these data, plus the specific additional documents that would identify it.

## RQ-X3 — Lead, silver and war

**Mechanisms.**
- Mining output drives both lead emissions and silver coinage, so lead is a supply-side proxy.
- *Or* war and fiscal stress drive debasement, independently of mining.

**Signatures.**
- Supply story: lead declines **before** fineness declines.
- Fiscal story: debasement steps follow campaigns while lead is flat.

**Evidence.**
- The McConnell et al. 2018 annual lead series (candidate).
- Silver fineness by reign (candidate: Butcher & Ponting 2014).
- A campaign register (DOM-WAR, to build).

**Confounders.**
- Changes in smelting technology alter the emission factor.
- Iberian vs. other ore sources.
- Ice-core chronology versions.

## RQ-X8 — 536 and 541 in Egypt

**Mechanisms.**
- Climatic or epidemic shock → land abandonment, fiscal arrears, lease changes.
- *Or* the patterns reflect which 6th-c. archives survive (e.g. a few large estates and villages).

**Evidence.**
- Dated 6th-c. papyri via HGV (have).
- An eruption list (candidate: Sigl et al. 2015).
- Literary plague accounts.

**Key requirement.** An archive-level observation model. Without it, a signal is uninterpretable.

## RQ-X4 — Hoards as an insecurity proxy

**Mechanisms.**
- Non-recovered hoards mark violence.
- *Or* they reflect saving habits, coin-reform incentives (hoarding old good coin) and modern detection.

**Signatures.**
- Spatial and temporal clustering near documented events, net of reform dates and modern detection intensity.

**Evidence.**
- CHRE (candidate).
- A reform-date register.
- The conflict register.

**Main contribution.** A deposition–recovery–finding observation model applied to an existing dataset.

## RQ-X6 — Visibility of technological adoption

**Mechanisms.**
- Adoption accelerates in a given period.
- *Or* publication and excavation intensity create the curve.

**Evidence.**
- An installation register built from inspected syntheses.
- An excavation-intensity proxy (e.g. number of published excavations per region and decade). Must be built.

## RQ-X2, RQ-X5, RQ-X7

These are recorded for completeness and are not started.

- **RQ-X2** needs a Roman-era flood observation set.
- **RQ-X5** needs outsider evidence dated to our window.
- **RQ-X7** is a deliberate test of the claim that the project can say "not identified".
