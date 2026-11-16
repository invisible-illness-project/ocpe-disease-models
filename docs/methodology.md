# Scientific and numerical methodology

## Evidence-to-model workflow

1. **Review each disease independently.** Primary clinical physiology, consensus documents, computational physiology, controlled studies, and reviews are distinguished. Historical JHS/EDS-HT/EDS-III terminology is retained when a cohort predates current hEDS criteria.
2. **Create a reference record.** Each source receives a stable `REF-` ID and bibliographic identifiers only when verified. `literature/bibliography.bib` is generated from the same registry.
3. **Extract bounded evidence claims.** `CLM-` records contain study type, population/sample where available, measured variables, findings, parameter implications, limitations, E0–E5 grade, and downstream links. Association is not promoted to causation.
4. **Specify a mechanism.** `MEC-` records distinguish mechanistic approximations, phenomenology, and hypotheses. Unimplemented mechanisms remain M0/M1 and cannot acquire numerical parameters merely by being plausible.
5. **Register equations and parameters.** Every `EQ-` record has states, units, assumptions, limits, implementation and validation. Every `PAR-` record has units, nominal/default and phenotype values, provenance class, scenario range, uncertainty, calibration requirement, and dependencies.
6. **Implement once.** Shared physiology is executed in one core; disease wrappers and YAML configurations supply mechanism-specific parameters rather than duplicate engines or output multipliers.
7. **Validate independently.** Software execution, equations, physiological direction, disease scenarios, empirical comparisons, sensitivity, and provenance have separate acceptance criteria and reports.
8. **Persist compact outputs.** Each registered simulation identifies configuration and model provenance; its result stores the exact resolved parameters and solver metadata.

## Parameter interpretation

The parameter registry uses these practical classes:

- `derived_from_published_group_measurements`: a group-level measurement anchors a scenario, such as oxygen extraction 0.49 versus 0.78 in selected Long COVID exertional participants and controls.
- `calibrated_or_assumed_requires_validation`: a value chosen to express a mechanism or temporal scenario, such as stressed-volume factor 0.92 or hEDS peripheral compliance 140 mL/mmHg.
- `assumed_computational_operating_point`: a healthy/reference numerical choice required to close the reduced-order equations.

Supported ranges are deterministic sensitivity/scenario ranges, **not** confidence intervals, reference ranges, priors, or population distributions. No value becomes patient-specific because it resembles a published group mean. Important compartment mismatches are explicit: plasma volume is not total stressed volume; arterial pulse-wave velocity is not venous compliance; a normalized cerebral index is not measured volumetric CBF; normalized functional capacity is not VO2.

## Phenotype construction

A phenotype YAML contains its ID, diseases, mechanism and evidence links, parameter overrides, maturity, classification, and limitations. `compose_phenotypes()` merges only non-conflicting values. A conflict instructs the researcher to define an explicit comorbidity configuration with its own evidence and joint calibration. The hEDS/ME/CFS comorbid YAML is such an explicit record; arbitrary silent stacking is not supported.

POTS configurations demonstrate that neuropathic, hyperadrenergic, and hypovolemic mechanisms can overlap. Long COVID autonomic and exertional records remain separate. hEDS venous compliance is an hEDS-only exploratory scenario and does not describe vascular EDS or all EDS subtypes.

## Protocols and boundary conditions

Protocols are piecewise-constant normalized inputs:

- `resting-baseline`: stable supine/resting operation.
- `head-up-tilt`: 120 s supine followed by 480 s upright.
- `tilt-recovery`: upright stress followed by supine recovery.
- `single-exertion-recovery`: baseline, a 20-minute normalized exertion bout, and 72-hour follow-up.
- `repeated-exertion-recovery`: two bouts separated by 24 hours and subsequent recovery.

Initial stressed volumes are scaled by `blood_volume_factor`; all later volume exchange is conservative. Sympathetic, exertion, delayed stress, and PEM start at their declared reference values. Flows are clamped to nonnegative values. HR and extraction are bounded for numerical and physiological safety. These clamps are modeling assumptions and can conceal regimes outside the intended operating domain; failed pressure regimes are reported rather than clipped into plausibility.

## Solver and numerical checks

DOP853 integrates the eight-state ODE system. Protocol YAML records output interval, maximum internal step, `rtol`, and `atol`. The mathematical layer checks:

- exact instantaneous volume-balance cancellation and tight simulated volume drift;
- finite states and outputs;
- convergence under tighter tolerances and smaller steps;
- stable resting behavior and meaningful response directionality.

Numerical convergence verifies approximation to the implemented equations. It says nothing about whether those equations represent a patient.

## Empirical comparisons

Empirical tests use predeclared broad scenario bands around published group-level observations:

- adult POTS HR-rise criterion, with MAP reported separately;
- delayed PEM timing rather than immediate fatigue;
- heterogeneous repeated-CPET capacity reductions;
- ME/CFS cerebral-flow group means and recovery limitations;
- selected invasive-CPET oxygen-extraction findings.

These are plausibility comparisons, not fitted individual data, held-out patient predictions, diagnostic sensitivity/specificity, or prospective external validation. Overlapping evidence used for calibration is not relabeled as independent validation.

## Sensitivity and uncertainty

Local one-at-a-time perturbations calculate centered output changes and normalized sensitivities where a nonzero baseline permits them. Two small full factorial grids examine interacting assumptions:

- hEDS peripheral compliance × gravity offset;
- ME/CFS delayed-stress constant × PEM onset constant.

Every row has a configuration SHA and is labeled a deterministic scenario with no probability. The analysis retains all outputs, including hEDS combinations that fail the MAP screening threshold. It does not perform patient-cohort simulation, Bayesian inference, global identifiability, or population uncertainty quantification.

## Observation mapping

`cardiac_output_l_min` is the simulator-native L/min output. The observation mapper explicitly aliases it to the OCPE cardiac-output quantity without a second unit conversion. Other mapped outputs include HR, MAP, stroke volume, cerebral index, metabolic capacity, and normalized PEM severity. Final-time demonstration observations are validated strictly with zero errors and warnings. No ECG/PPG waveform, HRV, respiratory, temperature, electrodermal, or accelerometry signal is synthesized.

## Reproducibility and change control

Run `scripts/run_examples.py`, `scripts/run_sensitivity.py`, and `scripts/run_validation.py` from a clean source checkout. Preserve configuration hashes, exact OCPE commit, dependency versions, fixture version, and validation reports. Equation, evidence, parameter, phenotype, or fixture changes require impact analysis across linked records; see `docs/scientific-change-management.md`.
