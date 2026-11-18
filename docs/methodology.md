# Scientific and numerical methodology

This document describes the current Stage 1.1 architecture with Stage 1.2 scientific remediation (model version 0.3.0). The governing equations, twelve states, five conserved volumes, separate baroreceptor signals, and independent cerebral pressure/CO2 pathways are unchanged from Stage 1.1; Stage 1.2 revised effective regional heights and the cerebral residual slope. Current decisions and readiness are in `docs/stage1-2/`, with executed before/after evidence in `validation/stage1-2/`. The Stage 1.1 design records and predefined reporting windows remain in `docs/stage1-1/` as history. Current release execution comprises 343 passed, 1 skipped, strict traceability 0/0/0, strict OCPE validation 0/0, regenerated regression fixtures, 61 local plus 27 grid plus 3 chronotropic-split sensitivity scenarios, and six regenerated demonstrations. Scientific readiness is **PARTIAL** because two 60° CO comparisons still miss and pressure over-defence remains. Stage 1.1 and Stage 1 numerical results quoted below are labeled historical records, not current outcomes.

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
- `calibrated_or_assumed_requires_validation`: a value chosen to express a mechanism or temporal scenario, such as stressed-volume factor 0.92 or the hEDS lower-limb venous compliance of 58.3333 mL/mmHg (migrated from the original aggregated peripheral-compliance 140 mL/mmHg scenario as 140 × 50/120).
- `assumed_computational_operating_point`: a healthy/reference numerical choice required to close the reduced-order equations.

Supported ranges are deterministic sensitivity/scenario ranges, **not** confidence intervals, reference ranges, priors, or population distributions. No value becomes patient-specific because it resembles a published group mean. Important compartment mismatches are explicit: plasma volume is not total stressed volume; arterial pulse-wave velocity is not venous compliance; a normalized cerebral index is not measured volumetric CBF; normalized functional capacity is not VO2.

## Phenotype construction

A phenotype YAML contains its ID, diseases, mechanism and evidence links, parameter overrides, maturity, classification, and limitations. `compose_phenotypes()` merges only non-conflicting values. A conflict instructs the researcher to define an explicit comorbidity configuration with its own evidence and joint calibration. The hEDS/ME/CFS comorbid YAML is such an explicit record; arbitrary silent stacking is not supported.

POTS configurations demonstrate that neuropathic, hyperadrenergic, and hypovolemic mechanisms can overlap. Long COVID autonomic and exertional records remain separate. hEDS venous compliance is an hEDS-only exploratory scenario and does not describe vascular EDS or all EDS subtypes.

## Protocols and boundary conditions

Protocols are piecewise-constant declared inputs. Each segment declares posture—an explicit `tilt_angle_deg` in [0, 90] or the legacy `upright` fraction migrated through `degrees(arcsin(upright))`, never both—plus `exertion`, `rhythmic_muscle_activity`, and `sustained_muscle_contraction` bounded to [0, 1], and an optional `end_tidal_co2_mmHg` that defaults to the 40 mmHg model reference. During `transition_duration` only the posture angle is linearly interpolated; all other inputs remain piecewise constant. Metabolic exertion is never used as a proxy for either muscle input, and posture never infers hypocapnia. The registered protocol set comprises the Stage 1 nine plus the Stage 1.1 additions (19 protocols registered in the synchronized 0.3.0 simulation registry):

- `resting-baseline`: stable supine/resting operation.
- `head-up-tilt`: 120 s supine, 30 s passive transition, 480 s at 70 degrees.
- `passive-tilt-30/45/60/70` (Stage 1.1): graded passive tilt geometry with a 30 s transition and reference ETCO2.
- `active-standing` (Stage 1.1): 3 s active transition to 90 degrees with ten seconds of declared low-level muscle activity, followed by sustained quiet standing; activity magnitudes are protocol assumptions, not a calibrated gait model.
- `tilt-recovery`: 70-degree tilt followed by a 30 s linear tilt-back and a 600 s supine recovery window.
- Cerebral CO2 isolation protocols (Stage 1.1, `simulations/cerebral/`): `pressure-reduction`, `co2-reduction`, `combined-pressure-co2-reduction`, `pressure-recovery-persistent-hypocapnia`, and `co2-recovery-persistent-pressure-reduction`, separating hydrostatic-pressure and declared-ETCO2 effects on the cerebral-flow index.
- `inactive-standing`: upright posture with no exertion and no muscle input.
- `light-rhythmic-activity`: upright rhythmic muscle activity without metabolic exertion, isolating the mechanical pump.
- `walking`: upright exertion combined with rhythmic muscle-pump activity, followed by supine recovery.
- `sustained-contraction`: upright sustained muscle contraction without rhythmic pump activity, isolating the venous impediment.
- `single-exertion-recovery`: baseline, a 20-minute normalized exertion bout, and 72-hour follow-up.
- `repeated-exertion-recovery`: two 20-minute normalized bouts separated by 24 hours, with six-day post-day-2 follow-up (seven-day total duration).

All five initial stressed volumes are scaled by `blood_volume_factor`; all later volume exchange is conservative across the five compartments, whose derivatives telescope exactly. The healthy baseline partitions systemic flow 25/25/50 across splanchnic, lower-limb, and other-systemic paths at a 2550 mL total stressed volume. Uniform volume scaling alone does not preserve the exact supine fixed point, so each phenotype derives its regional resistances, baroreflex pressure setpoints, and initial cerebral-flow index from the configured volumes and compliances; the Stage 1 record tested all ten configurations as exact supine fixed points, and the equivalent 0.3.0 check is executed in the mathematical layer (45 passed, including exact supine fixed points of all registered configurations under 0.3.0 parameters). The three autonomic effector states, exertion, delayed stress, and PEM start at their declared reference values (0.5 for each autonomic state, 0 otherwise). Flows are clamped to nonnegative values. HR and extraction are bounded for numerical and physiological safety. These clamps are modeling assumptions and can conceal regimes outside the intended operating domain; failed pressure regimes are reported rather than clipped into plausibility.

## Solver and numerical checks

DOP853 integrates the twelve-state ODE system. Protocol YAML records output interval, maximum internal step, `rtol`, and `atol`. The mathematical layer checks:

- exact instantaneous five-volume balance cancellation (RHS telescoping) and tight simulated volume drift, including walking, sustained-contraction, graded-tilt, active-standing, and tilt-back protocols;
- the exact supine fixed point of every registered configuration;
- finite states and outputs;
- convergence under tighter tolerances and smaller steps;
- stable resting behavior and meaningful response directionality.

The 0.3.0 mathematical layer executed these checks (45 passed, 289 deselected in 9.79s); the Stage 1 record covered the equivalent four-volume, eleven-state properties. Numerical convergence verifies approximation to the implemented equations. It says nothing about whether those equations represent a patient.

## Empirical comparisons

Empirical tests use predeclared broad scenario bands around published group-level observations:

- the adult POTS HR-rise criterion applied to the **sustained** response—mean HR over the final 120 s of the upright window minus the supine baseline—with the peak first-300-s rise and MAP reported separately;
- delayed PEM timing rather than immediate fatigue;
- heterogeneous repeated-CPET capacity reductions over the seven-day repeated-exertion protocol;
- ME/CFS cerebral-flow group means and recovery limitations;
- selected invasive-CPET oxygen-extraction findings.

The following healthy values in this paragraph are the **Stage 1 (0.2.0) historical record**, not current Stage 1.2 outcomes: early cardiac-output reduction was approximately 5.64%, below the broad 10–30% plausibility band; caudal accumulation was approximately 336.55 mL; end-tilt cerebral-flow-index reduction was approximately 0.003%; and heart-level MAP rose approximately 17.4 mmHg to 117.4 mmHg. Those results remain preserved to document the prior architecture. Current Stage 1.2 results and limitations are reported separately below.

These are plausibility comparisons, not fitted individual data, held-out patient predictions, diagnostic sensitivity/specificity, or prospective external validation. Overlapping evidence used for calibration is not relabeled as independent validation. Historical anchor values are Stage 1 (0.2.0) results, while the following paragraph reports the executed 0.3.0 comparison separately; the anchors and the predefined time-resolved CO/SV/HR reporting windows (supine baseline, transition, early upright, peak first-300-s, sustained final-120-s, and tilt-back recovery windows—see `docs/stage1-1/validation-matrix.md`) carry into the Stage 1.1 rerun unchanged.

The executed Stage 1.2 comparison uses the unchanged Stage 1.1 anchors and reporting windows. Healthy 70° early minimum CO reduction is 14.570%, sustained HR rise 15.467 bpm, caudal pooling 302.962 mL, and end-CFI reduction 4.407%, all within their preserved broad bands. Six of eight Zaidi 60°/70° two/five-minute CO/SV comparisons pass; the two misses are 60° CO reductions of 15.801% and 15.800% versus the unchanged 17–20% band. Neuropathic, hyperadrenergic, hypovolemic, and mixed POTS sustained HR rises are 36.724, 43.175, 41.793, and 41.686 bpm; Long-COVID-autonomic is 32.575 bpm. All meet the unchanged ≥30 bpm scenario criterion with upright MAP above 70 mmHg. ME/CFS CFI reduction is 24.652%, within 15–35%. Five cerebral isolation experiments preserve independent pressure and declared-CO2 controls. No threshold was widened and no POTS chronotropic gain was changed. These remain deterministic research scenarios with calibration overlap, not independent or clinical validation. Stage 1.1 baseline values are preserved in `validation/stage1-1/` and the Stage 1.2 before/after matrix.

## Sensitivity and uncertainty

Local one-at-a-time perturbations calculate centered output changes and normalized sensitivities where a nonzero baseline permits them. The Stage 1 (0.2.0) deterministic sensitivity export contained **42 local scenarios**, **18 grid scenarios**, and **3 chronotropic-split scenarios** referencing pre-0.3.0 parameter names (gravity pressure offsets, the single baroreflex setpoint/scale, the fixed head offset); it is preserved history. The current Stage 1.2 sensitivity export is **regenerated and complete** — **61 local scenarios, 27 grid scenarios, and 3 chronotropic-split scenarios** — rebuilt around hydrostatic heights, aortic/carotid setpoints/scales/weights/heights, the cerebral outflow pressure, the CO2 parameters, and the other-systemic resistances, and extended with local CO2-reactivity and CO2-clip scenarios and a CO2-reactivity × cerebral-outflow-pressure grid (14 sensitivity/uncertainty tests passed; current evidence is in `validation/stage1-2/`):

- Local perturbations cover regional compliances, resistances, sympathetic gains, hydrostatic heights, blood-volume factor, the three autonomic time constants, the autoregulation residual slope (around the neuropathic POTS scenario), the hEDS lower-limb venous compliance, the four muscle-pump parameters (healthy light rhythmic activity), the sustained-contraction resistance gain (healthy sustained contraction), and the cerebral CO2-reactivity and CO2-clip scenarios.
- Small full factorial grids examine interacting assumptions: hEDS lower-limb venous compliance × lower-limb hydrostatic height, ME/CFS delayed-stress constant × PEM onset constant, and the CO2-reactivity × cerebral-outflow-pressure grid.
- The chronotropic-split scenarios hold total chronotropic gain fixed and vary the cardiac-sympathetic fraction over 0, 0.5, and 1, demonstrating that the split changes the peak but not the sustained HR rise and remains unidentified by current evidence.

Every row has a configuration SHA and is labeled a deterministic scenario with no probability. **No scenario in the current grids ends below the 70 mmHg MAP screening threshold**—the hEDS grid spans final MAP values of approximately 108.24–110.50 mmHg. The pre-revision hEDS grid did contain three below-70-mmHg failures (minimum approximately 37.84 mmHg); those remain preserved as historical negative results under `validation/baseline/stage0/` and in the legacy audit, and they continue to motivate the M2 maturity of the hEDS compliance scenario. The analysis does not perform patient-cohort simulation, Bayesian inference, global identifiability, or population uncertainty quantification.

## Observation mapping

`cardiac_output_l_min` is the simulator-native L/min output. The observation mapper explicitly aliases it to the OCPE cardiac-output quantity without a second unit conversion. Other mapped outputs include HR, MAP, stroke volume, cerebral index, metabolic capacity, and normalized PEM severity. Final-time demonstration observations are validated strictly with zero errors and warnings. No ECG/PPG waveform, HRV, respiratory, temperature, electrodermal, or accelerometry signal is synthesized.

## Reproducibility and change control

Run `scripts/run_examples.py`, `scripts/run_sensitivity.py`, and `scripts/run_validation.py` from a clean source checkout. Preserve configuration hashes, exact OCPE commit, dependency versions, fixture version, and validation reports. Equation, evidence, parameter, phenotype, or fixture changes require impact analysis across linked records; see `docs/scientific-change-management.md`.
