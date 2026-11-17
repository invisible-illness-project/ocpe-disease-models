# Seven-layer validation report

A pass denotes completion of the declared computational check only. Software execution, numerical convergence, phenotype threshold matching, and group-level empirical agreement are independently necessary and are not clinical validation.

| Layer | Status | Pytest result |
|---|---|---|
| software | PASS | 127 passed, 1 skipped, 202 deselected in 198.15s (0:03:18) |
| mathematical | PASS | 45 passed, 285 deselected in 9.33s |
| physiological | PASS | 64 passed, 266 deselected, 1 warning in 8.15s |
| disease_phenotype | FAIL | 29 passed, 295 deselected, 6 xfailed in 186.51s (0:03:06) |
| empirical | PASS | 10 passed, 320 deselected, 1 warning in 96.46s (0:01:36) |
| sensitivity_uncertainty | PASS | 13 passed, 317 deselected in 124.91s (0:02:04) |
| scientific_traceability | PASS | 40 passed, 290 deselected in 4.16s |

Strict traceability: PASS — 0 errors, 0 warnings.

**Overall: FAIL**
