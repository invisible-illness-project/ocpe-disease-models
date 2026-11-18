# Scientific and engineering limitations

This file is part of the model interface. Removing or downplaying these limitations changes the scientific meaning of the outputs.

The current implementation retains the Stage 1.1 architecture with Stage 1.2 scientific remediation (model version 0.3.0, five stressed-volume compartments, twelve states). Stage 1.1 design and validation records remain preserved under `docs/stage1-1/` and `validation/stage1-1/`; the current root-cause analysis and exact before/after evidence are under `docs/stage1-2/` and `validation/stage1-2/`. The Stage 1.2 suite completed with 343 passed and one environment-dependent skip, no scientific expected failures, clean strict traceability, and zero strict OCPE errors or warnings. These execution results do not override the separately reported empirical misses below. Values attributed to Stage 1 or Stage 1.1 are preserved history.

## Model structure

- The cardiovascular model is deterministic, beat-averaged, and reduced to five linear-compliance stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous, and one lumped residual other-systemic venous compartment). It has no pulsatile ventricle, dynamic unstressed-volume reservoir, heart chambers, regional denervation state, microcirculation, or venous valves. The pressure-gradient floors are ideal-valve approximations, and central venous stressed volume remains a reduced-order preload proxy, not ventricular end-diastolic volume. The single other-systemic compartment lumps all remaining venous volume; Stage 1.2 assigns it an effective 11 cm dependent height rather than Stage 1.1's preload-preserving 0 cm. The 25/25/50 baseline flow partition, 2550 mL total stressed volume, and all regional heights are operating-point/calibration choices, not anatomy.
- Regional hydrostatic terms are lumped per-compartment heights (cm) converted at 0.7356 mmHg/cm and scaled by sin(tilt angle). They are not measured regional pooling fluxes or arterial-side hydrostatic columns; the transition interpolation is linear in angle only; and the legacy `upright` fraction survives only through the `arcsin` migration mapping.
- The skeletal-muscle pump is an explicit computational assumption (frequency, pumped volume, effectiveness, volume half-saturation), not an identified human pump law. The sustained-contraction impediment gain is assumed. Rhythmic activity, sustained contraction, and metabolic exertion are independent inputs; their magnitudes are scenario declarations, not measurements. The active-standing protocol's ten seconds of low-level muscle activity is a protocol assumption, not a calibrated gait model.
- The baroreflex uses a sigmoidal target driven by an integrated weighted error from separate aortic and carotid sensors with three first-order effector lags (cardiac sympathetic, vascular sympathetic, vagal). The aortic/carotid weights (default 0.25/0.75), sensor heights (default 0/25 cm), and independent setpoints/scales are computational assumptions, not measured afferent contributions. These lags are not pure neural transmission delays; catecholamine concentrations, MSNA, afferent/efferent lesion location, and 0.1 Hz oscillations are not represented. The cardiac-sympathetic/vagal chronotropic gain split is unidentified at fixed total gain—the fixed-total split scenarios change peak but not sustained HR rise—and the default equal split is a calibration choice. Baroreflex findings differ across POTS and JHS/EDS-HT cohorts; no universal gain reduction is justified.
- The cerebral-flow index is a normalized research proxy driven by cerebral perfusion pressure (brain-level arterial pressure minus a fixed effective cerebral outflow pressure of 5 mmHg) through a phenomenological bounded autoregulation curve. The 5 mmHg value is explicitly neither thoracic central venous pressure nor a resolved intracranial pressure, and no ICP state exists. The index is not measured CBF or MCA velocity and has no vascular territories.
- CO2 enters only through a declared per-segment end-tidal CO2 value acting as exp(0.035 × clip(ETCO2 − 40 mmHg, ±15 mmHg)) on the cerebral target. End-tidal CO2 is an approximate surrogate and is not exact PaCO2; no end-tidal-to-arterial correction is modeled; posture never infers hypocapnia; and the ±15 mmHg clip bounds extrapolation beyond the supported range. Orthostatic hyperventilation effects therefore exist in a run only when a protocol declares them.
- The healthy end-tilt cerebral-flow-index reduction is approximately 0.003% in the Stage 1 (0.2.0) record and 1.645% in Stage 1.1, both below the broad 3–11% soft plausibility band. Stage 1.2 produces **4.407%** at 70 degrees, within that band, after revising pressure/loading behavior and setting the cerebral autoregulation residual slope to 0.4 within its existing range. This is calibration agreement, not independent validation of cerebral autoregulation. The ME/CFS 15–35% scenario-band assertion remains unchanged, and the Stage 1.2 ME/CFS reduction of **24.652%** lies within it.
- Stage 1.1 underrepresented orthostatic CO/SV reduction: all eight Zaidi (REF-ZAIDI-2000) 60/70-degree two/five-minute comparisons missed. Stage 1.2 improves healthy early minimum CO reduction from **0.346% to 14.570%**, and **six of eight** preserved Zaidi comparisons now pass. The two residual misses are both 60° CO reductions: **15.801%** at two minutes and **15.800%** at five minutes versus the unchanged **17–20%** band. The corresponding 60° SV comparisons and all four 70° CO/SV comparisons pass. This remains incomplete graded-tilt agreement; the bands were not widened.
- At 70 degrees the healthy heart-level MAP still rises from the 100 mmHg supine operating point to **108.85 mmHg** (Stage 1.1: 111.33 mmHg). This pressor response remains a structural consequence of the integrated carotid-weighted baroreflex and reduced-order vascular compensation. It is not established as a quantitatively validated healthy tilt response and remains a limitation despite the improved CO/SV and CFI behavior.
- Nonnegative flow and bounded HR/extraction are numerical constitutive choices. They do not make every parameter regime physiological.
- No stochastic biological variability is implemented. The recorded seed does not create variability, and sensitivity grids have no probabilities.

## Disease representations

### POTS

- Phenotypes are calibrated computational scenarios, not natural-history or prevalence models. Neuropathic, hyperadrenergic, hypovolemic, and mixed mechanisms overlap in reality.
- The adult ≥30 bpm criterion is applied to the **sustained** HR rise (mean over the final 120 s of the upright window versus the supine baseline) as a scenario check, not as a diagnostic classifier; the peak rise is reported separately. Age, symptoms, duration, medication, and absence of orthostatic hypotension are not fully represented. The equal cardiac-sympathetic/vagal chronotropic gains in the POTS and Long COVID autonomic scenarios are scenario calibrations, not literature measurements; threshold agreement is calibration overlap, not independent validation. Stage 1.1 produced sustained rises of only 17.428, 19.659, 19.399, 19.216, and 18.931 bpm for neuropathic, hyperadrenergic, hypovolemic, mixed, and Long-COVID-autonomic respectively. Stage 1.2 corrects the shared preload/pressure-feedback defect **without changing those gains**, yielding **36.724, 43.175, 41.793, 41.686, and 32.575 bpm**; all five now pass the unchanged scenario criterion and retain MAP above 70 mmHg. This agreement does not establish diagnostic accuracy or patient-specific phenotype validity.
- The 0.92 stressed-volume factor is not a direct conversion of the reported plasma-volume deficit. RAAS and renal volume regulation are specified but not implemented.
- Hyperadrenergic gain is calibrated; no catecholamine state distinguishes primary from secondary hyperadrenergic physiology.

### EDS / hEDS

- The hEDS lower-limb venous compliance of 58.3333 mL/mmHg is an assumption (migrated from the original aggregated peripheral-compliance 140 mL/mmHg scenario, not volume-matched to healthy). Arterial elasticity or stiffness cannot identify venous capacitance, and mixed-EDS results cannot be generalized to every subtype.
- Historical JHS, EDS-HT, and EDS-III studies do not automatically represent current hEDS criteria. Referral, pain, medication, deconditioning, and autonomic confounding remain.
- The framework does not model vascular EDS fragility, arterial rupture, joint instability, pain-autonomic coupling, GI dysmotility, mast-cell biology, or a direct connective-tissue wearable signal.
- **No scenario in the Stage 1.2 hEDS compliance × lower-limb-hydrostatic-height sensitivity grid ends below the 70 mmHg MAP screening threshold** (current grid range approximately 108.24–110.50 mmHg). The pre-revision aggregated-peripheral grid did contain three below-70-mmHg failures, with a minimum of approximately 37.84 mmHg; those failed physiological regimes are preserved unchanged as historical results in `validation/baseline/stage0/`, `docs/stage1/baseline-scientific-report.md`, and the legacy audit. They were not tuned away or deleted, and they are not evidence about the revised grid. The assumed venous-compliance mechanism remains hypothesis-sensitive and M2.

### ME/CFS

- PEM dynamics are phenomenological. Delayed stress and PEM severity are not identified molecular, inflammatory, mitochondrial, or symptom-score states. In the repeated-exertion scenario, normalized PEM first exceeds 0.05 approximately 5.7 hours after the day-1 bout ends, earlier than the commonly reported 12–48-hour onset window after daily activity, although post-CPET reports of onset within 24 hours include this timing and the approximately 39.2-hour post-bout peak remains compatible with the cited delayed-peak evidence. The threshold crossing is therefore a scenario-timing limitation, not a claim that one universal PEM onset constant fits all provocations.
- The threshold/gain are calibrated and can saturate PEM target at one. Severe, bedbound, pediatric, and CPET-ineligible populations are underrepresented.
- Repeated-CPET effect sizes vary and include conflicting replications. Normalized functional capacity is not a direct day-2 VO2 measurement.
- Cerebral CO2 regulation uses only declared ETCO2 and a bounded multiplicative factor; it lacks an end-tidal-to-arterial correction, vessel diameter, autoregulatory territories, and a direct Doppler observation model. Selected extracranial Doppler cohorts constrain direction and broad magnitude only.
- Preload failure and impaired extraction in selected invasive-CPET cohorts are not universal ME/CFS mechanisms.

### Long COVID

- Autonomic, exertional/extraction, PEM, respiratory, endothelial/microvascular, immune, sleep, and fatigue-related presentations are heterogeneous. Two executable configurations do not cover this full space.
- The 0.49 oxygen-extraction value comes from a small selected study and is not a population estimate or proof of mitochondrial dysfunction.
- PEM timing constants are shared with the ME/CFS phenomenology and are not independently identified Long COVID dynamics.
- Respiratory limitation, ventilatory control, endothelial dysfunction, coagulation/microclots, inflammatory signaling, and circadian regulation remain unimplemented.
- The Long-COVID-exertional configuration does not alter the cardiovascular tilt pathway; its 70-degree tilt results are therefore numerically identical to healthy-reference. This is an expected scope boundary, not evidence that exertional Long COVID has normal orthostatic physiology.

## Parameters and empirical evidence

- Most nominal values are computational operating points or calibration assumptions. Supported ranges are sensitivity ranges, not clinical intervals or probability distributions.
- ME/CFS, hEDS, and Long-COVID-autonomic retain Stage 1.1 fixed-offset-derived splanchnic/lower-limb heights and were not recalibrated against Stage 1.2 healthy/POTS values. Their inherited ratios to healthy are not anatomical or disease-severity evidence.
- Group means and selected-cohort measurements do not identify patient-level parameters. Calibration overlap means current empirical comparisons are not fully independent M4 benchmarks.
- No diagnostic accuracy, treatment response, prognosis, disease severity ranking, comparative effectiveness, or patient-specific prediction can be inferred.
- Contradictory evidence—such as higher rather than lower resting spectral BRS in one JHS/EDS-HT cohort—is retained in the reviews and prevents a universal baroreflex assumption.

## Validation and sensitivity

- Seven layers measure different properties. A pass in one does not compensate for a failure in another, and none establishes clinical validity.
- The Stage 1.2 exact-base comparison, full test suite, strict traceability audit, strict OCPE package validation, regression-fixture regeneration, and sensitivity export were executed for this remediation. All declared test layers execute without the former Stage 1.1 scientific expected failures. The current scientific status remains **partial** because two Zaidi 60° CO comparisons still `MISS` and healthy MAP over-defence persists; see `docs/stage1-2/readiness-assessment.md`, `validation/stage1-2/scientific-comparison-matrix.md`, and `validation/reports/validation-report.json`. Historical Stage 1.1 failures remain available at their original paths and commits rather than being rewritten.
- Regression fixtures protect reviewed numerical behavior, not scientific truth. Updating them requires an explained scientific change.
- Sensitivity is local/deterministic and does not establish global identifiability. Two-parameter grids do not quantify structural uncertainty, parameter correlations, or population variability.
- Reports must retain failed tests and nonphysiological scenarios. Missing required tests, references, fixtures, or empty pytest selections are failures.

## Observation and packaging

- Observations are sparse mapped values, not raw sensor signals. No ECG/PPG/HRV/respiratory/temperature/electrodermal/accelerometry synthesis or sensor-error model is implemented.
- PEM severity is normalized 0–1, not a clinical 0–10 self-report score. Cerebral flow and functional capacity are normalized constructs.
- Configuration and OCPE domain-package discovery assume a source checkout or explicit paths. Wheel-installed users must supply the repository/package root; portable package-data installation remains future work.
- Reproducibility depends on the exact OCPE commit and recorded dependency versions. A mutable branch or unpinned dependency is not equivalent.

## Explicit scope exclusions

No synthetic wearable dataset, large simulated patient cohort, machine-learning time-series dataset, TSFM, flare predictor, patient-facing application, diagnostic recommendation, or treatment recommendation is provided. Stage 1.1 added none of these. Stage 2 and Stage 3 require separate scientific and engineering work.
