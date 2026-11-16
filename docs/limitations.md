# Scientific and engineering limitations

This file is part of the model interface. Removing or downplaying these limitations changes the scientific meaning of the outputs.

## Model structure

- The cardiovascular model is deterministic, beat-averaged, and reduced to four linear-compliance stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous). It has no pulsatile ventricle, dynamic unstressed-volume reservoir, heart chambers, regional denervation state, microcirculation, or venous valves. The pressure-gradient floors are ideal-valve approximations, and central venous stressed volume remains a reduced-order preload proxy, not ventricular end-diastolic volume.
- Regional gravity pressure offsets lump posture effects per compartment. They are not an angle-specific hydrostatic model, measured splanchnic pooling fluxes, or arterial-side hydrostatic columns; only the shared head-level baroreflex/cerebral correction `G_head` approximates heart-to-head hydrostatics.
- The skeletal-muscle pump is an explicit computational assumption (frequency, pumped volume, effectiveness, volume half-saturation), not an identified human pump law. The sustained-contraction impediment gain is assumed. Rhythmic activity, sustained contraction, and metabolic exertion are independent inputs; their magnitudes are scenario declarations, not measurements.
- The baroreflex uses a sigmoidal head-level-pressure target with three first-order effector lags (cardiac sympathetic, vascular sympathetic, vagal). These lags are not pure neural transmission delays; catecholamine concentrations, MSNA, afferent/efferent lesion location, and 0.1 Hz oscillations are not represented. The cardiac-sympathetic/vagal chronotropic gain split is unidentified at fixed total gain—the fixed-total split scenarios change peak but not sustained HR rise—and the default equal split is a calibration choice. Baroreflex findings differ across POTS and JHS/EDS-HT cohorts; no universal gain reduction is justified.
- The cerebral-flow index is a normalized proxy driven by cerebral perfusion pressure (arterial pressure minus the heart–brain offset and central venous back pressure) through a phenomenological bounded autoregulation curve. It is not measured CBF or MCA velocity, contains no CO2-dependent vasomotion, no intracranial-pressure state, and no vascular territories, so orthostatic hyperventilation effects cannot be inferred from it.
- The healthy end-tilt cerebral-flow-index reduction is approximately 0.003%, far below the reported approximately 7% control reduction and outside the broad 3–11% soft plausibility band used to disclose that comparison. In the same healthy tilt scenario, heart-level MAP rises by approximately 17.4 mmHg to 117.4 mmHg; pressure-driven autoregulation therefore nearly abolishes the control-side cerebral response. This is a retained warning-level negative result, not evidence that healthy controls have zero orthostatic cerebral-flow change. The ME/CFS 15–35% scenario-band assertion remains unchanged.
- The healthy early upright cardiac-output reduction is approximately 5.64%, **below** the broad 10–30% literature-derived soft plausibility band. This retained negative result indicates the reduced-order structure underrepresents the early orthostatic CO transient; it is reported as a warning and is not tuned away. The caudal stressed-volume accumulation of approximately 336.55 mL lies inside the broad 300–900 mL soft band.
- Nonnegative flow and bounded HR/extraction are numerical constitutive choices. They do not make every parameter regime physiological.
- No stochastic biological variability is implemented. The recorded seed does not create variability, and sensitivity grids have no probabilities.

## Disease representations

### POTS

- Phenotypes are calibrated computational scenarios, not natural-history or prevalence models. Neuropathic, hyperadrenergic, hypovolemic, and mixed mechanisms overlap in reality.
- The adult ≥30 bpm criterion is applied to the **sustained** HR rise (mean over the final 120 s of the upright window versus the supine baseline) as a scenario check, not as a diagnostic classifier; the peak rise is reported separately. Age, symptoms, duration, medication, and absence of orthostatic hypotension are not fully represented. The equal cardiac-sympathetic/vagal chronotropic gains in the POTS and Long COVID autonomic scenarios are post-migration scenario calibrations chosen to meet this sustained criterion, not literature measurements; threshold agreement is calibration overlap, not independent validation.
- The 0.92 stressed-volume factor is not a direct conversion of the reported plasma-volume deficit. RAAS and renal volume regulation are specified but not implemented.
- Hyperadrenergic gain is calibrated; no catecholamine state distinguishes primary from secondary hyperadrenergic physiology.

### EDS / hEDS

- The hEDS lower-limb venous compliance of 58.3333 mL/mmHg is an assumption (migrated from the original aggregated peripheral-compliance 140 mL/mmHg scenario, not volume-matched to healthy). Arterial elasticity or stiffness cannot identify venous capacitance, and mixed-EDS results cannot be generalized to every subtype.
- Historical JHS, EDS-HT, and EDS-III studies do not automatically represent current hEDS criteria. Referral, pain, medication, deconditioning, and autonomic confounding remain.
- The framework does not model vascular EDS fragility, arterial rupture, joint instability, pain-autonomic coupling, GI dysmotility, mast-cell biology, or a direct connective-tissue wearable signal.
- **No scenario in the current hEDS compliance × gravity sensitivity grid ends below the 70 mmHg MAP screening threshold** (current grid range approximately 115–117.7 mmHg). The pre-revision aggregated-peripheral grid did contain three below-70-mmHg failures, with a minimum of approximately 37.84 mmHg; those failed physiological regimes are preserved unchanged as historical results in `validation/baseline/stage0/`, `docs/stage1/baseline-scientific-report.md`, and the legacy audit. They were not tuned away or deleted, and they are not evidence about the revised grid. The assumed venous-compliance mechanism remains hypothesis-sensitive and M2.

### ME/CFS

- PEM dynamics are phenomenological. Delayed stress and PEM severity are not identified molecular, inflammatory, mitochondrial, or symptom-score states. In the repeated-exertion scenario, normalized PEM first exceeds 0.05 approximately 5.7 hours after the day-1 bout ends, earlier than the commonly reported 12–48-hour onset window after daily activity, although post-CPET reports of onset within 24 hours include this timing and the approximately 39.2-hour post-bout peak remains compatible with the cited delayed-peak evidence. The threshold crossing is therefore a scenario-timing limitation, not a claim that one universal PEM onset constant fits all provocations.
- The threshold/gain are calibrated and can saturate PEM target at one. Severe, bedbound, pediatric, and CPET-ineligible populations are underrepresented.
- Repeated-CPET effect sizes vary and include conflicting replications. Normalized functional capacity is not a direct day-2 VO2 measurement.
- Cerebral flow lacks CO2, vessel diameter, autoregulatory territories, and a direct Doppler observation model. Selected extracranial Doppler cohorts constrain direction and broad magnitude only.
- Preload failure and impaired extraction in selected invasive-CPET cohorts are not universal ME/CFS mechanisms.

### Long COVID

- Autonomic, exertional/extraction, PEM, respiratory, endothelial/microvascular, immune, sleep, and fatigue-related presentations are heterogeneous. Two executable configurations do not cover this full space.
- The 0.49 oxygen-extraction value comes from a small selected study and is not a population estimate or proof of mitochondrial dysfunction.
- PEM timing constants are shared with the ME/CFS phenomenology and are not independently identified Long COVID dynamics.
- Respiratory limitation, ventilatory control, endothelial dysfunction, coagulation/microclots, inflammatory signaling, and circadian regulation remain unimplemented.

## Parameters and empirical evidence

- Most nominal values are computational operating points or calibration assumptions. Supported ranges are sensitivity ranges, not clinical intervals or probability distributions.
- Group means and selected-cohort measurements do not identify patient-level parameters. Calibration overlap means current empirical comparisons are not fully independent M4 benchmarks.
- No diagnostic accuracy, treatment response, prognosis, disease severity ranking, comparative effectiveness, or patient-specific prediction can be inferred.
- Contradictory evidence—such as higher rather than lower resting spectral BRS in one JHS/EDS-HT cohort—is retained in the reviews and prevents a universal baroreflex assumption.

## Validation and sensitivity

- Seven layers measure different properties. A pass in one does not compensate for a failure in another, and none establishes clinical validity.
- Regression fixtures protect reviewed numerical behavior, not scientific truth. Updating them requires an explained scientific change.
- Sensitivity is local/deterministic and does not establish global identifiability. Two-parameter grids do not quantify structural uncertainty, parameter correlations, or population variability.
- Reports must retain failed tests and nonphysiological scenarios. Missing required tests, references, fixtures, or empty pytest selections are failures.

## Observation and packaging

- Observations are sparse mapped values, not raw sensor signals. No ECG/PPG/HRV/respiratory/temperature/electrodermal/accelerometry synthesis or sensor-error model is implemented.
- PEM severity is normalized 0–1, not a clinical 0–10 self-report score. Cerebral flow and functional capacity are normalized constructs.
- Configuration and OCPE domain-package discovery assume a source checkout or explicit paths. Wheel-installed users must supply the repository/package root; portable package-data installation remains future work.
- Reproducibility depends on the exact OCPE commit and recorded dependency versions. A mutable branch or unpinned dependency is not equivalent.

## Explicit scope exclusions

No synthetic wearable dataset, large simulated patient cohort, machine-learning time-series dataset, TSFM, flare predictor, patient-facing application, diagnostic recommendation, or treatment recommendation is provided. Stage 2 and Stage 3 require separate scientific and engineering work.
