# Domain map

**Status:** proposal. Every dataset or work named below is a **candidate** in `registers/expansion_source_candidates.csv` (`access_status = unverified_candidate`). I named it from prior knowledge and have **not** inspected it, and nothing here may be cited as read. Before use, register it in `source_register.csv` with an honest status.

Domain IDs (`DOM-*`) are stable. New domains are appended, never renumbered.

---

## DOM-ECO — Economy (existing pilot)

| Aspect | Content |
|---|---|
| Scope now | Egypt–Red Sea–India trade, 50–200 CE (RQ1–RQ3); context layer for legions, cities, roads and prices (D012) |
| Entities | voyage, cargo, tax obligation, merchant, loan, port, route, commodity, price observation |
| Expansion | production (grain, olive oil, wine, metals), regional price series, wages, fiscal flows (annona, stipendium), mining output |
| Links | consumes conflict (disruption, military demand), epidemics (labour supply), climate (harvests, Nile), technology (transport cost, productivity) |

## DOM-WAR — War and conflict

| Aspect | Content |
|---|---|
| Phenomena | external wars, campaigns, battles, sieges, raids, revolts, civil wars, usurpations, banditry and piracy |
| Entities | `ConflictEvent` (typed), `Campaign`, `Force` (attributed size claims), `Commander`, `Polity`/`Group` participants, `Fortification`, `Destruction` (archaeological) |
| Evidence classes | narrative histories (e.g. Tacitus, Cassius Dio, Ammianus, Procopius); epigraphy (military diplomas, building and dedication inscriptions); coins (victory types, hoards); archaeology (destruction layers, battlefield sites, fort phasing); outsiders' accounts (e.g. Shapur I's trilingual inscription at Naqsh-e Rostam) |
| Key debates | army sizes in narratives (inflated; topoi); "grand strategy" vs. reactive frontier policy; whether hoard non-recovery measures insecurity; reliability of the Historia Augusta for the 3rd century |
| Observation problems | narrative attention follows emperors and elite authors; source density collapses in some periods, especially mid-3rd century; destruction layers are dated coarsely and attributed to known wars by circular reasoning ("the layer is 260s, so it's the Alamanni") |
| Unit of record | one event per attributed claim; event identity across sources is a reviewable `IdentityClaim` |
| Links to economy | military pay and supply (fiscal demand, coin circulation); route disruption; captives into slave supply; destruction of capital; tax remissions |
| Candidate data | Coin Hoards of the Roman Empire (CHRE, Oxford); Seshat Global History Databank (warfare and polity variables; check licence); Perseus TEI texts (already used); EDH/EDCS epigraphy |
| No canonical source | There is no scholarly Roman conflict-event dataset that I know of. We build an event register from primary texts and inspected modern syntheses. Every event row cites its sources, and no row is derived from Wikipedia without the D015 label |

## DOM-EPI — Epidemics and health

| Aspect | Content |
|---|---|
| Phenomena | Antonine plague (from c. 165), Plague of Cyprian (c. 249–262), Justinianic plague (from 541) and later waves; endemic disease (malaria); famines, as linked events |
| Entities | `EpidemicEvent` (attributed), `MortalityClaim` (attributed rate or count, with denominator), `PathogenIdentification` (claim with method), `SkeletalAssemblage` |
| Evidence classes | literary (Galen, Cassius Dio, Cyprian, Procopius, John of Ephesus); papyri (village registers, tax lists, leases, prices); epigraphy (e.g. abrupt changes in dated inscriptions); aDNA (Yersinia pestis has been identified for the 6th-c. pandemic in published work); mass burials; osteology |
| Key debates | maximalist mortality (e.g. Harper 2017; Scheidel on post-Antonine Egyptian wages) vs. minimalist or "rejecting catastrophe" readings (e.g. Bruun; Mordechai & Eisenberg 2019 for the 6th c.); the critique of Harper by Haldon et al. 2018; whether the Antonine pathogen was smallpox (unconfirmed) |
| Observation problems | mortality is never observed directly. A *mention* of plague is not mortality, and a drop in document production may reflect administration, not death. aDNA confirms presence at a site, not prevalence |
| Direct link to our work | **E002** placed the Harper-2016 price-level break at 160–187 (tied). That interval overlaps the Antonine plague and the onset of the Antonine wars. This makes it a natural first cross-domain test (RQ-X1 in `03_question_bank.md`) and a natural trap for post-hoc attribution |
| Links to economy | labour supply → wages and rents; tax-base contraction; land abandonment; prices |
| Candidate data | published aDNA studies (Wagner et al. 2014; Keller et al. 2019); Egyptian papyrological series via papyri.info/HGV (already integrated); Harper 2016 price DB (have; private use, D016) |

## DOM-CLI — Climate and environment

| Aspect | Content |
|---|---|
| Variables | summer temperature anomaly; hydroclimate (drought index, precipitation); volcanic forcing; solar forcing; **Nile flood height and quality**; vegetation and land use (pollen); atmospheric pollution as an economic proxy (lead, copper) |
| Entities | `ProxyRecord` (site, archive type, raw measurement), `Reconstruction` (a modelled series with method, calibration window and uncertainty), `ForcingEvent` (eruption), `FloodObservation` (documentary) |
| Evidence classes | tree rings (Central European and Alpine reconstructions, e.g. Büntgen et al. 2011, 2016); multi-proxy syntheses (PAGES 2k); drought atlas (Old World Drought Atlas, Cook et al. 2015); ice cores (volcanic sulphate: Sigl et al. 2015; lead: McConnell et al. 2018); speleothems and lake sediments; documentary Nile evidence (papyri on flood levels and remissions; Manning et al. 2017 on eruptions and Nile suppression in the *Ptolemaic* period) |
| Key debates | "Roman Climate Optimum": the label and its spatial uniformity (McCormick et al. 2012; Harper 2017 vs. critics); the 536 CE eruptions and the "Late Antique Little Ice Age" (Büntgen 2016) and their societal impact; whether lead pollution tracks mining output, smelting technology, or both |
| Observation problems | A reconstruction is a model. It has a regional footprint, a seasonal target (often summer), a calibration window and widening uncertainty back in time. Using a Central European tree-ring summer temperature series for Egypt is a **transfer assumption** that needs a sensitivity test. The Nilometer flood series commonly cited is medieval (Roda, from the 7th c. CE); Roman-period Nile data are sparse and documentary |
| Resolution | annual to decadal for tree rings; ice-core dating error of a few years in the 1st millennium (version-dependent); documentary evidence is event-level |
| Links | harvest → grain supply → prices and fiscal receipts (Egypt: flood → tax remission → Alexandrian grain exports); lead → mining → coinage supply; drought → migration and conflict (hypothesis, rival-heavy) |
| Candidate data | NOAA/NCEI paleoclimate archive (hosts many tree-ring and ice-core series; check per-series licence); PAGES 2k; OWDA; Sigl et al. eruption list; McConnell et al. lead series (supplementary data) |

## DOM-EXT — External peoples and their accounts

| Aspect | Content |
|---|---|
| Scope | Barbaricum (Germanic, Sarmatian, Gothic, Hunnic groups), Parthian and Sasanian Iran, Arabia (Nabataean, Himyarite), Aksum, Meroë/Nubia, South Asia (Tamil kingdoms, Kushans), Han and later China |
| Three evidence classes, never merged | (1) **Roman/Greek accounts of others**: ethnography with strong topoi, e.g. Tacitus' *Germania*, Ammianus. (2) **Others' accounts**, including of Rome: e.g. Shapur I's inscription; Aksumite royal inscriptions; Tamil Sangam poems mentioning *Yavana*; the *Hou Hanshu* on *Daqin* and the embassy dated 166 CE; the *Weilüe*. (3) **Archaeology outside the empire**: Roman imports in Barbaricum; Roman coins in South India; Arikamedu; Berenike's Indian finds |
| Entities | `Group` (an attributed ethnonym **label**, not a natural kind), `GroupIdentification` (claim: label X in author Y = group Z, or = archaeological culture C), `Polity`, `Account` (a source's perspective on another group), `ExternalFind` |
| Key debates | ethnogenesis vs. migration models for late-antique groups; identifying archaeological cultures with named peoples (e.g. Wielbark ↔ Goths); whether Chinese *Daqin* means Rome, the Roman East, or something vaguer; Indian evidence for trade volume |
| Observation problems | our access is mostly through modern translations (rights per translation, not per ancient text); ethnonyms drift and are reused; outsiders' scripts and languages need specialists (Meroitic is only partly understood) |
| Links | external demand and supply in the Red Sea module (India, Aksum, Arabia); subsidies and tribute paid to outsiders (fiscal outflow); conflict participants; exotic goods as price anchors |
| Candidate data | Trismegistos (people, places, texts across languages); Pleiades (places outside the empire, partly); Chinese texts via the Chinese Text Project (check terms); epigraphic corpora for Arabian and Aksumite inscriptions (to identify) |

## DOM-TEC — Technology

| Aspect | Content |
|---|---|
| Phenomena | water power (mills, e.g. Barbegal; water-lifting devices); mining and metallurgy (hydraulic mining, cupellation); shipbuilding (hull construction transition, ship size); construction (concrete, cranes, aqueducts, roads); agriculture (presses, harvesters); glass; navigation (monsoon sailing); timekeeping and mechanisms |
| Entities | `Technology` (a SKOS concept, e.g. "vertical waterwheel"), `Installation` (a dated, placed instance, e.g. a mill site with phases), `TechClaim` (attributed claim of adoption, date or capacity), `Text` (technical authors such as Vitruvius, Pliny, Hero, Frontinus) |
| Key debates | Finley's "technological stagnation" vs. the revisionist view (Greene 2000; Wilson 2002, "Machines, power and the ancient economy"); scale of water-power use; productivity effects |
| Observation problems | adoption is observed through surviving, excavated and published installations. Mills are under-recognised in older excavations; diffusion curves mostly measure *archaeological visibility* |
| Links | transport-cost parameters (ship tonnage, road speed); productivity (milling, mining); mining → silver/lead → coinage and pollution proxies; military technology |
| Candidate data | OXREP databases (shipwrecks, mining, presses; check access); shipwreck catalogues (Parker 1992 and later updates); DARMC layers (some already used) |

## DOM-DEM — Population, health status and settlement

| Aspect | Content |
|---|---|
| Variables | population size (bounded, by region); urbanisation (Hanson cities, have); household structure (Egyptian census returns: Bagnall & Frier 1994); stature and health (skeletal studies, e.g. Koepke & Baten 2005); migration |
| Debates | model life tables vs. data; size of the imperial population (wide ranges); urban rates |
| Rule | population enters models only as bounds or scenarios, with sources per bound |

## DOM-MON — Money, coinage and prices

| Aspect | Content |
|---|---|
| Variables | coin production and types; debasement (silver fineness analyses, e.g. Butcher & Ponting 2014); hoards; price series (Harper 2016, have); price edicts (Diocletian 301 CE) |
| Rule | the nominal/bullion/purchasing-power separation (units rules) extends here. A debasement series is a metal-content claim, not an inflation rate |

## DOM-INS — Institutions, law and the fiscal state

| Aspect | Content |
|---|---|
| Content | tax regimes and rates (scoped, attributed); citizenship (e.g. the 212 CE grant); legal texts (Digest, Theodosian Code); administrative geography (provinces over time); the military supply system |
| Rule | an institution is attached to a jurisdiction and a period with dating evidence; "Roman law" is never applied timelessly |

---

## Cross-domain link register (hypothesised mechanisms)

Each row is a **hypothesis channel** to be evidenced link by link, not an established effect. Each link needs its own evidence and its own rival.

| ID | Chain | Typical rival | Hardest link |
|---|---|---|---|
| L01 | Nile flood → harvest → Egyptian tax grain → Alexandria exports → Rome supply | Administrative buffers (storage, other provinces) absorb shocks | Roman-era flood series |
| L02 | Epidemic → labour scarcity → wages/rents ↑, land abandonment | Document production, reporting or monetary change creates the pattern | Mortality denominator |
| L03 | War → fiscal demand → debasement → prices | Bullion supply (mining) independent of war | Dating debasement steps against campaigns |
| L04 | Volcanic cooling → harvest failure → famine/epidemic susceptibility | Coincidence in densely event-filled centuries | Spatial footprint of cooling |
| L05 | Mining output → lead pollution (ice core) → silver coinage supply | Smelting technology or ore source changes the emission factor | Emission factor bounds |
| L06 | Frontier insecurity → hoard non-recovery | Hoards reflect saving and burial customs; recovery reflects modern finding | Hoard deposition model |
| L07 | Indian Ocean demand → Red Sea trade volume → quarter-tax receipts (RQ1) | Fleet size or cargo value composition (existing H1a/H1b) | Desert capacity (D020) |
| L08 | Technology adoption (water mills) → labour productivity | Visibility bias in excavation | Adoption rate vs. publication rate |

The register lives in `docs/expansion/03_question_bank.md` as testable questions. Only those with an identification route are promoted to the hypothesis register.
