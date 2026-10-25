# Ontology extension and data architecture

**Status:** proposal. It extends `ontology/romeco.ttl` 0.1.0 and the DuckDB store, keeping D026–D029 unchanged. The target is ontology 0.2.0, implemented per domain as each passes the gate in `00_charter.md` §5.

## 1. Design choices with the largest effect on validity

1. **Time.** One interval-and-method model for everything (§4). Most cross-domain errors in this field are dating errors.
2. **Identity as claims.** Event, group, place and installation identities across sources are reviewable claims. This generalises CQ7.
3. **Series vs. events.** Climate and price series are stored as measurements, with a reconstruction method attached. They are not a list of "facts per year".

Choices that can wait: a graph database, full CIDOC CRM event modelling, GIS polygons for provinces.

## 2. New classes (ontology 0.2.0 draft)

All new claim types are subclasses of `rx:Claim`, so they inherit the three labels, attribution and the SHACL rules.

| Class | Super | Scope note | Identity rule |
|---|---|---|---|
| `rx:Event` | prov:Entity | Something said to have happened in an interval, at a place or places | `EVT-<domain>-<slug>`; one node per project-recognised event |
| `rx:EventClaim` | rx:Claim | A source's statement that an event occurred, with its own date, place and participants | one per source passage |
| `rx:IdentityClaim` | rx:Claim | "These records refer to the same X" (event, group, person, installation). Generalises `rx:PlaceIdentification` | reviewable; has rivals in an `rx:Question` |
| `rx:ConflictEvent`, `rx:EpidemicEvent`, `rx:ClimateEvent` (e.g. eruption), `rx:FamineEvent` | rx:Event | typed events | as Event |
| `rx:Participant` | — | n-ary role node: (event, group/polity/person, role, attributed size claim) | per event × participant |
| `rx:Group` | — | An ethnonym **as used by a source** | `GRP-<label>-<source>`; a cross-source group is an `rx:IdentityClaim` |
| `rx:Polity` | — | A state or political unit with a dated existence | `POL-*` |
| `rx:Person` | — | A named individual (commander, emperor, merchant) | link to Trismegistos People where possible |
| `rx:ProxyRecord` | prov:Entity | A raw physical measurement series from one archive (tree site, ice core, cave) | archive ID + dataset version |
| `rx:Reconstruction` | rx:ProjectDerivation *or* rx:Anchor | A modelled series (e.g. summer temperature anomaly), with method, calibration window, footprint and uncertainty | publisher dataset ID + version; *ours* if we compute it |
| `rx:Measurement` | rx:Claim | One value of a series at one interval (stored in Parquet, not as triples; see §5) | series ID + interval |
| `rx:Technology` | skos:Concept | A technique or device type (thesaurus, broader/narrower) | `TEC-*` |
| `rx:Installation` | — | A located instance with phases (a mill, a mine, a kiln, a harbour work) | `INS-*`; phases carry their own intervals |
| `rx:Account` | rx:Claim | A source's characterisation of another group or polity (perspective) | per passage |
| `rx:CoverageCell` | — | (domain, region, period, evidence class) → count, best resolution, review level | generated; never edited by hand |
| `rx:TransferAssumption` | rx:Claim (project_derivation) | "Series S, measured for region R1 / period P1, is used for R2 / P2", with a sensitivity test | must be linked from every cross-region use |

New controlled vocabularies (SKOS): `EventType`, `ParticipantRole`, `DatingMethod`, `ArchiveType` (tree ring, ice core, speleothem, pollen, documentary), `Season`, `EvidenceClass` (narrative, documentary, epigraphic, numismatic, archaeological, scientific, outsider-account).

## 3. Space

- **Places:** Pleiades URIs where available. Places outside the Pleiades coverage get `PLC-*` with coordinates, a stated precision and a source.
- **Uncertain or multiple locations:** an event may have several candidate places, each a `rx:PlaceIdentification` with rivals. Battles with disputed sites are the standard case.
- **Regions:** analysis regions (`REG-*`) are project definitions. Each is a set of Pleiades places or a polygon with a version. Provinces are time-varying (`REG-PROV-<name>-<interval>`).
- **Footprints:** every climate reconstruction has a footprint (point, region or field). A join between a footprint and a region outside it creates a `TransferAssumption`.

## 4. Time model (applies to every record)

Every dated record carries:

| Field | Meaning |
|---|---|
| `t_low`, `t_high` | integer years CE (BCE negative, **no year 0**: the library converts) bounding the interval |
| `t_resolution` | `day`, `month`, `season`, `year`, `regnal_year`, `decade`, `generation`, `century`, `phase` |
| `dating_method` | from `DatingMethod`: explicit date in text, regnal formula, consular date, Egyptian civil calendar, palaeography, stratigraphy, ceramic typology, numismatic terminus post quem, radiocarbon (with calibration curve and version), dendro, ice-core layer count (with chronology version) |
| `calendar_source` | e.g. Egyptian civil year vs. Julian, for documentary dates. Conversion is a named rule, like units |
| `dating_dependency` | ID of the claim the date depends on (e.g. a destruction layer dated *because* attributed to a known war). Prevents circular dating |

**Interval semantics (D033):** `[t_low, t_high]` bounds the *uncertainty* about one event's date, not a duration. Arithmetic uses astronomical years (1 BCE = 0, 2 BCE = −1). Bounds are inclusive, so an interval's length is `|A| = t_high − t_low + 1` years: (1 BCE, 1 CE) spans 2 years.

**Join rules for cross-domain analysis (D033):**
- **Overlap join:** returns pairs with `|A∩B| > 0`, reporting `overlap_frac = |A∩B| / |A|` (asymmetric; under uniform uncertainty, the probability that A's date falls in B, i.e. the aoristic weight) and the symmetric `jaccard = |A∩B| / |A∪B|`.
- **Containment join:** `B.t_low ≤ A.t_low` and `A.t_high ≤ B.t_high`. Inclusive, so equal intervals count as contained (Allen 1983: *equals*, *during*, *starts*, *finishes*).
- **Lag join:** `0 ≤ B.t_low − A.t_high ≤ k`, inclusive at both ends. A pair where B starts before A ends belongs to the overlap join, not the lag join.

Analyses must state which join they use. A correlation between two series must be **robust to resampling dates within their intervals**: a Monte Carlo over dating uncertainty that draws each date uniformly (integer years) within its interval, seeded (default 42) and reported. Circularly dated records are excluded from that test automatically. A record is circular if following `dating_dependency` links from it reaches the other side of the join, or returns to itself, over a chain of any length (A→B→A, A→C→B→A).

## 5. Storage

| Layer | Store | Why |
|---|---|---|
| Raw sources and datasets | content-addressed files + `registers/corpus/items.csv`; large datasets in `data/raw/<domain>/` (git-ignored if not redistributable) | rights and immutability (D016) |
| Canonical evidence | DuckDB built from curated CSVs (D027), extended per domain: `event`, `event_claim`, `participant`, `group_label`, `identity_claim`, `installation`, `installation_phase` | one source of truth, SQL tests |
| Series | Parquet, partitioned by `domain/series_id/version`; columns `t_low, t_high, value, value_low, value_high, unit, n, quality_flag`; series metadata as a claim row in DuckDB | millions of values do not belong in RDF |
| Graph | RDF view (core + domain graphs), SHACL, SPARQL. Series appear as one node per series, not per value | provenance queries without bloat |
| Coverage maps | generated Parquet + HTML artifact per domain | principle 9 |
| Simulations | `runs/<experiment_id>/<run_id>/` with a manifest, seed, code version and parameter snapshot; every row carries `record_origin = simulated` | origin label survives (WP7) |

**ID scheme:** `DOM-`, `EVT-`, `GRP-`, `POL-`, `PER-`, `INS-`, `TEC-`, `SER-` (series), `REG-`, `PLC-`, plus the existing `SRC-`, `DOC-`, `RD-`, `INT-`, `ANC-`, `CTX-`, `Q-`, `K`, `D`, `E`. IDs are stable and never reused.

## 6. Competency questions for the expansion (registered before building)

Expected answers can only be written once data is ingested. Until then each CQ states its **acceptance shape**.

| ID | Question | Acceptance shape |
|---|---|---|
| CQ12 | Which events are attested by only one source passage, and of what evidence class? | list with class; drives review priority |
| CQ13 | For an event, which dates are proposed, by whom, by which dating method, and is any dating circular? | all rival dates survive; circular dependencies flagged |
| CQ14 | Which analyses use a climate series outside its footprint, and is there a registered sensitivity test? | every such use has a TransferAssumption with a test |
| CQ15 | For a named group, which labels in which authors are identified with it, and on what grounds? | identity claims with rivals; no unattributed identification |
| CQ16 | What is the coverage (count, best resolution) of each evidence class by region × quarter-century? | coverage map regenerates deterministically |
| CQ17 | Which model inputs depend on outsider accounts vs. Roman accounts of the same event? | split counts; used to test perspective sensitivity |
| CQ18 | Which installations of technology T are dated only typologically, and how does the adoption curve change if they are excluded? | two curves, both reported |
| CQ19 | Which conclusions survive excluding all evidence from one author (e.g. Historia Augusta, Procopius)? | an exclude-one-author rerun, generalising CQ8 |
