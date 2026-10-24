# Alignment of the romeco ontology to external standards (WP9.2)

**Policy (D026):**
- Reuse **PROV-O** and **SKOS** directly: they are cheap, stable W3C Recommendations, and the competency questions use them.
- Record **CIDOC CRM**, **CRMinf** and **OWL-Time** as documented alignments only. No IRIs from them are asserted in the graph until a concrete exchange need arises. At that point the versions below are re-checked and a mapping file is added.

Versions were checked 2026-10-24 on the publishers' sites. The pages were read through a machine summary, so re-check before adopting.

| Standard | Version / status | Use here |
|---|---|---|
| PROV-O | W3C Recommendation, 30 April 2013 (`http://www.w3.org/ns/prov#`) | **imported terms**: prov:Entity, prov:Activity, prov:used, prov:wasDerivedFrom |
| SKOS | W3C Recommendation, 18 August 2009 | **imported terms**: concept schemes for status vocabularies and units |
| CIDOC CRM | 7.1.3, released February 2024 (cidoc-crm.org) | alignment only |
| CRMinf | 1.2.1, "Stable", April 2026 (cidoc-crm.org/crminf/fm_releases) | alignment only |
| OWL-Time | W3C Candidate Recommendation Draft, 15 November 2022 (namespace `http://www.w3.org/2006/time#`) | alignment only; dates are kept as integer CE bounds |

| romeco | Closest external notion | Fit and caveat |
|---|---|---|
| rx:Claim | CRMinf I2 Belief (an actor holding a proposition) / prov:Entity | rx:Claim bundles the proposition with its attribution. CRMinf separates I4 Proposition Set from I2 Belief and its I6 Belief Value. Our `epistemic_status` is the *project's* belief value, not the scholar's |
| rx:Interpretation | CRMinf I5 Inference Making (the act) producing an I2 Belief | We store the result, not the reasoning act. Adequate for CQ8–CQ9 |
| rx:Question + rx:hasPosition | CRMinf argumentation (competing beliefs about one proposition set) | Explicit "point of contention" with a selected position and a decision; no direct CRMinf class |
| rx:Reading | CRM E33 Linguistic Object (transcription) + P70 documents | |
| rx:AncientDocument | CRM E22 Human-Made Object (papyrus, ostracon) / E33 (literary work) | Physical object and text are not split, because no CQ needs it |
| rx:PlaceIdentification | CRM E13 Attribute Assignment (assigning an identity) | Good fit: identifications are acts, not facts |
| rx:Place | CRM E53 Place; Pleiades URIs | |
| rx:Derivation / rx:Experiment | prov:Activity; CRMinf S/I classes for computation not needed | |
| rx:Source / rx:FileItem | FRBR/LRMoo Work–Expression–Manifestation–Item (not adopted) | Source ≈ Work/Expression; FileItem ≈ Item |
| date_low_ce / date_high_ce | OWL-Time time:Interval with time:hasBeginning / time:hasEnd | Integer bounds suffice for current CQs; switch if uncertain dating needs richer semantics |
