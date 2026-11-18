# Roadmap

Where this repository is going, what is explicitly **not** in scope, and the
limitations that remain unresolved. Status language follows the maturity
model in `docs/validation/validation-architecture.md`: nothing here is
clinically validated, and no planned work changes that.

## Current state (snapshot)

- **Stage 1.2 scientific remediation is executed on the Stage 1.1 (model version 0.3.0) architecture.** The twelve states, five conserved stressed-volume compartments, separate aortic/carotid sensors, three autonomic effector states, explicit tilt geometry, and independent cerebral pressure/CO2 pathways are preserved. Nonzero effective dependent heights now apply to every peripheral venous bed, including the residual compartment. Healthy sustained HR rise is 15.467 bpm, early CO reduction 14.570%, caudal pooling 302.962 mL, and end-CFI reduction 4.407%; all four POTS configurations and Long-COVID-autonomic pass the unchanged sustained ≥30 bpm scenario criterion with MAP floors above 70 mmHg. Six of eight Zaidi comparisons pass; both 60° CO comparisons remain misses at 15.801% and 15.800% versus 17–20%. ME/CFS CFI reduction is 24.652%, within 15–35%. Current evidence is in `validation/stage1-2/` and `docs/stage1-2/`. Full-suite execution is **343 passed, 1 skipped**, with strict traceability 0/0/0 and strict OCPE validation 0/0. Overall scientific readiness is **PARTIAL**, not clinical readiness. Stage 1.1's eight Zaidi misses and five sustained-HR failures remain preserved as exact historical evidence, not current claims.
- The Stage 1 (0.2.0) record below is preserved history, superseded by the
  0.3.0 record above:
  all seven validation layers passed with executable tests and independent
  commit-bound PASS records documented in `docs/stage1/final-validation-report.md`
  and preserved in Git history.
  The full suite passed **287 tests** with two intended soft-anchor warnings at
  source/configuration commit `fb13cb21aa811da9babff6b271f006b8c79ec30f` (counted once per parametrized case;
  dual-marked tests make per-layer counts sum higher), and no required marker
  selection is empty. All 26 validation-registry records are PASS and bound to
  that tested source commit.
- Strict scientific traceability and strict OCPE package validation complete
  with zero errors and zero warnings.
- Six curated demonstrations run and are pinned in
  `simulations/simulation_registry.yaml` (19 protocols, 11 simulation
  records at 0.3.0); the six demonstration scripts regenerated 16 persisted
  0.3.0 runs. The Stage 1 four-compartment
  eleven-state revision (`docs/stage1/revised-physiological-architecture.md`)
  is historical model version 0.2.0. Deterministic sensitivity exports
  cover **61 local, 27 grid, and 3 chronotropic-split scenarios** at 0.3.0
  (the Stage 1 record of 42 local, 18 grid, 3 split is preserved history); no
  scenario in the current hEDS grid ends below the 70 mmHg MAP screening
  threshold, while the pre-revision below-70-mmHg failures remain preserved
  as historical results under `validation/baseline/stage0/` and in the
  legacy audit.
- CI configuration includes a pull-request gate (lint, full tests, strict
  audit, strict OCPE package validation) and an extended workflow
  (demonstrations, sensitivity, seven-layer runner). Local execution is not a
  substitute for successful remote runs on both Python 3.11 and 3.12.

## Near-term

1. **Resolve the remaining Stage 1.2 empirical limitations.** The two 60° CO misses, healthy end-tilt MAP over-defence (108.846 mmHg versus 100 mmHg supine), narrow caudal-pooling margin, and un-recalibrated non-POTS geometry overrides require reviewed scientific work. Do not widen bands, add expected failures, or tune chronotropic gains to conceal them. Stage 1.1's more extensive failures remain preserved history rather than open current results.
2. **Obtain independent empirical benchmarks** with no calibration overlap,
   explicit construct mapping, and prospective acceptance metrics before any
   integrated disease model is assigned M4.
3. **Resolve or reject the assumed hEDS venous-compliance mechanism** using
   defensible vascular evidence and structural analysis. The current
   compliance × gravity grid contains no below-70-mmHg MAP regimes, but the
   compliance magnitude remains an unmeasured assumption and the
   pre-revision grid failures (minimum approximately 37.84 mmHg) are
   preserved as historical results; neither the historical failures nor the
   current clean grid justifies raising the scenario above M2.
4. **Curate empirical source artifacts and permissions** for any new data in
   `validation/fixtures/`, per `docs/scientific-change-management.md`.
5. **Improve distribution portability** so required phenotype, protocol,
   registry, and OCPE package data are available without an implicit source
   checkout, while preserving exact hashes and provenance.
6. **Verify remote CI on Python 3.11 and 3.12** and preserve the reports as
   commit-specific records; never silence an empty or failed layer.
7. **Deepen structural validation** of PEM kinetics, orthostatic recovery,
   comorbidity composition, and cross-disease heterogeneity before expanding
   the parameter space. This includes the residual 60° CO misses, healthy
   pressure over-defence, narrow pooling margin, and approximately 5.7-hour
   post-bout PEM threshold crossing relative to the 12–48-hour daily-activity
   onset window.

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
- **Healthy orthostatic response.** Stage 1.2 brings early CO, sustained HR, pooling, and CFI within their preserved broad bands, but the result is calibration agreement rather than independent validation. The 60° CO reductions remain below 17–20%, healthy end-tilt MAP remains 8.846 mmHg above supine, and pooling is only 2.962 mL above the lower band edge. Stage 1.1 and Stage 1 healthy misses remain unchanged historical evidence.
- **POTS and Long-COVID-autonomic scenario interpretation.** All four POTS configurations and Long-COVID-autonomic now pass the unchanged sustained ≥30 bpm criterion without gain changes. This does not establish patient-level identification, symptom persistence, medication response, or mechanistic subtype validation. Hyperadrenergic POTS still lacks an independent catecholamine/non-baroreflex state. Stage 1.1's five criterion failures remain historical negative results.
- **Retained non-POTS geometry.** ME/CFS, hEDS, and Long-COVID-autonomic keep Stage 1.1 fixed-offset-derived splanchnic/lower-limb heights and were not recalibrated against the new healthy/POTS values. Their ratios to healthy are inherited scenario assumptions, not anatomical or severity claims.
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
