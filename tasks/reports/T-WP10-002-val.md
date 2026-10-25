# Validation: T-WP10-002 (implementation run)

Result: PASS
Branch agent/T-WP10-002, commit 5fe7e07, diff base 64dcbe0. Validator: AG-VAL, 2026-10-25.

## Checks
| Check | Result | Evidence |
|---|---|---|
| `pytest -q` (full suite) | PASS | 221 passed, 0 failed, 1 skipped |
| `tests/test_time.py` | PASS | 40 passed |
| `python -m romeco.cli graph` | PASS | core.ttl 3074 triples, SHACL conforms=True, warnings=4; full.ttl 55106 triples, SHACL conforms=True, warnings=4 (same as T-WP10-001) |
| `python -m romeco.cli agents-check` | PASS | `agents-check: OK` |
| `python -m romeco.cli benchmark` | N/A | no extractor code changed |
| Acceptance: planted circular A/B pair excluded from monte_carlo() without `exclude` | PASS | `test_monte_carlo_auto_excludes_planted_circular_pair` (res.circular == {A, B}); also longer-cycle, downstream and caller-exclude-union tests |
| Acceptance: duplicate record IDs raise | PASS | `test_duplicate_record_ids_raise` (monte_carlo, monte_carlo_join, draw_dates) |
| Acceptance: n_draws=True and n_draws=0 raise | PASS | `test_n_draws_must_be_positive_int_not_bool` (True, False, 0, -1, 1.0, "3", None) for both entry points |
| Acceptance: seed-42 reproducibility from T-WP10-001 still passes | PASS | `test_monte_carlo_reproducible_for_fixed_seed` unchanged and passing; `test_seed_42_default_draws_unchanged_by_hardening` added |
| Acceptance: D034 A=(100,110), B=(110,120) in overlap, not lag; B=(111,120) lag 1; randomised disjointness | PASS | `test_d034_lag_join_disjoint_from_overlap_join_planted`, `test_d034_no_pair_in_both_joins_randomised` (150x150 pairs, k in 0,1,5,30; asserts nonempty overlap and lag sets) |
| Diff within outputs_expected and ag-mod grant | PASS | Changed files: `src/romeco/time.py`, `tests/test_time.py` (outputs_expected, ag-mod grant) and `tasks/reports/T-WP10-002.md` (grant `tasks/reports/**`, not listed in outputs_expected). Working tree clean. |
| Forbidden: no existing dated record changed | PASS | Diff touches nothing under data/, registers/ or config/. |
| Forbidden: no join semantics beyond D034 | PASS | Only the lag predicate changed (`0 <= lag` to `1 <= lag`); overlap and containment code untouched in the diff. |
| Forbidden: T-WP10-001 tests edited only for lag 0 | PASS | One pre-existing test modified (the lag-join inclusivity test: lag0 expectation removed, lag1 added). All other test changes are additions. |

## Observations (not failures)
- Escalation condition on join context: `monte_carlo` on a flat list applies only the "returns to itself" criterion; the "reaches the other side" criterion is provided by a new function `monte_carlo_join(left, right, ...)`. Adding this public function and `extra_dependencies` / `MonteCarloResult.circular` goes beyond the literal acceptance text but stays inside time.py and does not alter join semantics. The researcher may want to confirm that the split is acceptable.
- Lag join with k=0 is accepted and returns no pairs.

## Not checked
- Correctness of time.py beyond the tests present (no independent numerical review).
- The skipped test in the full suite was not investigated.
- The 4 SHACL warnings were not compared against a baseline beyond the T-WP10-001 counts.
- The content accuracy of tasks/reports/T-WP10-002.md.
- The truncated tail of the diff (end of `monte_carlo_join` and the final seed-42 test) was not read line by line; those tests pass.
