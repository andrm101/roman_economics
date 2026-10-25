---
name: audit-result
description: Independently audit a finished result (experiment, WP result section or curated batch) without the producer's reasoning. Use before any result is reported as a finding.
---

# Independent audit

You start cold. Do not read the producing agent's transcript or task report until step 5.

1. Read the claim of the result: the WP result section or the experiment's `headline` in `registers/experiment_registry.csv`.
2. **Re-derive it.** Re-run the code from a clean checkout of the branch, using the recorded seed and config. Compare numbers exactly.
3. **Spot-check provenance.** For at least five input claims (all of them if fewer), follow assertion → source → page/locus. Open the page image or edition yourself where rights allow. Record any mismatch.
4. **Check the claim language.** Every causal verb ("caused", "led to", "because", "drove") must be backed by a registered identification strategy. Every number in prose needs a tag. Check uncertainty is reported, and check whether the dominant uncertainty source is included.
5. Only now read the producer's report. Note anything it says was not checked that you also did not check.
6. Write `audits/<task_id or experiment_id>.md` with a verdict: `pass`, `pass_with_notes` or `fail`, plus the list of issues. You never fix the result yourself.
