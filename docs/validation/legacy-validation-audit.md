# Legacy OCPE validation audit

## Scope and examined revisions

| Revision | Role | Observed verification |
|---|---|---|
| `c0d8678` (`64ef9e2^`) | Pre-refactor numerical/validation stack | 75 passed, 2 strict expected failures |
| `64ef9e296b12e21b1f4909f2c46dc0d5e25169e7` | Authoritative architectural migration commit | Clean editable source install: 45 passed; strict package validation and dependency checks passed |
| `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d` | Pinned current OCPE integration | 121 passed; current upstream left unmodified |

The complete refactor diff, parent validation modules/tests, workflows, migration notes, archived numerical fixtures, documentation, dependencies, and related current validator modules were inspected. The parent tree is available in the working environment as a separate read-only extraction; no upstream branch was reset or overwritten.

## What the legacy system validated

The parent `docs/validation_strategy.md` defines four levels, not merely software unit tests:

1. **Schema and semantics:** YAML syntax, registry cross-references, symbols, units, and equation metadata.
2. **Physiological plausibility:** extreme state bounds, volume conservation, and overflow/underflow checks on simulated outputs.
3. **Clinical-cohort response checks:** orthostatic HR/BP comparisons, including healthy HR rise below 30 bpm and POTS HR rise at least 30 bpm.
4. **Wearable agreement:** Bland–Altman agreement, ICC, CCC, and correlation criteria against reference ECG/IBI measurements.

These levels are not interchangeable. In particular, schema validity was never scientific validation, and a diagnostic threshold check was not proof of diagnostic accuracy.

## Implementation inventory

| Capability | Historical implementation | Evidence produced |
|---|---|---|
| Orthostatic physiological evaluation | `validation/evaluator.py::PhysiologicalEvaluator` | Baseline/tilt HR, peak HR, HR increase, pressure extrema/MAP, initial pressure drop, bound checks, POTS-criterion and baroreflex-compensation checks |
| Extended cohort checks | `validation/validation_suite.py::AdvancedValidationSuite` | Hemodynamic bounds, optional circadian variation, symptom/pressure coupling, beta-blocker HR cap, hydration/volume checks, aggregate pass status |
| Knowledge-base checks | `tools/validate_kb.py`, `tests/test_evidence_layered_validation.py` | Registry/schema/evidence integrity and CI failure on invalid content |
| Review provenance | `validation/sidecar_manifest.py`, `docs/adr/0001-sidecar-yaml-review-validation-tracking.md` | Sidecar hashes/review tracking and scientific-change accountability |
| Numerical behavior | `tests/test_orthostatic_response.py`, `test_steady_state_params.py`, `test_experimental_mode.py` | Orthostatic phenotypes, steady state, perturbation behavior, determinism, preserved strict xfails |
| CI | `.github/workflows/ci.yml` | Python 3.11/3.12, pytest, knowledge-base validation |
| Reference outputs | `results/*.npz` and test fixtures | Large archived synthetic telemetry/reference traces for the former solver |

The evaluator used fixed time windows and beat peaks from the former pulsatile model. Those windows and systolic/diastolic definitions cannot be copied unchanged into the new beat-averaged model. The extended suite also contains intervention and symptom rules that are outside this assignment and are not treated as validated clinical efficacy models.

## Preserved negative scientific results

The legacy suite used strict xfails, so an unexpected pass would fail. Two limitations are especially relevant:

- Neuropathic venomotor denervation with `dV_veno_max=75 mL` produced sustained ΔHR around 21 bpm and a nearly flat dose response (18.5→21.7 bpm); the ≥30 bpm target required future model revision.
- The 0-D arterial Windkessel could not reproduce an upright ΔSBP ≥10 mmHg criterion because pulse pressure narrowed as stroke volume fell, despite a MAP pressor response.

The legacy strategy also records a nominal healthy HR rise of 76.1 bpm and attributes the excessive compensatory tachycardia partly to the absent active skeletal-muscle pump. These are unresolved model limitations, not validation successes. The new framework does not inherit the old outputs or claim that these limitations are solved generally; its own healthy and phenotype tests are independent.

## Refactor commit findings

Commit `64ef9e2` moved numerical simulation, virtual cohorts, sensor synthesis, simulation evaluators, examples, and telemetry into `migration_archive/`, while transforming the knowledge base into versioned OCPE packages. `migration_archive/MIGRATION_NOTES.md` explicitly assigns numerical components to downstream applications and removes simulation/synthetic generation from OCPE 0.1 scope.

The active 45-test suite verifies the new specification/loader/resolver/validator/evidence behavior. It does not execute the archived numerical solver. Archived numerical tests fail if run unchanged at that revision because their former `knowledge_base/` and simulation paths moved. This is a migration/path issue and is not silently counted as either a pass or an active-suite failure.

At the pinned current OCPE revision, the temporary archive has been removed. Numerical simulation remains outside upstream. Consequently, the disease repository must provide its own executable equations and solver while using OCPE for semantics, units, evidence, packages, and observation exchange.

## Dependencies and external services

- Parent numerical stack: NumPy, SciPy, PyYAML, pytest; the historical `requirements.txt` pins NumPy 2.4.6, SciPy 1.17.1, and PyYAML 6.0.3.
- Refactored OCPE: Python package under `implementations/python`, package schemas, loader, resolver, units, validator, and CLI.
- Historical CI: GitHub Actions on Python 3.11/3.12 with read-only repository permissions.
- No external validation web service is required. Source-checkout path assumptions matter for package and fixture discovery.
- Archived NPZ telemetry is large synthetic output, not independent clinical reference data.

## Migration decisions

Preserve the scientific intent of separate semantic, numerical, physiological, and empirical checks; deterministic fixtures; explicit negative results; strict CI; and provenance. Adapt time windows and metrics to the new state/output model. Retire virtual cohort generation, treatment-efficacy assertions, symptom scoring, and sensor synthesis from this assignment. Do not copy the old solver or large NPZ telemetry merely to make the new repository appear compatible.

The target implementation and verification matrix is in `validation-migration-plan.md`. Migration is considered verified only where the corresponding new capability has actually executed; a document or an archived file alone is not completion.
