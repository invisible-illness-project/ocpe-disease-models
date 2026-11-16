# Stage 1 parameter provenance and uncertainty audit

This document audits every parameter of the Stage 1 revised shared model
(model version 0.2.0, `src/ocpe_disease_models/models/shared/model.py`). The
authoritative machine-readable record is `literature/parameter_registry.yaml`
(52 entries, schema `validation/traceability/schemas/parameter_registry.schema.json`).
The strict traceability audit (`validation/traceability/audit/traceability_report.md`)
confirms 52/52 parameters with id, source, estimation method, and provenance, and
100% fully documented, with zero errors, warnings, and infos. This document is a
human-readable synthesis; in any discrepancy the registry governs.

Scope note: this is a research demonstration. No parameter is a direct patient
measurement, no patient-specific calibration has been performed, and all 52
registry entries carry `calibration.required_for_patient_use: true` with
`current_status: research demonstration only`.

## 1. Registry policy and provenance classes

Registry policy (`literature/parameter_registry.yaml`, `registry_policy`):

- Nominal values are executable research assumptions unless explicitly described
  otherwise. Literature supports structure, direction, or group-level
  constraints, not automatic patient validity.
- Supported ranges define deterministic sensitivity scenarios, not probability
  distributions or synthetic patient cohorts.

Each parameter carries a `value_class`. The 52 parameters distribute as follows:

| Value class | Count | Meaning |
|---|---:|---|
| `assumed_computational_operating_point` | 31 | Explicit computational operating-point choice; not estimated from any patient |
| `calibrated_or_assumed_requires_validation` | 14 | Scenario calibration constrained by cited group-level direction or temporal observations; not a fitted patient measurement |
| `derived_from_model_operating_point` | 5 | Algebraically derived from the healthy (or phenotype) supine fixed point |
| `derived_from_published_group_measurements` | 2 | Anchored to published group-level measurements (invasive CPET); not patient-specific |

"Calibrated" here means deterministic scenario calibration against declared
scenario criteria (for example the >=30 bpm sustained adult orthostatic HR-rise
scenario threshold, CLM-POTS-CRITERIA) — never curve fitting to individual
patient data. "Derived" means exact algebra from the declared operating point.
"Measured-anchored" applies only to the two extraction parameters and remains
group-level. Evidence grades (E0–E5, `docs/maturity-model.md`) attach to the
linked evidence claims; maturity levels (M0–M4) attach to mechanisms and
phenotypes. Neither raises a parameter above its value class.

## 2. Complete parameter audit (all 52 fields)

Healthy nominal values below equal the `ModelParameters` defaults and the
registry `value`/`healthy_reference_value`. "Range" is the declared
deterministic sensitivity/scenario range. Override counts are the number of
phenotype YAMLs that set the field (full matrix in section 4).

### 2.1 Compliances (4) — mL/mmHg

| Model field | Healthy | Range | Class | Overrides |
|---|---:|---|---|---:|
| `arterial_compliance` | 1.5 | 1.0–2.0 | assumed | 0 |
| `central_venous_compliance` | 140.0 | 100–180 | assumed | 0 |
| `splanchnic_venous_compliance` | 70.0 | 40–100 | assumed | 0 |
| `lower_limb_venous_compliance` | 50.0 | 35–70 | assumed | 2 (hEDS 58.3333) |

### 2.2 Regional resistances (4) — mmHg·s/mL — derived from supine fixed point

| Model field | Healthy | Range | Class | Overrides |
|---|---:|---|---|---:|
| `splanchnic_arterial_resistance` | 2.204081632653061 | 1.8–2.6 | derived | 3 (POTS) |
| `lower_limb_arterial_resistance` | 2.204081632653061 | 1.8–2.6 | derived | 3 (POTS) |
| `splanchnic_venous_resistance` | 0.12244897959183673 | 0.08–0.17 | derived | 3 (POTS) |
| `lower_limb_venous_resistance` | 0.12244897959183673 | 0.08–0.17 | derived | 3 (POTS) |

### 2.3 Regional control gains (dimensionless) and gravity offsets (mmHg) (4)

| Model field | Healthy | Range | Class | Overrides |
|---|---:|---|---|---:|
| `splanchnic_resistance_sympathetic_gain` | 0.8 | 0.4–1.2 | calibrated | 6 (incl. range exception) |
| `lower_limb_resistance_sympathetic_gain` | 0.8 | 0.4–1.2 | calibrated | 6 (incl. range exception) |
| `splanchnic_gravity_pressure_offset` | 4.0 | 3.0–6.0 | calibrated | 8 |
| `lower_limb_gravity_pressure_offset` | 8.0 | 6.0–12.0 | calibrated | 8 |

### 2.4 Initial volumes, pressures, and volume scaling (5)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `arterial_volume_initial` | 150.0 | 120–180 | mL | assumed | 0 |
| `central_venous_volume_initial` | 700.0 | 560–840 | mL | assumed | 0 |
| `splanchnic_venous_pressure_initial` | 10.0 | 8–12 | mmHg | assumed | 0 |
| `lower_limb_venous_pressure_initial` | 10.0 | 8–12 | mmHg | assumed | 0 |
| `blood_volume_factor` | 1.0 | 0.85–1.05 | dimensionless multiplier | calibrated | 2 |

### 2.5 Cardiac, baroreflex, and autonomic (13)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `stroke_volume_max` | 100.0 | 80–120 | mL/beat | assumed | 0 |
| `stroke_volume_half_volume` | 300.0 | 200–400 | mL | assumed | 0 |
| `contractility_sympathetic_gain` | 0.25 | 0.1–0.4 | dimensionless | assumed | 0 |
| `heart_rate_rest` | 70.0 | 60–80 | beats/min | assumed | 8 (migrated operating point) |
| `heart_rate_cardiac_sympathetic_gain` | 20.0 | 10–75 | beats/min | calibrated | 8 |
| `heart_rate_vagal_gain` | 20.0 | 10–75 | beats/min | calibrated | 8 |
| `baroreflex_pressure_setpoint` | 100.0 | 90–105 | mmHg | assumed | 2 (fixed-point derived) |
| `baroreflex_pressure_scale` | 2.0 | 1.5–3.0 | mmHg | calibrated | 3 (incl. range exception) |
| `cardiac_sympathetic_time_constant` | 6.0 | 3–10 | s | assumed | 0 |
| `vascular_sympathetic_time_constant` | 10.0 | 5–15 | s | assumed | 0 |
| `vagal_time_constant` | 1.0 | 0.5–2.0 | s | assumed | 0 |
| `exercise_heart_rate_gain` | 70.0 | 50–90 | beats/min | assumed | 0 |
| `exercise_resistance_reduction` | 0.3 | 0.15–0.45 | dimensionless fraction | assumed | 0 |

### 2.6 Skeletal muscle pump and sustained contraction (5)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `muscle_pump_stroke_volume` | 20.0 | 10–30 | mL | assumed | 0 |
| `muscle_pump_frequency` | 1.0 | 0.5–2.0 | 1/s | assumed | 0 |
| `muscle_pump_effectiveness` | 1.0 | 0.5–1.0 | dimensionless | assumed | 0 |
| `muscle_pump_half_volume` | 500.0 | 250–750 | mL | assumed | 0 |
| `sustained_contraction_resistance_gain` | 3.0 | 1.0–5.0 | dimensionless | calibrated | 0 |

### 2.7 Cerebral perfusion proxy (6)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `head_hydrostatic_pressure_offset` | 20.0 | 15–25 | mmHg | assumed | 0 |
| `cerebral_reference_perfusion_pressure` | 95.0 | 85–105 | mmHg | derived | 0 |
| `cerebral_autoregulation_residual_slope` | 0.2 | 0.1–0.4 | dimensionless | assumed | 0 |
| `cerebral_orthostatic_impairment` | 0.0 | 0.0–0.3 | dimensionless fraction | calibrated | 3 |
| `cerebral_decline_time_constant` | 5.0 | 3–10 | s | assumed | 0 |
| `cerebral_recovery_time_constant` | 12.0 | 6–240 | s | assumed | 2 |

### 2.8 Metabolic capacity and oxygen extraction (5)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `baseline_metabolic_capacity` | 1.0 | 0.8–1.0 | normalized fraction | assumed | 4 |
| `oxygen_extraction_fraction` | 0.78 | 0.39–0.88 | dimensionless fraction | measured-anchored (group) | 3 |
| `functional_capacity_reference_extraction` | 0.78 | 0.7–0.85 | dimensionless fraction | measured-anchored (group) | 0 |
| `pem_capacity_penalty` | 0.5 | 0.3–0.7 | dimensionless fraction | calibrated | 0 |
| `pem_extraction_penalty` | 0.1 | 0.0–0.2 | dimensionless fraction | calibrated | 0 |

### 2.9 Exertion and PEM dynamics (6)

| Model field | Healthy | Range | Units | Class | Overrides |
|---|---:|---|---|---|---:|
| `exertional_load_time_constant` | 1800.0 | 900–3600 | s | assumed | 0 |
| `delayed_stress_time_constant` | 21600.0 | 14400–43200 | s | assumed | 2 (both range exceptions) |
| `pem_onset_time_constant` | 86400.0 | 43200–172800 | s | assumed | 1 |
| `pem_recovery_time_constant` | 172800.0 | 86400–604800 | s | assumed | 1 |
| `pem_trigger_threshold` | 0.999 | 0.0005–0.01 | normalized delayed-stress units | calibrated | 4 |
| `pem_response_gain` | 0.0 | 0.0–20.0 | dimensionless | calibrated | 4 |

Count check: 4 + 4 + 4 + 5 + 13 + 5 + 6 + 5 + 6 = 52. Every field above is a
`ModelParameters` dataclass field and a `PAR-*` registry entry; the registry
additionally records evidence claims, references, equations, validation links,
provenance, and per-phenotype values for each.

Special note on `pem_trigger_threshold`: the healthy nominal 0.999 is
intentionally outside the declared active-PEM scenario range 0.0005–0.01; the
registry range status states that 0.999 keeps PEM near its ceiling in the
healthy reference while `pem_response_gain` 0.0 disables the PEM response
there. This is a declared design choice recorded in the range status, not one
of the five registered range exceptions (section 5).

## 3. Fixed-point and migration derivations (exact)

All derived values below were re-verified against the executable equations in
`model.py` (`initial_state`, `_derived`) and are enforced per phenotype by
`tests/mathematical/test_equilibrium.py` (VAL-MATH-EQUILIBRIUM: supine residual
< 1e-9 and CO/flow identities for every configured phenotype).

### 3.1 Healthy supine operating point

With `blood_volume_factor` 1.0: V_a = 150, V_c = 700, V_s = 10×70 = 700,
V_l = 10×50 = 500 mL (total stressed volume 2050 mL); P_a = 100, P_c = 5,
P_s = P_l = 10 mmHg; SV = 100×700/(700+300) = 70 mL/beat at contractility 1;
HR = 70 bpm; Q_co = 70×70/60 = 81.6667 mL/s (4.9 L/min); equal regional split
q = 40.8333 mL/s per bed.

### 3.2 Derived resistances (5 derived-class parameters)

- `splanchnic_arterial_resistance` = `lower_limb_arterial_resistance`
  = (P_a − P_s)/q = 90/40.8333 = 2.2040816327 mmHg·s/mL.
- `splanchnic_venous_resistance` = `lower_limb_venous_resistance`
  = (P_s − P_c)/q = 5/40.8333 = 0.1224489796 mmHg·s/mL.
- `cerebral_reference_perfusion_pressure` = P_a − P_c = 95 mmHg (healthy supine
  CPP), so CFI = 1 at the operating point.

### 3.3 Per-phenotype fixed-point resistance and setpoint re-derivation

Phenotypes that change resting CO or stressed volume re-derive the four
regional resistances from their own supine gradients and flows so the
configured initial state remains an exact fixed point:

| Phenotype | Changed inputs | Supine P_a / P_c / P_s / P_l (mmHg) | CO (mL/s) | q = CO/2 | R_art (both beds) | R_ven (both beds) |
|---|---|---|---:|---:|---:|---:|
| pots-hyperadrenergic | `heart_rate_rest` 71.5 | 100 / 5 / 10 / 10 | 83.4167 | 41.7083 | 2.1578421578421576 | 0.11988011988011989 |
| pots-hypovolemic | `blood_volume_factor` 0.92 | 92 / 4.6 / 9.2 / 9.2 | 79.5904 | 39.7952 | 2.08065306122449 | 0.11559183673469388 |
| pots-mixed | `blood_volume_factor` 0.96 | 96 / 4.8 / 9.6 / 9.6 | 80.6584 | 40.3292 | 2.1423673469387756 | 0.11902040816326531 |

Derivation: volumes scale by the factor (V_a = 150f, V_c = 700f, V_s = 700f,
V_l = 500f mL); pressures follow from unchanged compliances; SV =
100·V_c/(V_c+300); q = HR_rest·SV/120; R_art = (P_a − P_s)/q;
R_ven = (P_s − P_c)/q. The baroreflex setpoint is set to the new supine
arterial pressure so the baroreflex target stays 0.5 at the fixed point:
`baroreflex_pressure_setpoint` 92.0 (hypovolemic) and 96.0 (mixed). These
overrides are consistency derivations, not physiological measurements; the
hypovolemic configuration deliberately does not restore resting CO to healthy.

### 3.4 Stage 0 → Stage 1 migration identities

- Chronotropic migration is exact at the supine operating point:
  HR_rest,new = HR_base,old + 0.5·g_HR,old and g_Sc + g_V = g_HR,old with a
  default equal split. Applied to the archived Stage 0 values: healthy
  50 + 0.5×40 = 70; neuropathic 37.5 + 32.5 = 70; hyperadrenergic
  20 + 51.5 = 71.5; hypovolemic 30 + 40 = 70; mixed 32.5 + 37.5 = 70.
- Gravity split: G_old → (G_s, G_l) = (G_old/2, G_old): healthy 8 → (4, 8);
  hEDS/ME-CFS 9 → (4.5, 9); POTS 10 → (5, 10); Long COVID autonomic
  11 → (5.5, 11).
- hEDS compliance migration: `lower_limb_venous_compliance` =
  C_p,old × (50/120) = 140 × 50/120 = 58.333333333333336 mL/mmHg. This is an
  exploratory constant-pressure compliance scenario (P_l(0) held at 10 mmHg;
  total stressed volume intentionally not volume-matched to healthy), not an
  hEDS blood-volume claim, and the configuration remains M2.

## 4. Phenotype overrides, including the reviewed chronotropic calibrations

Ten phenotype configurations exist: `healthy-reference` (no overrides, M3),
`pots-neuropathic` (M3), `pots-hyperadrenergic` (M3), `pots-hypovolemic` (M3),
`pots-mixed` (M2), `eds-heds-vascular` (M2), `eds-heds-mecfs-comorbid` (M2),
`mecfs-pem` (M3), `long-covid-autonomic` (M3), `long-covid-exertional` (M3).
All overrides live in `phenotypes/**/*.yaml` and are mirrored one-to-one in the
registry `phenotype_values` blocks; no disease label branches the shared
equations.

### 4.1 Chronotropic calibrations (exact reviewed values)

`heart_rate_rest` (bpm) / `heart_rate_cardiac_sympathetic_gain` (bpm) /
`heart_rate_vagal_gain` (bpm), with the equal split g_Sc = g_V retained in
every phenotype:

| Phenotype | HR_rest | g_Sc | g_V | Total gain | Basis |
|---|---:|---:|---:|---:|---|
| healthy-reference | 70.0 | 20.0 | 20.0 | 40 | Migrated split of the Stage 0 healthy gain |
| eds-heds-vascular / eds-heds-mecfs-comorbid | 70.0 | 30.0 | 30.0 | 60 | Calibrated scenario gain |
| mecfs-pem | 70.0 | 25.0 | 25.0 | 50 | Calibrated scenario gain |
| long-covid-autonomic | 70.0 | 50.0 | 50.0 | 100 | Sustained >= 30 bpm orthostatic-rise scenario calibration |
| long-covid-exertional | 70.0 | 20.0 | 20.0 | 40 | Healthy defaults retained (no POTS-like tachycardia required) |
| pots-neuropathic | 70.0 | 40.0 | 40.0 | 80 | Sustained >= 30 bpm scenario calibration (executed sustained rise 31.63 bpm) |
| pots-hyperadrenergic | 71.5 | 70.0 | 70.0 | 140 | Hyperadrenergic direction; catecholamine dynamics not modeled |
| pots-hypovolemic | 70.0 | 60.0 | 60.0 | 120 | Sustained >= 30 bpm scenario calibration with fixed-point resistance/setpoint re-derivation |
| pots-mixed | 70.0 | 50.0 | 50.0 | 100 | Intermediate composition (M2, exploratory) |

The review basis is the Stage 1 change record in
`validation/fixtures/regression_fixtures.json` ("per-phenotype supine
fixed-point calibration; sustained POTS/Long-COVID chronotropic calibration")
plus the validation correction in
`docs/stage1/revised-physiological-architecture.md` that the consensus
criterion concerns the sustained, not peak, HR rise. Total gains were set so
the POTS scenarios and the Long COVID autonomic scenario meet or exceed the
30 bpm sustained-rise scenario threshold (VAL-POTS-* and the disease-phenotype
layer); agreement with that threshold is scenario acceptance, not diagnostic
validation, and calibration overlap with the acceptance metric means these
gains are not independently identified. The 31.63 bpm neuropathic sustained
figure is taken from `validation/sensitivity/chronotropic_split.json`.

### 4.2 Remaining phenotype overrides (all fields, all phenotypes)

- `lower_limb_venous_compliance` (mL/mmHg): eds-heds-vascular 58.333333333333336; eds-heds-mecfs-comorbid 58.333333333333336.
- `splanchnic_arterial_resistance` / `lower_limb_arterial_resistance` (mmHg·s/mL): pots-hyperadrenergic 2.1578421578421576; pots-hypovolemic 2.08065306122449; pots-mixed 2.1423673469387756.
- `splanchnic_venous_resistance` / `lower_limb_venous_resistance` (mmHg·s/mL): pots-hyperadrenergic 0.11988011988011989; pots-hypovolemic 0.11559183673469388; pots-mixed 0.11902040816326531.
- `splanchnic_resistance_sympathetic_gain` / `lower_limb_resistance_sympathetic_gain`: eds-heds-vascular 0.7; eds-heds-mecfs-comorbid 0.7; pots-hyperadrenergic 1.0; pots-hypovolemic 0.9; pots-mixed 0.55; pots-neuropathic 0.35 (range exception, section 5).
- `splanchnic_gravity_pressure_offset` (mmHg): eds-heds-vascular 4.5; eds-heds-mecfs-comorbid 4.5; mecfs-pem 4.5; long-covid-autonomic 5.5; all four POTS phenotypes 5.0.
- `lower_limb_gravity_pressure_offset` (mmHg): eds-heds-vascular 9.0; eds-heds-mecfs-comorbid 9.0; mecfs-pem 9.0; long-covid-autonomic 11.0; all four POTS phenotypes 10.0.
- `blood_volume_factor`: pots-hypovolemic 0.92; pots-mixed 0.96 (assumed demonstration values, not measured plasma-volume deficits; REF-RAJ-2005 measured deficit is 12.8 ± 7.6% of ideal in a small cohort and is not equated with this scaling).
- `baroreflex_pressure_setpoint` (mmHg): pots-hypovolemic 92.0; pots-mixed 96.0 (fixed-point derivations, section 3.3).
- `baroreflex_pressure_scale` (mmHg): pots-hyperadrenergic 1.5; pots-mixed 3.0; pots-hypovolemic 6.0 (range exception, section 5).
- `cerebral_orthostatic_impairment`: mecfs-pem 0.23; eds-heds-mecfs-comorbid 0.23; long-covid-autonomic 0.08 (exploratory multipliers, not direct measurements).
- `cerebral_recovery_time_constant` (s): mecfs-pem 240.0; eds-heds-mecfs-comorbid 240.0.
- `baseline_metabolic_capacity`: eds-heds-mecfs-comorbid 0.85; mecfs-pem 0.85; long-covid-autonomic 0.85; long-covid-exertional 0.8.
- `oxygen_extraction_fraction`: mecfs-pem 0.74; eds-heds-mecfs-comorbid 0.74; long-covid-exertional 0.49. Only 0.78 (healthy) and 0.49 (Long COVID exertional) are anchored to the selected invasive-CPET control/patient groups (REF-SINGH-2022, CLM-LC-EXTRACTION); the 0.74 values are computational assumptions and are not substituted across diseases.
- `delayed_stress_time_constant` (s): mecfs-pem 72000.0; eds-heds-mecfs-comorbid 72000.0 (both range exceptions, section 5).
- `pem_onset_time_constant` (s): mecfs-pem 86400.0 (equals the healthy default; restated after the Stage 1 onset/recovery correction).
- `pem_recovery_time_constant` (s): mecfs-pem 172800.0 (equals the healthy default; restated).
- `pem_trigger_threshold`: mecfs-pem, eds-heds-mecfs-comorbid, long-covid-autonomic, long-covid-exertional 0.001 (inside the active-PEM scenario range).
- `pem_response_gain`: mecfs-pem 20.0; eds-heds-mecfs-comorbid 20.0; long-covid-exertional 16.0; long-covid-autonomic 12.0.

Fields with no phenotype override in any configuration: all four compliances
except the hEDS lower-limb value, all initial volumes/pressures,
`stroke_volume_max`, `stroke_volume_half_volume`,
`contractility_sympathetic_gain`, all three autonomic time constants,
`exercise_heart_rate_gain`, `exercise_resistance_reduction`, all five muscle
parameters, `head_hydrostatic_pressure_offset`,
`cerebral_reference_perfusion_pressure`,
`cerebral_autoregulation_residual_slope`, `cerebral_decline_time_constant`,
`functional_capacity_reference_extraction`, `pem_capacity_penalty`,
`pem_extraction_penalty`, and `exertional_load_time_constant`.

## 5. Registered range exceptions (exactly five)

Five phenotype values intentionally sit outside their declared local
sensitivity/scenario ranges and carry explicit `range_exception` text in the
registry. They are scenario calibrations; they do not widen the supported
ranges and are not patient measurements.

| # | Parameter | Phenotype | Value | Declared range | Registered rationale |
|---|---|---|---:|---|---|
| 1 | `splanchnic_resistance_sympathetic_gain` | pots-neuropathic | 0.35 | 0.4–1.2 | Demonstrated reduced splanchnic vasoconstrictive response |
| 2 | `lower_limb_resistance_sympathetic_gain` | pots-neuropathic | 0.35 | 0.4–1.2 | Demonstrated reduced lower-limb vasoconstrictive response |
| 3 | `baroreflex_pressure_scale` | pots-hypovolemic | 6.0 mmHg | 1.5–3.0 mmHg | Scenario calibration; independent calibration still required |
| 4 | `delayed_stress_time_constant` | mecfs-pem | 72000 s (20 h) | 14400–43200 s | Prolonged PEM delay beyond the healthy scenario range |
| 5 | `delayed_stress_time_constant` | eds-heds-mecfs-comorbid | 72000 s (20 h) | 14400–43200 s | Same exploratory comorbid delay |

The `pem_trigger_threshold` healthy nominal (0.999) outside the active-PEM
range is separately and deliberately declared in that parameter's range status
(section 2.9) and is not counted here.

## 6. Sensitivity, uncertainty, and identifiability results

All sensitivity artifacts are deterministic (DOP853, rtol 1e-7, atol 1e-8,
seed 0 fixed; no stochastic sampling, no synthetic cohort). Sources:
`validation/sensitivity/sensitivity-report.md`, `local_sensitivity.json`,
`uncertainty_grid.json`, `chronotropic_split.json`, and fixture
`validation/fixtures/sensitivity_ranges.json` (schema 1.1, central finite
differences on the healthy background, head-up-tilt).

### 6.1 Local sensitivity (one-at-a-time)

Central-difference derivatives on the healthy background (per unit parameter):

- `blood_volume_factor` (step 0.02): d(sustained HR rise) = −24.19 bpm,
  d(final MAP) = +10.91 mmHg — the dominant orthostatic assumption.
- `splanchnic_resistance_sympathetic_gain` (step 0.1): −3.857 bpm, +1.150 mmHg.
- `lower_limb_gravity_pressure_offset` (step 1 mmHg): +0.751 bpm, −0.224 mmHg.
- `lower_limb_venous_compliance` (step 5 mL/mmHg): +0.090 bpm, −0.027 mmHg;
  the hEDS assumption block records sustained rise 11.447 bpm at the healthy
  50.0 versus 12.191 bpm at 58.3333 (hypothesis value, not a measured
  coefficient).

Low-to-high normalized sensitivities on the pots-neuropathic background
(head-up-tilt): `blood_volume_factor` −1.827 (peak) / −2.093 (sustained) for
HR rise and +0.469 for final MAP; `lower_limb_gravity_pressure_offset` +0.767;
`splanchnic_gravity_pressure_offset` +0.514; `lower_limb_venous_compliance`
+0.529; venous resistances +0.269/+0.459; sympathetic gains −0.10 to −0.15;
autonomic time constants near zero for sustained metrics (they shape transient
timing, not the steady state); `cerebral_autoregulation_residual_slope`
≈ 1e-7 on HR (it acts on the cerebral proxy, which is not fed back into
hemodynamics). Muscle-pump parameters on the healthy light-activity background
are small (−0.005 to +0.019 normalized) and `sustained_contraction_resistance_gain`
is +0.279/+0.329 on HR rise. PEM outputs are insensitive to all cardiovascular
perturbations in these protocols (0.0), and vice versa.

### 6.2 Deterministic assumption grids

- eds-heds-vascular (3×3 compliance × gravity grid, 9 scenarios): peak HR rise
  17.12–27.15 bpm, sustained 15.79–25.43 bpm, final MAP 115.0–117.7 mmHg; no
  scenario ends below the 70 mmHg MAP screening threshold.
- mecfs-pem (3×3 delayed-stress × PEM-onset grid, 9 scenarios): PEM peak
  0.0557–0.1207, final functional capacity 0.7841–0.7915, final MAP ≈ 100 mmHg;
  no regime failures. These constants are phenomenological; the grid is not a
  distribution over patients.

### 6.3 Chronotropic split non-identifiability

The Stage 1 architecture separated chronotropy into cardiac-sympathetic and
vagal gains with g_Sc + g_V fixed by the migrated total. The split is
structurally non-identified by current evidence
(`validation/sensitivity/chronotropic_split.json`; pots-neuropathic,
head-up-tilt, total chronotropic gain fixed at 80 bpm, fractions 0 / 0.5 / 1):

| Cardiac-sympathetic fraction | g_Sc / g_V (bpm) | Peak HR rise (bpm) | Sustained HR rise (bpm) | Final MAP (mmHg) |
|---:|---|---:|---:|---:|
| 0.0 | 0 / 80 | 34.99 | 31.63 | 115.71 |
| 0.5 | 40 / 40 | 33.23 | 31.63 | 115.71 |
| 1.0 | 80 / 0 | 32.68 | 31.63 | 115.71 |

Sustained HR rise and final MAP agree to integration precision across all three
splits (heart-rate-final 101.6299 bpm in all rows); only the transient peak
carries a weak signal. The registry therefore records
"split is not identified by the current evidence" and the architecture review
requires this fixed-total-gain test. The 0/80 and 80/0 extremes deliberately
exceed the individual 10–75 bpm scenario ranges of the two gain parameters;
they bound an unidentifiable direction rather than propose phenotype values,
and every shipped phenotype uses the equal split.

### 6.4 Soft anchors and regime screening

Healthy tilt early-CO reduction evaluates to 5.64%, outside the predeclared
10–30% soft plausibility band; the check passes its hard 0–50% bound and emits
an explicit `UserWarning` (recorded in `validation/reports/physiological.log`)
rather than being hidden. Caudal stressed-volume accumulation is screened
against a 300–900 mL soft band. Healthy end-tilt CFI reduction is approximately
0.003%, outside the broad 3–11% disclosure band around the reported 7% control
reduction; the empirical test emits a separate `UserWarning` while preserving
the ME/CFS 15–35% scenario-band assertion. Heart-level MAP rises approximately
17.4 mmHg to 117.4 mmHg in the healthy scenario, so the pressure-only proxy
nearly abolishes the control-side response. These bands are literature-anchored
plausibility screens, not fitted targets.

## 7. Uncertainty limitations

1. **No patient identification.** All 52 parameters are computational operating
   points, group-anchored values, operating-point derivations, or scenario
   calibrations. Every registry entry states that patient-specific calibration
   is required and has not been performed.
2. **Ranges are not distributions.** Supported ranges define deterministic
   sensitivity scenarios only; there are no probability statements, prevalence
   estimates, or synthetic cohorts anywhere in the parameter layer.
3. **Local and two-parameter analyses only.** The sensitivity evidence is
   one-at-a-time central differences, low-to-high normalized spans, and 3×3
   grids. It does not quantify correlated, global, or structural uncertainty,
   and derivative magnitudes are operating-point dependent.
4. **Structural non-identifiability is documented, not resolved.** The
   chronotropic split (section 6.3) is the explicitly tested example; regional
   compliances, regional gains, gravity offsets, pump parameters, autonomic
   lags, and the autoregulation slope are likewise not individually identifiable
   from the cited evidence (architecture review, item 9 of the validation
   strategy; evidence matrix "negative and constraining findings").
5. **Calibration overlap.** Scenario criteria (for example the 30 bpm
   sustained-rise threshold) are used both to calibrate gains and to accept
   scenarios, so passing them is not independent validation. Group-level
   anchors (POTS criteria, PEM timing 12–48 h, repeated-CPET 5.3%/13.8%,
   end-tilt cerebral reduction 26%, extraction 0.49/0.78) are heterogeneous
   plausibility checks with construct mismatch (normalized constructs, not
   measured VO2 or volumetric CBF).
6. **Known quantitative tensions.** The healthy early-CO reduction (5.64%) sits
   outside the 10–30% soft anchor and the healthy end-tilt CFI reduction
   (approximately 0.003%) sits outside the 3–11% disclosure band around the 7%
   control finding; both emit warnings. The ME/CFS PEM scenario first crosses
   0.05 at approximately 5.7 hours after the day-1 bout ends, earlier than the
   12–48-hour daily-activity onset window but within reported post-CPET onset
   within 24 hours. The hEDS
   compliance magnitude is a migration-scaled hypothesis and its configuration
   remains M2.
7. **Structural omissions bound interpretation.** No CO₂, renal/RAAS,
   unstressed-volume, venous-valve, interstitial, pulmonary, or pure-delay
   dynamics; linear compliances; clipped ideal-valve flows; the cerebral-flow
   index is a normalized proxy, and central venous stressed volume is a
   preload proxy, not end-diastolic volume.
8. **Validation status at audit time.** All 26 records in
   `validation/validation_registry.yaml` are `status: PASS` and bound to tested
   source/configuration commit `fb13cb21aa811da9babff6b271f006b8c79ec30f`. The complete clean run at that
   revision passed 287 tests with two intended soft-anchor warnings, and all
   seven independently selected layers passed. The subsequent validation-record
   commit adds executed records and is not retroactively described as tested
   before it existed. Parameter values in this document are audited against the
   registry and executable defaults, which are mutually consistent. PASS status
   is limited to the declared computational checks and does not raise the
   provenance class, evidence grade, maturity, or clinical validity of any
   parameter. Final executed counts, warning totals, commands, and artifact
   hashes are recorded in `docs/stage1/final-validation-report.md` and
   `validation/reproducibility.json`.

## 8. Traceability to the machine-readable registry

- Each row above corresponds to one `PAR-*` entry in
  `literature/parameter_registry.yaml` with: id, name, symbol, `model_field`
  (the exact `ModelParameters` field), healthy/nominal value, units, source,
  estimation method, supported range and its status, qualitative uncertainty,
  calibration status, equation dependencies (`EQ-*`), validation dependencies
  (`VAL-*`), phenotype values with config paths and any `range_exception`,
  provenance text, references (`REF-*`), description, population statement,
  and value class.
- The registry is schema-validated
  (`validation/traceability/schemas/parameter_registry.schema.json`) and the
  strict audit (`scripts/audit_traceability.py`;
  `validation/traceability/audit/traceability_report.{json,md}`) passes with
  zero errors/warnings/infos and 100% parameter completeness.
- Executable defaults in `ModelParameters` and all phenotype YAML overrides are
  audited against the registry by the scientific-traceability test layer
  (`tests/unit/test_traceability_audit.py`,
  `tests/unit/test_declarative_executable_consistency.py`); the chain
  `reference → evidence claim → mechanism → equation → parameter →
  implementation → validation test → simulation output` is intact.
- Related machine-readable companions: `literature/evidence_registry.yaml`
  (claims and grades), `literature/mechanism_registry.yaml` (maturity),
  `literature/equation_registry.yaml`, `validation/validation_registry.yaml`
  (26 records), `simulations/simulation_registry.yaml`, and the sensitivity
  artifacts listed in section 6.
