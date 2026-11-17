# Seven-layer validation report

A pass denotes completion of the declared computational check only. Software execution, numerical convergence, phenotype threshold matching, and group-level empirical agreement are independently necessary and are not clinical validation.

| Layer | Status | Pytest result |
|---|---|---|
| software | PASS | 131 passed, 1 skipped, 202 deselected in 193.81s (0:03:13) |
| mathematical | PASS | 45 passed, 289 deselected in 9.79s |
| physiological | PASS | 64 passed, 270 deselected, 1 warning in 8.23s |
| disease_phenotype | FAIL | 29 passed, 299 deselected, 6 xfailed in 186.28s (0:03:06) |
| empirical | PASS | 10 passed, 324 deselected, 1 warning in 96.97s (0:01:36) |
| sensitivity_uncertainty | PASS | 13 passed, 321 deselected in 125.21s (0:02:05) |
| scientific_traceability | PASS | 40 passed, 294 deselected in 3.67s |

Strict traceability: PASS — 0 errors, 0 warnings.

**Overall: FAIL**
