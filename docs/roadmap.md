# Roadmap

Where this repository is going, what is explicitly **not** in scope, and the limitations that remain unresolved. Status language follows the maturity model in `docs/validation/validation-architecture.md`: nothing here is clinically validated, and no planned work changes that.

## Current state (Stage 1.3 snapshot)

- **Stage 1.3 is implemented as model/package 0.4.0.** The twelve states, five conserved stressed-volume compartments, separate aortic/carotid sensors, three autonomic effector states, explicit tilt geometry, and independent cerebral pressure/CO₂ pathways are preserved. Peripheral compliances are redistributed, a one-sided dependent-venous quadratic elastance is added, common effective anatomy replaces eight phenotype-specific height overrides, and baroreflex/vascular/cardiac/cerebral parameters are revised as experimental assumptions.
- **Stage 1.2 was reproduced before modification.** Fresh exact-commit worktrees reproduced 957/957 reported numeric fields and 277/277 identifiers/status fields, with maximum absolute numerical difference 7.25 × 10⁻¹⁵. Missing audit Git objects are disclosed in `docs/stage1-3/baseline-reproduction.md`.
- **Healthy Stage 1.3 70° outcomes** are sustained HR rise 13.298 bpm, end MAP 102.253 mmHg, caudal pooling 469.395 mL, residual-systemic volume change −17.931 mL, and end-CFI reduction 4.961%. At direct 60° comparison, CO/SV reductions are within the preserved bands; reusing those bands at 70° is explicitly extrapolated. These are calibrated scenario agreements, not independent validation.
- **Phenotype criteria remain active.** Four POTS configurations and Long-COVID-autonomic pass the unchanged sustained ≥30 bpm scenario criterion; neuropathic POTS clears it by only about 0.093 bpm. ME/CFS CFI reduction is 24.538%, within 15–35%. Common anatomy does not validate any phenotype mechanism.
- **Mechanisms were evaluated independently before combination.** The audit linear proposal failed the preserved orthostatic comparisons and was rejected. The final nonlinear combination and all isolated effects are preserved in `validation/stage1-3/scientific-comparison-matrix.md`.
- Six demonstrations regenerate 16 persisted runs. The simulation registry contains 19 protocols and 12 current simulation records at 0.4.0. Sensitivity exports contain 96 local, 27 deterministic grid, and 3 fixed-total chronotropic-split scenarios. None is a synthetic patient or population sample.
- Current execution evidence is in `validation/reports/`, `validation/reproducibility.json`, and `docs/stage1-3/implementation-and-validation.md`. Strict traceability and strict OCPE structural validation are separate from scientific validity.
- Stage 1.2, Stage 1.1, and Stage 1 documents and outputs remain historical records. Their failures and limitations are not rewritten as current Stage 1.3 results.

## Near-term scientific priorities

1. **Test the new constitutive structure independently.** Evaluate the one-sided quadratic dependent-elastance law and coefficient against regional pressure/volume evidence not used for calibration; compare plausible alternative forms.
2. **Obtain non-overlapping empirical benchmarks.** Use prospective multi-angle HR/MAP/CO/SV data, including a genuine 70° experiment, before upgrading scientific readiness. Do not reuse calibration targets as external validation.
3. **Address narrow margins and pressure compensation.** Direct 60° CO passes by only about 0.081 percentage points, neuropathic-POTS sustained HR by about 0.093 bpm, and healthy end-tilt MAP remains 2.253 mmHg above supine.
4. **Deepen identifiability analysis.** Move beyond local deterministic perturbations to transient data, profile or global methods, and explicit structural alternatives. Do not infer patient parameters from the present group bands.
5. **Resolve phenotype assumptions.** Seek evidence for the neuropathic 0.34 range exception and hEDS compliance 70; represent non-baroreflex catecholamine mechanisms before claiming hyperadrenergic specificity.
6. **Deepen cerebral and PEM structural validation.** Preserve independent declared CO₂, fixed-outflow-pressure, and phenomenological-PEM limitations; do not convert normalized states into measured clinical scores.
7. **Curate empirical artifacts and permissions** for any new data in `validation/fixtures/`, per `docs/scientific-change-management.md`.
8. **Improve distribution portability** so required phenotype, protocol, registry, and OCPE package data are available without an implicit source checkout, while preserving exact hashes and provenance.
9. **Verify remote CI on Python 3.11 and 3.12** and preserve commit-specific reports; never silence an empty or failed layer.

## Explicitly out of current scope

- **Stage 2 — synthetic wearable dataset generation.** Signal synthesis and wearable-sensor modeling require separately approved work. This repository does not generate synthetic wearable datasets. Stage 1.3 numerical agreement does not establish readiness for general-purpose synthetic data.
- **Stage 3 — flare prediction.** No longitudinal flare forecasting, symptom prediction, or individual-patient prediction is in scope. Sensitivity rows are deterministic model scenarios, not patients.
- **Clinical validation.** No maturity level, evidence grade, green CI run, or within-band comparison establishes clinical validity, diagnostic accuracy, treatment efficacy, or patient-specific calibration.
- **Wearable agreement metrics.** No ICC, CCC, Bland–Altman, or equivalent wearable validation capability is claimed.

## Unresolved limitations (preserved, not closed)

- **Calibrated dependent elastance.** The quadratic form and 0.0001 mmHg/mL² coefficient are high-uncertainty structural assumptions, not measured tissue properties.
- **Calibration overlap.** The same group-level bands and phenotype criteria used during remediation are reported as outcomes. Passing them is not independent validation.
- **Parameter non-identifiability.** Baroreflex weighting, chronotropic split, compliance/elastance, geometry/blood volume, and cardiac/vascular compensation are not uniquely identified.
- **Effective rather than measured anatomy.** Common heights remove unsupported disease differences but remain lumped effective parameters.
- **POTS and Long-COVID interpretation.** Scenario threshold agreement does not resolve patient identification, symptoms, medication effects, or subtype mechanisms. Hyperadrenergic POTS lacks an independent catecholamine/non-baroreflex state.
- **hEDS mechanism status.** Lower-limb compliance 70 mL/mmHg is exploratory. The current grid contains no below-70-mmHg MAP scenario, but this does not validate the mechanism; historical grid failures remain preserved.
- **Cerebral simplifications.** Fixed effective outflow pressure is not resolved ICP or thoracic CVP. ETCO₂ is declared and bounded, not inferred from posture or converted to PaCO₂.
- **PEM kinetics.** PEM remains normalized and phenomenological; the prior approximately 5.7-hour post-bout threshold-crossing caveat and daily-activity onset-window limitation remain.
- **Package-data limitation.** Running requires a source checkout or `OCPE_DM_ROOT` because phenotypes, protocols, registries, and the OCPE domain package are repository data.
- **Platform numerics and CI.** Cross-platform trailing-digit solver differences are absorbed by tolerances. Local execution is not a substitute for verified remote Python-matrix runs.
