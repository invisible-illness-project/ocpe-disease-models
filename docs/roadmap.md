# Roadmap

Where this repository is going, what is explicitly **not** in scope, and the
limitations that remain unresolved. Status language follows the maturity
model in `docs/validation/validation-architecture.md`: nothing here is
clinically validated, and no planned work changes that.

## Current state (snapshot)

- All seven validation layers have executable tests and independent
  commit-bound PASS records in `validation/reports/validation-report.json`.
  The full suite passed **287 tests** with two intended soft-anchor warnings at
  source/configuration commit `fb13cb21aa811da9babff6b271f006b8c79ec30f` (counted once per parametrized case;
  dual-marked tests make per-layer counts sum higher), and no required marker
  selection is empty. All 26 validation-registry records are PASS and bound to
  that tested source commit.
- Strict scientific traceability and strict OCPE package validation complete
  with zero errors and zero warnings.
- Six curated demonstrations run and are pinned in
  `simulations/simulation_registry.yaml`. The Stage 1 four-compartment
  eleven-state revision (`docs/stage1/revised-physiological-architecture.md`)
  is implemented as model version 0.2.0. Deterministic sensitivity exports
  cover **42 local, 18 grid, and 3 chronotropic-split scenarios**; no
  scenario in the current hEDS grid ends below the 70 mmHg MAP screening
  threshold, while the pre-revision below-70-mmHg failures remain preserved
  as historical results under `validation/baseline/stage0/` and in the
  legacy audit.
- CI configuration includes a pull-request gate (lint, full tests, strict
  audit, strict OCPE package validation) and an extended workflow
  (demonstrations, sensitivity, seven-layer runner). Local execution is not a
  substitute for successful remote runs on both Python 3.11 and 3.12.

## Near-term

1. **Obtain independent empirical benchmarks** with no calibration overlap,
   explicit construct mapping, and prospective acceptance metrics before any
   integrated disease model is assigned M4.
2. **Resolve or reject the assumed hEDS venous-compliance mechanism** using
   defensible vascular evidence and structural analysis. The current
   compliance × gravity grid contains no below-70-mmHg MAP regimes, but the
   compliance magnitude remains an unmeasured assumption and the
   pre-revision grid failures (minimum approximately 37.84 mmHg) are
   preserved as historical results; neither the historical failures nor the
   current clean grid justifies raising the scenario above M2.
3. **Curate empirical source artifacts and permissions** for any new data in
   `validation/fixtures/`, per `docs/scientific-change-management.md`.
4. **Improve distribution portability** so required phenotype, protocol,
   registry, and OCPE package data are available without an implicit source
   checkout, while preserving exact hashes and provenance.
5. **Verify remote CI on Python 3.11 and 3.12** and preserve the reports as
   commit-specific records; never silence an empty or failed layer.
6. **Deepen structural validation** of PEM kinetics, orthostatic recovery,
   comorbidity composition, and cross-disease heterogeneity before expanding
   the parameter space. This includes the retained healthy early-CO miss, the
   near-zero healthy end-tilt CFI response despite the approximately 7% control
   finding, and the approximately 5.7-hour post-bout PEM threshold crossing
   relative to the 12–48-hour daily-activity onset window.

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
  hypovolemic, and mixed scenarios now meet the declared **sustained**
  orthostatic HR-rise criterion (mean over the final 120 s of the upright
  window), but this does not resolve patient-level identification, symptom
  persistence, medication effects, or the legacy model's documented dose
  response and systolic-pressure failures. Those historical negative results
  remain unchanged.
- **hEDS physiological fragility (historical) and mechanism status.** The
  three below-70-mmHg compliance/gravity grid scenarios belong to the
  pre-revision aggregated-peripheral model and are preserved unchanged as
  historical results in `validation/baseline/stage0/` and the handoff; the
  current revised grid has no such failures. The assumed lower-limb
  venous-compliance mechanism is nevertheless hypothesis-sensitive and
  remains M2.
- **Healthy orthostatic response.** Early CO reduction remains approximately
  5.64% against a broad 10–30% soft anchor, and end-tilt CFI reduction remains
  approximately 0.003% against the reported 7% control finding and broad 3–11%
  disclosure band. Both warnings are unresolved structural limitations; the
  ME/CFS scenario-band assertion was not weakened to accommodate them.
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
