# Validation T-WP11-001 (AG-VAL): overall PASS

Branch agent/T-WP11-001 vs contract tasks/T-WP11-001.yaml.

| Check | Result | Evidence |
|---|---|---|
| pytest -q | PASS | 180 passed, 0 failed, 1 skipped |
| graph + SHACL | PASS | core.ttl 3046 triples, full.ttl 55078 triples, conforms=True, warnings=4 |
| agents-check (a) | PASS | "agents-check: OK" |
| CQ10 coverage (b) | PASS | Own rdflib run of CQ10 on regenerated full.ttl: exactly 3 rows with claim = claim/ANC-PLINY-DESERT (EXT-113b3df1fa7e-00928-000, EXT-68c25790bd89-00053-001, -002). Each has review_queue/<ext_id>/packet.md; page.png present for the two Adams candidates; Pliny text edition has none (acceptable, no PDF page). INDEX.md present with 3 rows. |
| review_decisions.csv unchanged (c) | PASS | `git diff main --stat -- registers` empty; working tree clean for registers |
| No decisions / human_reviewed (d) | PASS | Branch diff contains only the report; grep of review_queue finds no human_reviewed. The single mention is prose in the report ("no ... human_reviewed status written"), outside the forbidden-text file globs. |
| Report sections (e) | PASS | Summary, Files changed, Checks run, Not checked (non-empty), Escalations all present |
| Diff within outputs (f) | PASS | `git diff main...HEAD`: tasks/reports/T-WP11-001.md only (29 lines). Uncommitted: core.ttl (regeneration; also touched by my graph run) and tasks/T-WP11-001.yaml (approval edit), neither committed. |
| benchmark | N/A | No extractor code changed |

## Observations (not failures)
- Claim scope: CQ10 also returns 8 candidates (12 day) for the distinct claim ANC-PLINY-DESERT-DAYS. The contract says ANC-PLINY-DESERT; exact-claim match gives 3. If the researcher intended the -DAYS claim too, 8 more packets are missing. Needs the researcher's reading.
- Producer's report says pytest was not run; I ran it.
- Report states the hook denied read-only commands mentioning the policy path; I hit the same denial once (a command mentioning the agent config folder). Not worked around.
- core.ttl shows modified (regeneration); line endings only per producer, not verified by me.

## Not checked
- Packet contents against page images/sources (only existence and CQ10 match verified).
- Producer's claim that -001/-002 are distinct or duplicate occurrences.
- Held-out gold not consulted.
