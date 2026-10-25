# Expansion charter: the Roman World Evidence Twin

**Status:** proposal (brainstorm, 2026-10-25). Nothing in `docs/expansion/` is implemented unless a WP result section says so. Decision: D031.

## 1. What we are building

The current project is a bounded pilot: the Egypt–Red Sea–India trade c. 50–200 CE (RQ1). The expansion keeps that pilot as the first module. Around it, it builds a single ecosystem covering the Roman world and the peoples it interacted with, across these domains:

- economy;
- war and conflict;
- epidemics;
- climate and environment;
- external peoples and their own accounts;
- technology;
- the demography, institutions and settlement that connect them.

We call it an **evidence twin**, not a digital twin. The difference is the core design rule.

| | Digital twin (engineering sense) | Evidence twin (this project) |
|---|---|---|
| State | Fully specified, continuously updated from sensors | Specified only where attested. Elsewhere bounded, or explicitly unknown |
| Gaps | Filled by the model | Shown as gaps. Filled only inside labelled experiments |
| Simulation | Runs the twin | Runs *on* the twin, one hypothesis at a time, with an observation model |
| Validation | Against live data | Against held-out evidence, if any. Otherwise reported as unvalidated |
| Output | "The state of the system" | "What the evidence allows, and what each mechanism would imply" |

A full-state twin of antiquity would consist mostly of generated values. Our brief forbids synthetic data that looks like recovered history (see the *Synthetic data* rules), so that design is excluded at the root.

## 2. Principles carried over unchanged

These principles already hold in WP0–WP9 and apply to every new domain:

1. **Layers.** There are four: object, edition/dataset, modern interpretation and project transformation. They are never merged.
2. **Three labels per claim.** Record origin, epistemic status and review status are independent.
3. **Candidates are not evidence (D024).** Machine extraction proposes; a human promotes.
4. **Rivals survive (D028).** A contested question keeps every position. Selection is a logged decision.
5. **Independence is counted, not assumed.** Ten modern authors citing one source give one observation (CQ11).
6. **No universal units or calendars.** Every conversion is a named, scoped rule.
7. **Synthetic data is labelled at the row level.** The label survives joins, graphs and plots.
8. **Causal claims need an identification strategy.** Temporal coincidence of coarse-dated series is not one.

## 3. Principles added by the expansion

9. **Coverage before content.** Each domain publishes a coverage map before any synthesis. It records which places, periods and resolutions have *any* evidence, and of which class. An empty cell means "no evidence ingested", never "nothing happened".
10. **Time is an interval with a dating method.** Events, records and series values carry `[t_low, t_high]`, a dating method and a resolution. Joins across domains must state how they handle overlapping or uncertain intervals (§4 of `02_ontology_and_data.md`).
11. **Group names are labels in sources, not natural kinds.** "Goths", "Saracens" and "Seres" are attributed labels used by a given author at a given date. Identity across sources is a reviewable claim, exactly like place identification (CQ7).
12. **Accounts are perspectives.** Roman sources on outsiders, outsiders' sources on Rome, and archaeology are three different evidence classes. The archaeology of an "enemy" is not confirmation of a Roman narrative about them.
13. **Proxies are not the variable.** A tree-ring width, a lead deposition rate or a burial count is a measurement with its own transfer function to temperature, mining output or mortality. The transfer function is a parameter with evidence and bounds.
14. **Domain models answer domain questions.** The ecosystem shares data, IDs and time, but no single model must explain everything. A cross-domain claim (e.g. climate → harvest → prices → unrest) is a chain of separately evidenced links, and its weakest link is reported.
15. **Grand-narrative caution.** "Decline and fall" explanations (climate, plague, barbarians, debasement) are hypotheses in a register with their rivals and critics. The project's name ("Growth and Fall") describes the topic, not a conclusion.

## 4. Non-goals

- A single empire-wide GDP, population or temperature curve presented without bounds and coverage.
- Filling the map with simulated settlements, battles or epidemics so the twin "looks complete".
- Adjudicating grand narratives by fit alone: if several mechanisms fit, we report observational equivalence.
- Bulk acquisition that ignores rights: the rights gate applies to every domain.
- Replacing specialists. Readings, identifications and proxy calibrations with high impact need human review.

## 5. Gate: when a domain moves from documented to ingested

A domain module moves from **documented** to **ingested** only when all of these are in place:

1. a coverage map;
2. at least one competency question with a registered expected answer;
3. a rights audit of its candidate datasets;
4. one research question that the module serves, with its rival.

It moves to **modelled** only when the RQ has an identification strategy and the evidence for the test is registered before fitting.

The economy pilot (RQ1) remains the first module through this gate. WP3 (novelty audit) must close before any new domain is modelled (§ roadmap).
