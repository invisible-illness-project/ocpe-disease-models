# Scientific and engineering limitations

This file is part of the model interface. Removing or downplaying these limitations changes the scientific meaning of the outputs.

The current implementation is the Stage 1.1 revision (model version 0.3.0, five stressed-volume compartments, twelve states); see `docs/stage1-1/` for the design record, decision log, validation matrix, and readiness assessment. A deterministic 0.3.0 scientific scenario comparison matrix has been executed (`validation/stage1-1/scientific-comparison-matrix.md`); its results, including negative ones, are reflected below. Release validation (full test suite, strict traceability, strict OCPE package validation, fixtures) is executed at tested commit `942713ef720ad0e801e71bf9bc78405cd844a739` — 327 passed, 1 skipped, 6 xfailed, 2 warnings in 341.60s; all seven layer execution statuses PASS; the overall seven-layer scientific status is **FAIL** from the preserved strict phenotype xfails. Values attributed to Stage 1 (0.2.0) are preserved history.

## Model structure

- The cardiovascular model is deterministic, beat-averaged, and reduced to five linear-compliance stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous, and one lumped residual other-systemic venous compartment). It has no pulsatile ventricle, dynamic unstressed-volume reservoir, heart chambers, regional denervation state, microcirculation, or venous valves. The pressure-gradient floors are ideal-valve approximations, and central venous stressed volume remains a reduced-order preload proxy, not ventricular end-diastolic volume. The single other-systemic compartment lumps all remaining venous volume with a 0 cm hydrostatic height; the 25/25/50 baseline flow partition and 2550 mL total stressed volume are operating-point choices, not anatomy.
- Regional hydrostatic terms are lumped per-compartment heights (cm) converted at 0.7356 mmHg/cm and scaled by sin(tilt angle). They are not measured regional pooling fluxes or arterial-side hydrostatic columns; the transition interpolation is linear in angle only; and the legacy `upright` fraction survives only through the `arcsin` migration mapping.
- The skeletal-muscle pump is an explicit computational assumption (frequency, pumped volume, effectiveness, volume half-saturation), not an identified human pump law. The sustained-contraction impediment gain is assumed. Rhythmic activity, sustained contraction, and metabolic exertion are independent inputs; their magnitudes are scenario declarations, not measurements. The active-standing protocol's ten seconds of low-level muscle activity is a protocol assumption, not a calibrated gait model.
- The baroreflex uses a sigmoidal target driven by an integrated weighted error from separate aortic and carotid sensors with three first-order effector lags (cardiac sympathetic, vascular sympathetic, vagal). The aortic/carotid weights (default 0.25/0.75), sensor heights (default 0/25 cm), and independent setpoints/scales are computational assumptions, not measured afferent contributions. These lags are not pure neural transmission delays; catecholamine concentrations, MSNA, afferent/efferent lesion location, and 0.1 Hz oscillations are not represented. The cardiac-sympathetic/vagal chronotropic gain split is unidentified at fixed total gain—the fixed-total split scenarios change peak but not sustained HR rise—and the default equal split is a calibration choice. Baroreflex findings differ across POTS and JHS/EDS-HT cohorts; no universal gain reduction is justified.
- The cerebral-flow index is a normalized research proxy driven by cerebral perfusion pressure (brain-level arterial pressure minus a fixed effective cerebral outflow pressure of 5 mmHg) through a phenomenological bounded autoregulation curve. The 5 mmHg value is explicitly neither thoracic central venous pressure nor a resolved intracranial pressure, and no ICP state exists. The index is not measured CBF or MCA velocity and has no vascular territories.
- CO2 enters only through a declared per-segment end-tidal CO2 value acting as exp(0.035 × clip(ETCO2 − 40 mmHg, ±15 mmHg)) on the cerebral target. End-tidal CO2 is an approximate surrogate and is not exact PaCO2; no end-tidal-to-arterial correction is modeled; posture never infers hypocapnia; and the ±15 mmHg clip bounds extrapolation beyond the supported range. Orthostatic hyperventilation effects therefore exist in a run only when a protocol declares them.
- The healthy end-tilt cerebral-flow-index reduction is approximately 0.003% in the Stage 1 (0.2.0) record, far below the reported approximately 7% control reduction and outside the broad 3–11% soft plausibility band used to disclose that comparison. In the executed 0.3.0 scenario matrix the reduction is **1.645%** at 70 degrees (0.819/1.192/1.497% at 30/45/60 degrees)—**the miss persists, narrowed, and remains below the unchanged 3–11% disclosure band**. This is a retained negative result, not evidence that healthy controls have negligible orthostatic cerebral-flow change. The ME/CFS 15–35% scenario-band assertion remains unchanged, and the 0.3.0 ME/CFS reduction of 22.913% lies within it.
- The healthy orthostatic cardiac-output underresponse persists at 0.3.0: sustained CO change is **−3.105%** and SV change **−12.733%** at 70 degrees, and **all eight Zaidi (REF-ZAIDI-2000) 60/70-degree 2/5-minute CO/SV comparisons MISS** the published ranges newly predeclared for Stage 1.1 (model CO −2.571/−3.105% vs −20 to −17%; model SV −11.375/−12.733% vs −34 to −28%). The Stage 1 record (~5.64% early CO reduction vs the broad 10–30% soft band; caudal accumulation ~336.55 mL within the 300–900 mL band) is preserved history. This indicates the reduced-order structure underrepresents the orthostatic CO/SV reduction; it is reported, not tuned away.
- At 70 degrees the healthy heart-level MAP rises to approximately **111.33 mmHg** from the 100 mmHg supine operating point. This pressor response is a structural consequence of the integrated carotid-weighted baroreflex and is not established as a quantitatively validated healthy tilt response; it is disclosed alongside the CO/SV and CFI misses rather than treated as evidence of physiological validity.
- Nonnegative flow and bounded HR/extraction are numerical constitutive choices. They do not make every parameter regime physiological.
- No stochastic biological variability is implemented. The recorded seed does not create variability, and sensitivity grids have no probabilities.

## Disease representations

### POTS

- Phenotypes are calibrated computational scenarios, not natural-history or prevalence models. Neuropathic, hyperadrenergic, hypovolemic, and mixed mechanisms overlap in reality.
- The adult ≥30 bpm criterion is applied to the **sustained** HR rise (mean over the final 120 s of the upright window versus the supine baseline) as a scenario check, not as a diagnostic classifier; the peak rise is reported separately. Age, symptoms, duration, medication, and absence of orthostatic hypotension are not fully represented. The equal cardiac-sympathetic/vagal chronotropic gains in the POTS and Long COVID autonomic scenarios are post-migration scenario calibrations chosen to meet this sustained criterion, not literature measurements; threshold agreement is calibration overlap, not independent validation. **At 0.3.0 all four POTS phenotypes FAIL the unchanged ≥30 bpm sustained criterion** (neuropathic 17.428, hyperadrenergic 19.659, hypovolemic 19.399, mixed 19.216 bpm), as does Long-COVID-autonomic (18.931 bpm): the dual-sensor integrated baroreflex and resistance re-partition materially reduced sustained chronotropic compensation relative to the 0.2.0 calibrated scenarios. This failure is preserved as a negative result; the criterion was not widened and the gains were not recalibrated.
- The 0.92 stressed-volume factor is not a direct conversion of the reported plasma-volume deficit. RAAS and renal volume regulation are specified but not implemented.
- Hyperadrenergic gain is calibrated; no catecholamine state distinguishes primary from secondary hyperadrenergic physiology.

### EDS / hEDS

- The hEDS lower-limb venous compliance of 58.3333 mL/mmHg is an assumption (migrated from the original aggregated peripheral-compliance 140 mL/mmHg scenario, not volume-matched to healthy). Arterial elasticity or stiffness cannot identify venous capacitance, and mixed-EDS results cannot be generalized to every subtype.
- Historical JHS, EDS-HT, and EDS-III studies do not automatically represent current hEDS criteria. Referral, pain, medication, deconditioning, and autonomic confounding remain.
- The framework does not model vascular EDS fragility, arterial rupture, joint instability, pain-autonomic coupling, GI dysmotility, mast-cell biology, or a direct connective-tissue wearable signal.
- **No scenario in the current hEDS compliance × lower-limb-hydrostatic-height sensitivity grid ends below the 70 mmHg MAP screening threshold** (current grid range approximately 110.67–111.52 mmHg). The pre-revision aggregated-peripheral grid did contain three below-70-mmHg failures, with a minimum of approximately 37.84 mmHg; those failed physiological regimes are preserved unchanged as historical results in `validation/baseline/stage0/`, `docs/stage1/baseline-scientific-report.md`, and the legacy audit. They were not tuned away or deleted, and they are not evidence about the revised grid. The assumed venous-compliance mechanism remains hypothesis-sensitive and M2.

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
- Group means and selected-cohort measurements do not identify patient-level parameters. Calibration overlap means current empirical comparisons are not fully independent M4 benchmarks.
- No diagnostic accuracy, treatment response, prognosis, disease severity ranking, comparative effectiveness, or patient-specific prediction can be inferred.
- Contradictory evidence—such as higher rather than lower resting spectral BRS in one JHS/EDS-HT cohort—is retained in the reviews and prevents a universal baroreflex assumption.

## Validation and sensitivity

- Seven layers measure different properties. A pass in one does not compensate for a failure in another, and none establishes clinical validity.
- The Stage 1.1 (0.3.0) scientific scenario comparison matrix and the full release validation cycle (full test suite, strict traceability audit, strict OCPE package validation, regression-fixture regeneration, sensitivity export, demonstrations) have been executed at tested commit `942713ef720ad0e801e71bf9bc78405cd844a739`; the results (including the Zaidi CO/SV MISSes and the POTS sustained-HR criterion FAILs) are reported in `docs/stage1-1/validation-matrix.md` and `validation/reports/validation-report.json`. The overall seven-layer scientific status is FAIL because the six strict phenotype xfails are preserved scientific failures; no negative result is converted into a pass, and execution does not resolve the scientific misses listed above.
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
