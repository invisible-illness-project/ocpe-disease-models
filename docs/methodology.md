# Scientific and numerical methodology

This document describes the current Stage 1.1 five-compartment, twelve-state implementation (model version 0.3.0). The Stage 1.1 design record, decision log, validation matrix (including predefined reporting windows and unchanged empirical anchors), and readiness assessment are in `docs/stage1-1/`. The Stage 1 design record, migration formulas, and per-phenotype fixed-point derivation for the superseded 0.2.0 revision are in `docs/stage1/revised-physiological-architecture.md`; the supporting evidence decisions are in `docs/stage1/literature-and-evidence-matrix.md`; the audited original three-compartment implementation is preserved unchanged in `docs/stage1/baseline-scientific-report.md` and `validation/baseline/stage0/`. **Stage 1.1 status:** the deterministic scientific scenario comparison matrix has been executed for 0.3.0 (`validation/stage1-1/scientific-comparison-matrix.md` / `.json`), and release validation (full test suite, strict traceability 0/0/0, strict OCPE package validation 0/0, regression fixtures, sensitivity exports, demonstrations) has been executed at frozen tested commit `a6d7619e277fc05081de3c852189b549d714b8b5` — full suite 323 passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s, with all seven layer execution statuses PASS and the overall seven-layer scientific status **FAIL** from the six preserved strict phenotype xfails. Every numerical validation-suite result quoted below and attributed to Stage 1 is the Stage 1 record bound to the 0.2.0 tested commit, not a 0.3.0 result.

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

The 0.3.0 mathematical layer executed these checks (45 passed, 285 deselected in 9.33s); the Stage 1 record covered the equivalent four-volume, eleven-state properties. Numerical convergence verifies approximation to the implemented equations. It says nothing about whether those equations represent a patient.

## Empirical comparisons

Empirical tests use predeclared broad scenario bands around published group-level observations:

- the adult POTS HR-rise criterion applied to the **sustained** response—mean HR over the final 120 s of the upright window minus the supine baseline—with the peak first-300-s rise and MAP reported separately;
- delayed PEM timing rather than immediate fatigue;
- heterogeneous repeated-CPET capacity reductions over the seven-day repeated-exertion protocol;
- ME/CFS cerebral-flow group means and recovery limitations;
- selected invasive-CPET oxygen-extraction findings.

Healthy orthostatic soft anchors are reported explicitly rather than tuned: the early cardiac-output reduction is approximately 5.64%, **below** the broad 10–30% literature-derived plausibility band, and is retained as a warning-level negative result and structural limitation, not converted into a pass. Caudal stressed-volume accumulation is approximately 336.55 mL, inside the broad 300–900 mL soft band. Separately, the healthy end-tilt cerebral-flow-index reduction is approximately 0.003%, outside the broad 3–11% soft band around the reported 7% control reduction; heart-level MAP rises approximately 17.4 mmHg to 117.4 mmHg in that scenario, leaving the pressure-only proxy almost unchanged. This control-side miss emits a second explicit warning. The ME/CFS 15–35% scenario-band assertion is unchanged. None of these bands is a hard fitted target.

These are plausibility comparisons, not fitted individual data, held-out patient predictions, diagnostic sensitivity/specificity, or prospective external validation. Overlapping evidence used for calibration is not relabeled as independent validation. Historical anchor values are Stage 1 (0.2.0) results, while the following paragraph reports the executed 0.3.0 comparison separately; the anchors and the predefined time-resolved CO/SV/HR reporting windows (supine baseline, transition, early upright, peak first-300-s, sustained final-120-s, and tilt-back recovery windows—see `docs/stage1-1/validation-matrix.md`) carry into the Stage 1.1 rerun unchanged.

The executed 0.3.0 scenario matrix reports against the unchanged Stage 1 anchors and the Zaidi CO/SV ranges newly predeclared for Stage 1.1: healthy 70-degree sustained CO −3.105%, SV −12.733%, HR rise +7.723 bpm, and end-CFI reduction 1.645% (graded 30/45/60-degree sustained HR rises of 3.626/5.417/6.954 bpm); **all eight** Zaidi 60/70-degree 2/5-minute CO/SV comparisons MISS their preserved published ranges (model CO −2.571/−3.105% vs −20 to −17%; SV −11.375/−12.733% vs −34 to −28%); **all four POTS phenotypes FAIL** the unchanged ≥30 bpm sustained-HR-rise criterion (neuropathic 17.428, hyperadrenergic 19.659, hypovolemic 19.399, mixed 19.216 bpm), as does Long-COVID-autonomic (18.931 bpm); the ME/CFS CFI reduction of 22.913% remains within the unchanged 15–35% band; and the cerebral isolation experiments separate the pressure and declared-CO2 pathways (pressure-only target 0.98355 with CO2 factor 1; CO2-only factor 0.70469 with pressure target 1; combined CFI 0.69310; the persistent-hypocapnia and persistent-pressure-reduction recovery experiments remain separated). No threshold was widened and no gain was recalibrated to produce these outcomes; they are deterministic research scenario comparisons, not release validation passes.

## Sensitivity and uncertainty

Local one-at-a-time perturbations calculate centered output changes and normalized sensitivities where a nonzero baseline permits them. The Stage 1 (0.2.0) deterministic sensitivity export contained **42 local scenarios**, **18 grid scenarios**, and **3 chronotropic-split scenarios** referencing pre-0.3.0 parameter names (gravity pressure offsets, the single baroreflex setpoint/scale, the fixed head offset); it is preserved history. The 0.3.0 sensitivity export is **regenerated and complete** — **59 local scenarios, 27 grid scenarios, and 3 chronotropic-split scenarios** — rebuilt around hydrostatic heights, aortic/carotid setpoints/scales/weights/heights, the cerebral outflow pressure, the CO2 parameters, and the other-systemic resistances, and extended with local CO2-reactivity and CO2-clip scenarios and a CO2-reactivity × cerebral-outflow-pressure grid (13 sensitivity tests passed; see `docs/stage1-1/validation-matrix.md`):

- Local perturbations cover regional compliances, resistances, sympathetic gains, hydrostatic heights, blood-volume factor, the three autonomic time constants, the autoregulation residual slope (around the neuropathic POTS scenario), the hEDS lower-limb venous compliance, the four muscle-pump parameters (healthy light rhythmic activity), the sustained-contraction resistance gain (healthy sustained contraction), and the cerebral CO2-reactivity and CO2-clip scenarios.
- Small full factorial grids examine interacting assumptions: hEDS lower-limb venous compliance × lower-limb hydrostatic height, ME/CFS delayed-stress constant × PEM onset constant, and the CO2-reactivity × cerebral-outflow-pressure grid.
- The chronotropic-split scenarios hold total chronotropic gain fixed and vary the cardiac-sympathetic fraction over 0, 0.5, and 1, demonstrating that the split changes the peak but not the sustained HR rise and remains unidentified by current evidence.

Every row has a configuration SHA and is labeled a deterministic scenario with no probability. **No scenario in the current grids ends below the 70 mmHg MAP screening threshold**—the hEDS grid spans final MAP values of approximately 110.67–111.52 mmHg. The pre-revision hEDS grid did contain three below-70-mmHg failures (minimum approximately 37.84 mmHg); those remain preserved as historical negative results under `validation/baseline/stage0/` and in the legacy audit, and they continue to motivate the M2 maturity of the hEDS compliance scenario. The analysis does not perform patient-cohort simulation, Bayesian inference, global identifiability, or population uncertainty quantification.

## Observation mapping

`cardiac_output_l_min` is the simulator-native L/min output. The observation mapper explicitly aliases it to the OCPE cardiac-output quantity without a second unit conversion. Other mapped outputs include HR, MAP, stroke volume, cerebral index, metabolic capacity, and normalized PEM severity. Final-time demonstration observations are validated strictly with zero errors and warnings. No ECG/PPG waveform, HRV, respiratory, temperature, electrodermal, or accelerometry signal is synthesized.

## Reproducibility and change control

Run `scripts/run_examples.py`, `scripts/run_sensitivity.py`, and `scripts/run_validation.py` from a clean source checkout. Preserve configuration hashes, exact OCPE commit, dependency versions, fixture version, and validation reports. Equation, evidence, parameter, phenotype, or fixture changes require impact analysis across linked records; see `docs/scientific-change-management.md`.
