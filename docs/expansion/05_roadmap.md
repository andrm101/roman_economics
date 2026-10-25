# Roadmap for the expansion

**Status:** proposal. The new WPs are appended after WP9. Existing IDs do not change.

## Ordering principle

Infrastructure that every domain shares comes first: time, identity, coverage and the agent harness. Then **one** cross-domain question (RQ-X1), using data mostly in hand. Domains are ingested only to the depth that a registered question requires. Breadth comes from the coverage maps, not from modelling everything.

| WP | Content | Depends on | Acceptance test |
|---|---|---|---|
| WP3 (open) | Novelty audit, now including the cross-domain literature: Harper 2017 and its critics; MERCURY; Seshat; climate-history syntheses | — | Comparison table; contribution statements for RQ1 **and** RQ-X1 |
| WP10 | Shared expansion infrastructure: time model and dating library (no year 0; calendar rules); `IdentityClaim`; `TransferAssumption`; `CoverageCell`; ontology 0.2.0; CQ12–CQ19 shapes | WP9 | Round-trip and SHACL tests for the new classes; the dating Monte Carlo reproduces known interval-overlap cases; the circular-dating check catches a planted cycle |
| WP11 | Agent harness (Part 2 of the docs): role definitions, task contracts, hooks, permissions, review queue | WP10 | A dry run on one existing source performs discovery → review packet with zero manual edits. Guardrail tests fail on planted violations: fake page, unapproved promotion, rights breach, held-out peek |
| WP12 | Candidate dataset rights and availability audit (`expansion_source_candidates.csv` → `source_register.csv`) | WP11 | Every candidate has a verified status or is marked unavailable; nothing is cited as read without a parse manifest |
| WP13 | Coverage maps for DOM-EPI, DOM-MON, DOM-CLI over Egypt and the eastern Mediterranean, 100–300 CE | WP12 | CQ16 regenerates deterministically; maps are published as an artifact |
| WP14 | RQ-X1 registration and test: the 160–187 price break, M-labour vs. M-money vs. M-record | WP3, WP13 | Manifest committed before the run; dating-resampled null; composition-stable subsample; result reported as discriminated, partly discriminated, or not identified |
| WP15 | Event register v0 (DOM-WAR): campaigns and revolts 100–300 CE from primary texts already in Perseus TEI, with identity claims | WP10, WP11 | CQ12–CQ13 answered; each event has ≥1 locus; single-source events flagged |
| WP16 | Climate module v0 (DOM-CLI): ingest 2–3 published reconstructions plus an eruption list, with footprints and versions | WP12 | CQ14 enforced: every out-of-footprint use has a TransferAssumption and a sensitivity run |
| WP17 | External accounts v0 (DOM-EXT): Red Sea–relevant outsider accounts (Aksum, South Asia, China), linked to the RQ1 module | WP12 | Three-class separation enforced by SHACL; CQ15, CQ17 |
| WP18 | Technology module v0 (DOM-TEC): installation register for one technology (water mills or shipwreck tonnage) with a visibility model | WP12 | CQ18; an adoption curve with and without typological dates |
| WP5–WP8 | (unchanged) M1, M2, synthetic framework, paper | — | as before |

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Scope creep: breadth without a question | A large, unvalidated "twin" that cannot support any claim | The gate in `00_charter.md` §5; a domain is ingested only for a registered question |
| Grand-narrative pull ("climate/plague caused the fall") | Post-hoc attribution | Rival-first question design; identification strategy before data; RQ-X7 kept as a non-identification exercise |
| Dating error dominates | Spurious cross-domain correlations | The time model and dating Monte Carlo are mandatory for cross-domain joins |
| Rights | Unpublishable corpus | WP12 before ingestion; per-translation rights |
| Agent error at scale | Many plausible but wrong rows | Candidates are not evidence; human promotion; auditor; held-out benchmarks per extractor and domain |
| Specialist knowledge gaps (aDNA, palaeoclimate, Meroitic, Chinese) | Misread evidence | Treat such evidence through published, inspected syntheses with attribution; flag for specialist review; never let an agent "read" a specialist dataset beyond its documentation |

## Recommendation

1. **Close WP3** with the cross-domain literature included.
2. **Build WP10 and WP11.** They are cheap and reusable, and the agent deployment depends on them.
3. **Run RQ-X1.** It is the cross-domain question most likely to yield a defensible result from data already partly in hand. It also tests the expansion machinery (dating, coverage, observation model) on a well-known debate.

The other domains stay documented until a question needs them.
