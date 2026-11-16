# Scientific and engineering limitations

This file is part of the model interface. Removing or downplaying these limitations changes the scientific meaning of the outputs.

## Model structure

- The cardiovascular model is deterministic, beat-averaged, and reduced to three stressed-volume compartments. It has no pulsatile ventricle, separate unstressed volume, heart chambers, skeletal-muscle pump, splanchnic compartment, regional denervation, microcirculation, or venous valves.
- A normalized gravity pressure offset lumps posture effects. It is not an angle-specific hydrostatic model or measured splanchnic pooling flux.
- The sigmoidal pressure feedback and single sympathetic state omit vagal dynamics, afferent/efferent lesion location, catecholamine concentrations, MSNA, and 0.1 Hz oscillations. Baroreflex findings differ across POTS and JHS/EDS-HT cohorts; no universal gain reduction is justified.
- Nonnegative flow and bounded HR/extraction are numerical constitutive choices. They do not make every parameter regime physiological.
- No stochastic biological variability is implemented. The recorded seed does not create variability, and sensitivity grids have no probabilities.

## Disease representations

### POTS

- Phenotypes are calibrated computational scenarios, not natural-history or prevalence models. Neuropathic, hyperadrenergic, hypovolemic, and mixed mechanisms overlap in reality.
- The adult ≥30 bpm criterion is used as a scenario check, not as a diagnostic classifier. Age, symptoms, duration, medication, and absence of orthostatic hypotension are not fully represented.
- The 0.92 stressed-volume factor is not a direct conversion of the reported plasma-volume deficit. RAAS and renal volume regulation are specified but not implemented.
- Hyperadrenergic gain is calibrated; no catecholamine state distinguishes primary from secondary hyperadrenergic physiology.

### EDS / hEDS

- Peripheral venous compliance 140 mL/mmHg is an assumption. Arterial elasticity or stiffness cannot identify venous capacitance, and mixed-EDS results cannot be generalized to every subtype.
- Historical JHS, EDS-HT, and EDS-III studies do not automatically represent current hEDS criteria. Referral, pain, medication, deconditioning, and autonomic confounding remain.
- The framework does not model vascular EDS fragility, arterial rupture, joint instability, pain-autonomic coupling, GI dysmotility, mast-cell biology, or a direct connective-tissue wearable signal.
- Deterministic hEDS sensitivity grids include combinations with final MAP below 70 mmHg (minimum approximately 37.84 mmHg in the declared grid). Those are failed physiological regimes, not valid hEDS phenotypes. They demonstrate model/parameter fragility and prevent a robust quantitative clinical interpretation.

### ME/CFS

- PEM dynamics are phenomenological. Delayed stress and PEM severity are not identified molecular, inflammatory, mitochondrial, or symptom-score states.
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
