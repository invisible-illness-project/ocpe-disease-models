# Technical handoff: OCPE disease models

- Release record date: 2026-11-16
- Target branch: `research/initial-disease-modeling-framework`
- Validated source commit: `e87401ddd435d2fd1d5e15420308086051229851`
- Pinned OCPE commit: `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`
- Historical OCPE validation commit: `64ef9e296b12e21b1f4909f2c46dc0d5e25169e7`

This handoff records computational research software, not a clinically validated model, diagnostic device, treatment system, synthetic wearable dataset, or flare predictor.

## A. Executive summary

The target repository now contains an executable, literature-grounded disease-modeling framework with an explicit boundary between OCPE semantics and numerical simulation. OCPE 0.1 supplies identifiers, quantities, concepts, specifications, units, evidence integrity, package validation, and observation exchange. It does not supply the numerical solver used here. SciPy integration, disease phenotypes, protocols, scientific validation, and compact outputs live in the disease repository.

Delivered capabilities include:

- Conservative three-compartment hemodynamics, autonomic feedback, orthostatic protocols, a reduced cerebral-flow index, oxygen-extraction/capacity constructs, and a phenomenological delayed-PEM cascade.
- POTS neuropathic, hyperadrenergic, hypovolemic, and mixed configurations; exploratory hEDS vascular mechanics; ME/CFS post-exertional recovery; and two distinct Long COVID configurations.
- Thirty-eight references, 22 evidence claims, 19 mechanisms, 18 equations, 35 parameter records, 24 validation records, eight simulation records, and generated BibTeX.
- Six required demonstrations, deterministic sensitivity/uncertainty analyses, strict OCPE observation mapping, seven independent validation layers, scientific change controls, CI workflows, and reproducibility metadata.
- Four required legacy/migration documents, including a concrete migration matrix and preservation of historical negative results.

At the validated source commit, the full suite reported **231 passed**. Every required layer passed independently, Ruff passed, strict traceability reported zero errors/warnings/infos, and strict OCPE package validation reported zero errors/warnings. These are local computational results. Remote GitHub matrix execution is configured but is not claimed as completed.

No upstream OCPE files were modified. No secrets or credentials were added. The work was committed in logical units on the feature branch; publication to a remote requires the repository owner's authorized secure operation.

## B. Literature findings and scientific interpretation

### POTS

The reviews cover neuropathic, hyperadrenergic, hypovolemic, and mixed presentations. They retain physiological heterogeneity and contradictory baroreflex findings rather than imposing one universal gain reduction. The adult sustained HR-rise criterion is used as a scenario acceptance metric, not as a diagnostic classifier or proof of model validity. Plasma-volume findings motivate the hypovolemic configuration, but the 0.92 stressed-volume factor is explicitly not a direct conversion of measured plasma-volume deficit. Hyperadrenergic chronotropic gain is calibrated; catecholamine concentration, reuptake, and primary/secondary distinctions are not modeled. The neuropathic resistance gain of 0.35 and hypovolemic baroreflex pressure scale of 6.0 mmHg lie outside their declared local sensitivity ranges; both are explicitly registered as scenario-calibration exceptions, not patient measurements or widened supported ranges.

The implemented scenarios produce orthostatic HR rises of 30.860 bpm (neuropathic), 30.158 bpm (hyperadrenergic), 30.457 bpm (hypovolemic), and 33.351 bpm (mixed). These values are demonstration outputs with calibration overlap, not estimated clinical performance.

### EDS / hEDS

The hEDS work is limited to indirect vascular mechanics. Arterial elasticity or stiffness is not treated as a measurement of venous capacitance, and historical JHS/EDS-HT/EDS-III evidence is not automatically generalized to current hEDS or other EDS subtypes. The peripheral venous compliance of 140 mL/mmHg is an exploratory assumption, so the configuration remains **M2**.

The nominal hEDS scenario produces a 28.163 bpm HR rise. More importantly, three declared compliance/gravity grid scenarios end below 70 mmHg MAP, with a minimum of 37.839 mmHg. These are retained as failed physiological regimes. They demonstrate parameter/model fragility and prohibit a robust clinical interpretation.

### ME/CFS

The literature review distinguishes delayed PEM from immediate exertional fatigue and preserves repeated-CPET heterogeneity, negative replications, selection toward CPET-capable patients, and construct mismatch between normalized capacity and measured VO2. The implemented exertion → delayed stress → thresholded PEM → capacity cascade is explicitly phenomenological and asserts no molecular cause.

Following failure of the original early-onset behavior, the ME/CFS scenario was recalibrated within declared assumption ranges to delayed-stress, PEM-onset, and PEM-recovery constants of 43200, 172800, and 86400 s. The corrected scenario stays below 0.01 PEM during exertion and the first post-exertional hour, reaches a normalized peak of 0.1413 about 39.5 h after the first exertion, shows a 4.45% next-day normalized-capacity reduction, and recovers sufficiently for the declared half-life check. None of these values is a patient-specific symptom forecast.

### Long COVID

Long COVID is not represented as one uniform physiology. The autonomic configuration produces a 32.483 bpm orthostatic HR rise. The separate exertional/extraction configuration uses an extraction fraction of 0.49 versus the 0.78 healthy operating point, consistent with `CLM-LC-EXTRACTION` and `REF-SINGH-2022`; it is not required to show POTS-like tachycardia. The ME/CFS 0.74 subgroup anchor is not substituted for this Long COVID value. Respiratory, endothelial/microvascular, immune, sleep, and other mechanisms remain unimplemented or hypothesis-grade.

### Cross-disease interpretation

Shared equations provide comparability of computational constructs, not evidence that diseases share one cause or severity scale. The cross-disease demonstration is a qualitative scenario comparison, not a disease ranking, prevalence model, or differential-diagnosis tool.

## C. Architecture

The implementation is divided into five concerns:

1. **Scientific source layer:** references, claims, reviews, limitations, and evidence grades.
2. **Mechanism specification layer:** mechanisms, equations, parameters, maturity, and implementation links.
3. **Executable numerical layer:** `ComputationalPatient`, `ModelParameters`, protocol segments, DOP853 integration, and deterministic outputs.
4. **Semantic interoperability layer:** the OCPE disease package, adapter, quantity/unit declarations, and validated observation records.
5. **Validation and reproducibility layer:** seven test layers, fixtures, sensitivity analyses, demonstrations, audits, CI, and commit-specific reports.

The cardiovascular states are arterial, central-venous, and peripheral-venous stressed volumes plus sympathetic state. Additional states represent exertional load, delayed stress, PEM severity, and cerebral-flow index. The compartment equations telescope exactly:

`dVa/dt + dVc/dt + dVp/dt = 0`.

The observation mapper adapts the simulator-native `cardiac_output_l_min` name to the OCPE cardiac-output quantity without a second unit conversion. No numerical disease solver was added to upstream OCPE.

## D. Implementation and reproducible outputs

The main entry points are:

- `scripts/simulate.py` for one configured run.
- `scripts/run_examples.py` for all six demonstrations.
- `scripts/run_sensitivity.py` for 14 local and 18 deterministic grid scenarios.
- `scripts/run_validation.py` for independent seven-layer reporting.
- `scripts/audit_traceability.py` for strict registry/provenance auditing.

Each persisted simulation includes parameters, protocol segments, summary metrics, a configuration SHA-256, Python/NumPy/SciPy versions, the OCPE commit, and solver method, sampling interval, maximum step, relative/absolute tolerances, and seed. Compact NPZ traces, JSON results, validated observations, and PNG figures are included only for curated demonstrations and analyses.

`validation/reproducibility.json` records dependency versions, execution commands, validation results, artifact hashes, and all 16 persisted demonstration runs. Its `repository_commit` is the last tested source/configuration commit, not a claim that the later release-record commit was tested before it existed. The release-record commit adds only the executed reports, regenerated curated outputs, manifest, registry results, and handoff; any later source/configuration change requires a new validation cycle. The seed does not introduce stochastic variability. No large patient cohort, machine-learning time-series dataset, or synthetic wearable dataset is generated.

## E. Validation results

Validated source: `e87401ddd435d2fd1d5e15420308086051229851`.

| Layer | Independent result | Scope |
|---|---:|---|
| Software | 104 passed | Configuration, serialization, OCPE adapter/mapping, regression, and dual-marked registry integrity |
| Mathematical | 22 passed | Conservation, bounded/finite states, and solver convergence |
| Physiological | 16 passed | Resting operating point, orthostatic direction, pressure compensation, and recovery |
| Disease phenotype | 35 passed | POTS variants, hEDS exploration, PEM timing/recovery, and Long COVID heterogeneity |
| Empirical | 9 passed | Literature-linked group-level plausibility anchors |
| Sensitivity/uncertainty | 11 passed | Deterministic derivatives, grids, directionality, and configuration hashes |
| Scientific traceability | 39 passed | Schemas, registry resolution, complete scientific chains, parameter/default/override consistency, reports, and scope guards |

The full suite contains 231 unique tests; dual-marked tests explain why the independently selected layer counts sum to more than 231. Empty required selections fail by design. Strict traceability passed with zero errors and warnings, and strict OCPE validation passed with zero errors and warnings.

The final calibration changes are preserved in `validation/fixtures/regression_fixtures.json` with a dated change record. Earlier failures—29.33 bpm hyperadrenergic rise, excessive first-hour PEM, and the stale 0.74 Long COVID test criterion—were resolved by correcting the configuration/test inconsistency, not by weakening the declared criteria.

## F. Scientific confidence and maturity

Evidence grades E0–E5 and maturity levels M0–M4 are independent. Execution alone cannot establish M3, and M3/M4 cannot establish clinical validity.

- Shared hemodynamic, autonomic, pooling, cerebral-flow, capacity, extraction, and PEM mechanisms have executed their declared mathematical/physiological checks and are registered M3 where applicable.
- The hEDS venous-compliance configuration remains M2 because its magnitude is assumed and its sensitivity grid contains failed physiological regimes.
- RAAS, connective-tissue causal links, microvascular/endothelial, respiratory, inflammatory/neuroimmune, sleep/circadian, GI, and pain-autonomic mechanisms remain M0/M1 or otherwise unimplemented as registered.
- No integrated disease model is assigned M4. Current empirical comparisons use heterogeneous group-level anchors, broad plausibility bands, calibration overlap, and normalized constructs rather than independent patient-level external validation.

Confidence is strongest in software integrity, exact volume conservation, deterministic reproducibility, and explicit provenance. It is weaker in absolute parameter identification, structural uncertainty, disease heterogeneity, and generalization beyond the demonstrated scenarios.

## G. Stage 2 readiness

Stage 2 synthetic wearable dataset generation is explicitly excluded and was not implemented.

Available foundations are limited to stable simulation protocols, small deterministic traces, seven final-time observation mappings, explicit UCUM units, configuration hashes, and strict OCPE validation. Missing prerequisites include raw ECG/PPG/HRV/respiratory/temperature/electrodermal/accelerometry channels, sampling and aliasing models, motion artifacts, sensor bias/drift/dropout, device-specific error models, reference measurements, cohort governance, and agreement analyses such as ICC/CCC or Bland–Altman limits.

Accordingly, the repository is **not ready to generate clinically meaningful synthetic wearable datasets**. It can provide compact computational inputs to a separately governed sensor-modeling effort, but no wearable realism or agreement claim is supported.

## H. Stage 3 compatibility

Stage 3 flare prediction is also excluded. No forecasting model, symptom label, TSFM, machine-learning dataset, patient-facing prediction, or treatment recommendation is supplied.

The longitudinal protocols and normalized states may serve as research inputs after an independent protocol defines outcomes, labels, missingness, cohort governance, validation splits, calibration, and clinical utility. Deterministic parameter grids are not training cohorts and have no prevalence or probability interpretation. Compatibility of file formats must not be confused with readiness for flare prediction.

## I. Validation migration

The migration documents are:

- `docs/validation/legacy-validation-audit.md`
- `docs/validation/validation-migration-plan.md`
- `docs/validation/validation-architecture.md`
- `docs/validation/validation-runbook.md`

The migration matrix maps semantic/schema validation, physiological bounds, conservation, orthostatic criteria, regression, CI, fixtures, review sidecars, sensor agreement, virtual cohorts, and archived telemetry to explicit adaptation, reimplementation, deferral, retirement, or non-migration decisions.

Historical reproduction is preserved rather than rewritten: parent `c0d8678` reported 75 passed and two strict xfailed; authoritative `64ef9e2` reported 45 passed with strict package/dependency checks; pinned current OCPE reported 121 passed. The archived numerical tests at the refactor commit retain their path-related failures. Legacy strict expected failures included a neuropathic sustained HR rise of about 21 bpm with flat dose response and failure to reproduce upright systolic-pressure criteria despite a MAP pressor response. The legacy healthy HR rise of 76.1 bpm and absent skeletal-muscle-pump limitation remain documented.

The new system does not claim source-level solver compatibility, wearable agreement, virtual-cohort migration, or clinical validation. Current local seven-layer results permit legacy numerical results to serve as historical comparators rather than evidence for the new model.

## J. Traceability

The implemented chain is:

`reference → evidence claim → mechanism → equation → parameter → implementation → validation test → simulation output`.

Every implemented mechanism now has evidence, equation, parameter, implementation, and validation links. Validation records associated with mechanisms expose their evidence/equation/parameter links, and regression tests guard those requirements. Stable schemas and identifier resolution cover references, claims, mechanisms, equations, parameters, validations, and simulations.

The canonical reports are `validation/traceability/audit/traceability_report.json` and `.md`. Strict mode fails on errors or warnings. The final audit reports zero errors, warnings, and infos. This establishes record integrity, not the truth of a mechanism or the clinical validity of an output.

## K. Validation-system assessment

The validation system is suitable for a small, auditable research framework because it separates software execution, mathematics, physiology, disease scenarios, empirical plausibility, sensitivity, and provenance. It preserves failed parameter regimes, rejects empty required test selections, and records exact configurations and source revisions.

Its principal weaknesses are scientific rather than cosmetic:

- Many parameters are assumed or calibrated operating points, not independently identified measurements.
- Group-level empirical anchors are heterogeneous and overlap with calibration; they are not prospective external validation.
- Local perturbations and two-parameter grids do not quantify structural uncertainty, correlations, global identifiability, or population variability.
- The reduced-order cardiovascular, cerebral, extraction, and PEM constructs omit major physiological processes.
- Source-checkout configuration discovery limits wheel portability.
- Local Python 3.12 execution does not prove the configured remote Python 3.11/3.12 matrix passes.

The system therefore supports reproducible computational scrutiny, not diagnosis, prognosis, treatment selection, disease-severity ranking, or patient-specific inference.

## L. Scientific change management and operational handoff

Scientific changes follow `docs/scientific-change-management.md`. Equation, parameter, evidence, phenotype, fixture, and maturity changes require linked provenance and appropriate independent review. Regression fixtures are regenerated rather than hand-edited to conceal drift, with change records explaining mechanism, evidence, and expected direction. Rollback uses reviewed Git reverts rather than destructive history changes. Failed tests and unresolved limitations may not be deleted to obtain a green release.

The branch contains logical commits for the executable framework, literature, governance/CI, curated artifacts, and solver metadata. The release-record commit adds executed validation results, the reproducibility manifest, and this handoff. `docs/reproducibility.md` and `docs/validation/validation-runbook.md` are the operational entry points.

Security and publication notes:

- Upstream OCPE remains at the pinned commit with a clean working tree.
- No PAT, token, credential, private key, or temporary secret was committed.
- CI uses read-only contents permission, disables persisted checkout credentials, and requires no secrets.
- No remote push is claimed. Push only through an explicitly authorized secure operation.
- Any temporary PAT previously pasted into chat should be revoked or rotated; chat exposure should not be treated as secure storage.

Remaining priorities are independent empirical benchmarking, resolution or rejection of fragile hEDS regimes, richer structural validation, package-data portability, and verified remote CI. Stage 2 sensor modeling and Stage 3 prediction require separate approved projects and must not be inferred from this release.
