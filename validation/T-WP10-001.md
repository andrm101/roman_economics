# Validation: T-WP10-001 (implementation run)

Result: PASS
Branch agent/T-WP10-001, commit 014f6ed, diff base fa465ab. Validator: AG-VAL, 2026-10-25.

## Checks
| Check | Result | Evidence |
|---|---|---|
| `pytest -q` (full suite) | PASS | 205 passed, 0 failed, 1 skipped |
| `tests/test_time.py` | PASS | 24 passed |
| `python -m romeco.cli graph` | PASS | core.ttl 3074 triples, SHACL conforms=True, warnings=4; full.ttl 55106 triples, SHACL conforms=True, warnings=4 |
| `python -m romeco.cli agents-check` | PASS | `agents-check: OK` |
| `python -m romeco.cli benchmark` | N/A | no extractor code changed |
| Acceptance: 1 BCE -> 0, 1 CE -> 1; (-1, 1) spans 2 years | PASS | `test_astronomical_conversion_acceptance`, plus `test_year_zero_rejected`, `test_roundtrip` |
| Acceptance: planted A->B->A reported circular | PASS | `test_planted_two_cycle_is_circular`, `test_longer_cycle_and_other_side`, `test_cycle_downstream_is_circular` |
| Acceptance: Monte Carlo reproducible for fixed seed | PASS | `test_monte_carlo_reproducible_for_fixed_seed` |
| D033 coverage | PASS | tests for overlap_frac and Jaccard, inclusive containment, lag 0 <= lag <= k (negative k rejected), uniform seeded draws, cycles of any length |
| Diff within contract outputs and ag-mod grant | PASS | Changed files are `src/romeco/time.py`, `tests/test_time.py` (both in outputs_expected and the ag-mod grant) and `tasks/reports/T-WP10-001.md`. The report file is not listed in outputs_expected but is covered by the grant `tasks/reports/**` and the task-protocol. |
| Forbidden: no change to existing dated records | PASS | The diff touches no file under data/, registers/ or config/. `time.py` has no file I/O or CSV writes. |

## Not checked
- Correctness of time.py beyond the tests present (no independent review of the numerical logic).
- The skipped test in the full suite was not investigated.
- The 4 SHACL warnings were not compared against a previous baseline.
- The accuracy of the content of tasks/reports/T-WP10-001.md.
