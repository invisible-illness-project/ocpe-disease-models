# Seven-layer validation architecture

## Principles

- Layers are independently executable and reportable.
- A required empty pytest selection is a failure, not a skip.
- Missing references, fixtures, observations, or registry records cannot silently pass.
- Empirical agreement, numerical convergence, and software execution answer different questions.
- Negative results and invalid parameter regimes remain visible.
- M0–M4 maturity is assigned per mechanism/phenotype and is not calculated from total test counts.

## Layer inventory

| Layer | Question | Principal machinery | Registry examples |
|---|---|---|---|
| Software | Does the implementation load, compose, serialize, interoperate, and remain stable? | Unit/integration tests, configuration conflict detection, serialization, OCPE strict validation, regression fixtures | `VAL-SW-*`, `VAL-REGRESSION` |
| Mathematical | Are the implemented equations numerically and dimensionally coherent? | RHS conservation, units, finite states, boundary checks, tolerance/step refinement | `VAL-MATH-CONSERVATION`, `VAL-MATH-CONVERGENCE` |
| Physiological | Are baseline, response direction, feedback, bounds, and recovery plausible? | Resting operating point, tilt response, sympathetic compensation, cerebral recovery | `VAL-PHYS-*` |
| Disease phenotype | Do declared mechanism configurations express the intended heterogeneous scenarios? | POTS subtypes/mixture, exploratory hEDS, ME/CFS PEM, separate Long COVID subgroups, comorbidity conflicts | `VAL-POTS-*`, `VAL-EDS-DIRECTION`, `VAL-ME-PEM`, `VAL-LC-*` |
| Empirical | How do outputs compare with cited published observations? | Predeclared broad group-level scenario bands with population/construct limitations | `VAL-ME-CPET`, `VAL-ME-CBF`, `VAL-EMPIRICAL-ANCHORS` |
| Sensitivity/uncertainty | Which assumptions drive outputs and where do regimes fail? | Local perturbations, two-parameter deterministic grids, configuration hashes, retained MAP failures | `VAL-SENSITIVITY`, `VAL-UNCERTAINTY` |
| Scientific traceability | Can every implemented claim be followed from evidence to output? | Seven registries, JSON Schema, link/orphan/coverage audits, future-scope guard | `VAL-TRACEABILITY`, `VAL-SCOPE-FUTURE` |

## Pytest and runner contract

`pyproject.toml` declares the markers. `scripts/run_validation.py` maps them as follows:

```text
software                 → pytest -m 'software or regression'
mathematical             → pytest -m mathematical
physiological            → pytest -m physiological
disease_phenotype        → pytest -m phenotype
empirical                → pytest -m empirical
sensitivity_uncertainty  → pytest -m sensitivity_uncertainty
scientific_traceability  → pytest -m scientific_traceability + strict audit
```

Each layer writes its own log and status in `validation/reports/`. The overall report does not average or hide layer failures. Strict traceability treats both errors and warnings as release-blocking.

## Traceability audit

The audit loads seven registries and checks:

- schema conformance and duplicate/stable IDs;
- claims without references and mechanisms without claims or exploratory status;
- equations without expressions, assumptions, or provenance;
- parameters without source, estimation method, or provenance;
- implemented mechanisms without resolving validation tests;
- tests without expected behavior, acceptance criteria, or scientific justification;
- simulations without configuration/model provenance;
- broken cross-registry links and orphaned/unused scientific components.

A documentation path for an M0/M1 mechanism does not make it implemented. Explicit `status` controls implementation classification; a mere `implementation:` review-path field cannot trigger an implemented-test requirement. IDs at sentence punctuation are parsed without treating the punctuation as part of the identifier.

## Reports and evidence

- `validation/traceability/audit/traceability_report.json` and `.md`: deterministic scientific-link audit.
- `validation/reports/validation-report.json` and `.md`: independent layer outcomes and environment identity.
- `validation/reports/<layer>.log`: unabridged pytest output for each layer.
- `validation/sensitivity/`: all local/grid scenarios, summary ranges, figure, and failed physiological regimes.
- `validation/reproducibility.json`: exact code/OCPE/dependency/fixture identity for the final snapshot.
- CI artifacts: reports only; no synthetic cohort or large telemetry upload.

Validation-registry results point to these reports and record the code commit actually tested. Historical reports are retained by commit/CI artifact rather than overwritten to imply retrospective success.

## Release interpretation

Software and mathematical success supports implementation reliability. Physiological success supports internal scenario plausibility. Disease-phenotype success supports intended configuration behavior. Empirical success supports bounded comparison with cited observations. Sensitivity quantifies assumption dependence. Traceability supports auditability. None alone—or all together without suitable independent patient data—constitutes clinical validation.
