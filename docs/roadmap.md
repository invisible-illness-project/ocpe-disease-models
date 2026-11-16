# Roadmap

Where this repository is going, what is explicitly **not** in scope, and the
limitations that remain unresolved. Status language follows the maturity
model in `docs/validation/validation-architecture.md`: nothing here is
clinically validated, and no planned work changes that.

## Current state (snapshot)

- All seven validation layers have executable tests and independent PASS
  records in `validation/reports/validation-report.json`: 228 tests are
  collected overall, and no required marker selection is empty.
- Strict scientific traceability and strict OCPE package validation complete
  with zero errors and zero warnings.
- Six curated demonstrations run and are pinned in
  `simulations/simulation_registry.yaml`. Deterministic sensitivity exports
  cover 14 local and 18 grid scenarios; invalid hEDS pressure regimes remain
  visible as failures rather than being filtered.
- CI configuration includes a pull-request gate (lint, full tests, strict
  audit, strict OCPE package validation) and an extended workflow
  (demonstrations, sensitivity, seven-layer runner). Local execution is not a
  substitute for successful remote runs on both Python 3.11 and 3.12.

## Near-term

1. **Obtain independent empirical benchmarks** with no calibration overlap,
   explicit construct mapping, and prospective acceptance metrics before any
   integrated disease model is assigned M4.
2. **Resolve or reject fragile hEDS parameter regimes** using defensible
   vascular evidence and structural analysis. The below-70-mmHg grid cases
   must not be tuned away or hidden.
3. **Curate empirical source artifacts and permissions** for any new data in
   `validation/fixtures/`, per `docs/scientific-change-management.md`.
4. **Improve distribution portability** so required phenotype, protocol,
   registry, and OCPE package data are available without an implicit source
   checkout, while preserving exact hashes and provenance.
5. **Verify remote CI on Python 3.11 and 3.12** and preserve the reports as
   commit-specific records; never silence an empty or failed layer.
6. **Deepen structural validation** of PEM kinetics, orthostatic recovery,
   comorbidity composition, and cross-disease heterogeneity before expanding
   the parameter space.

## Explicitly out of current scope

- **Stage 2 — synthetic wearable dataset generation.** Signal synthesis and
  wearable-sensor modeling are Lamina's domain (legacy validation-strategy
  level 4: ICC, Bland–Altman limits of agreement, Pearson agreement against
  wearable telemetry). This repository does not generate synthetic wearable
  datasets and does not plan to in the current scope; that boundary is
  documented, not a gap we claim to cover.
- **Stage 3 — flare prediction.** No longitudinal flare forecasting, symptom
  prediction, or individual-patient prediction is in scope. Current
  sensitivity and scenario runs are deterministic computational grids, not
  patient samples or population estimates.
- **Clinical validation.** No maturity level (M0–M4), evidence grade (E0–E5),
  or green CI run establishes clinical validity or diagnostic accuracy;
  nothing on this roadmap seeks it.
- **Wearable agreement metrics** of any kind (see Stage 2).

## Unresolved limitations (preserved, not closed)

These are tracked open items from the validation migration plan and runbook;
listing them here preserves them — their appearance on this roadmap is not a
resolution.

- **POTS generalization.** The calibrated neuropathic, hyperadrenergic,
  hypovolemic, and mixed scenarios now meet the declared orthostatic HR-rise
  criterion, but this does not resolve patient-level identification, symptom
  persistence, medication effects, or the legacy model's documented dose
  response and systolic-pressure failures. Those historical negative results
  remain unchanged.
- **hEDS physiological fragility.** Three declared compliance/gravity grid
  scenarios end below 70 mmHg MAP. The assumed venous-compliance mechanism is
  therefore hypothesis-sensitive and remains M2.
- **Empirical anchor curation.** Which additional published group-level values
  enter `validation/fixtures/`, and under what licenses/permissions, is
  undecided. Existing anchors are literature-derived plausibility checks, not
  redistributed patient datasets.
- **Legacy scope.** Current layers 2–5 execute locally, so legacy numerical
  results are historical comparators rather than evidence for the new model.
  No source-compatibility wrapper or wearable-agreement capability is claimed.
- **Package-data limitation.** The wheel ships only the Python package;
  running requires a source checkout (or `OCPE_DM_ROOT`) because phenotypes,
  protocols, registries, and the OCPE domain package are repository data
  (see `docs/reproducibility.md`).
- **Platform numerics.** Cross-platform trailing-digit solver differences are
  absorbed by acceptance tolerances rather than eliminated.
