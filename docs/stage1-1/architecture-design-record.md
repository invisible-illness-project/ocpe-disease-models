# Stage 1.1 revised architecture and design record

- Model CURIE: `ocpe:disease-models/shared-physiology`
- Model version: **0.3.0** (Stage 1.1 revision of the Stage 1 model, version 0.2.0)
- Status: **design record; implementation present in source; deterministic scientific scenario matrix executed** (`validation/stage1-1/scientific-comparison-matrix.md` / `.json`); **release validation executed** at frozen tested source commit `a6d7619e277fc05081de3c852189b549d714b8b5` (full suite 323 passed, 1 skipped, 6 xfailed, 2 warnings in 344.19s; all seven layer execution statuses PASS; overall seven-layer scientific status **FAIL** from the six preserved strict phenotype xfails; strict traceability 0 errors/0 warnings/0 infos; strict OCPE package validation 0 errors/0 warnings)

This document records the Stage 1.1 architecture. It does not replace the
Stage 1 design gate (`docs/stage1/revised-physiological-architecture.md`) or
the audited Stage 0 baseline (`docs/stage1/baseline-scientific-report.md`),
which remain unchanged history. Numerical results quoted from Stage 1 are
bound to the 0.2.0 tested commit. Executed 0.3.0 scenario results—including
the negative ones—are recorded in `validation-matrix.md` §§4–6; the executed
0.3.0 release validation record (commit `a6d7619`, overall scientific status
FAIL from the preserved strict phenotype xfails) is summarized in
`readiness-assessment.md` and `validation-matrix.md`.

## Scope of the revision

Stage 1.1 keeps the Stage 1 structure—conservative stressed-volume
compartments, three differentiated autonomic effector states, an explicit
muscle-pump path, a bounded cerebral autoregulation proxy, and the
phenomenological PEM cascade—and makes six targeted changes:

1. a fifth (residual other-systemic) venous compartment with an explicit
   25/25/50 baseline flow partition;
2. hydrostatic posture geometry expressed as heights (cm) times sin(tilt
   angle) instead of fixed mmHg gravity offsets;
3. separate aortic and carotid baroreceptor sensors with an integrated
   weighted baroreflex, distinct from brain-level pressure;
4. explicit `tilt_angle_deg` protocol posture with linear angle-only
   transitions;
5. an explicit per-segment end-tidal CO2 input acting on the cerebral-flow
   target;
6. a fixed effective cerebral outflow pressure replacing the central venous
   back-pressure subtraction.

Everything not listed here—including the bounded pressure-autoregulation
curve, the preload/contractility stroke-volume equation, the PEM equations,
the metabolic/extraction equations, and the muscle-pump equations—is
**retained unchanged** from Stage 1.

## States and volumes (12 states, five volumes)

The state vector now has **12 states**:

| # | State | Unit | Notes |
|---|---|---|---|
| 1 | `arterial_volume` | mL | Arterial stressed volume |
| 2 | `central_venous_volume` | mL | Central venous stressed volume/preload proxy |
| 3 | `splanchnic_venous_volume` | mL | Splanchnic venous stressed volume |
| 4 | `lower_limb_venous_volume` | mL | Lower-limb venous stressed volume |
| 5 | `other_systemic_venous_volume` | mL | **New.** One residual systemic venous compartment lumping all non-splanchnic, non-lower-limb peripheral venous volume |
| 6 | `cardiac_sympathetic_state` | — | Effector state, initial 0.5 |
| 7 | `vascular_sympathetic_state` | — | Effector state, initial 0.5 |
| 8 | `vagal_state` | — | Effector state, initial 0.5 |
| 9 | `exertional_load` | — | Capacity-normalized load |
| 10 | `delayed_stress` | — | Delayed exertional stress |
| 11 | `pem_severity` | — | Normalized phenomenological PEM severity |
| 12 | `cerebral_flow_index` | — | Normalized cerebral-flow approximation (research proxy) |

The five volume derivatives telescope exactly:

```text
dVa/dt + dVc/dt + dVs/dt + dVl/dt + dVo/dt = 0
```

so **exact five-volume conservation** holds analytically, as the four-volume
identity did in Stage 1. The muscle pump still transfers volume from the
lower-limb to the central venous compartment without creating blood.

### Baseline flow partition and total stressed volume

Healthy-reference initial stressed volumes are 150 (arterial) + 700 (central
venous) + 700 (splanchnic venous) + 500 (lower-limb venous) + 500
(other-systemic venous) = **2550 mL total stressed volume** at
`blood_volume_factor = 1`.

Regional resistances were re-derived so that the healthy baseline systemic
flow partitions **25% splanchnic / 25% lower-limb / 50% other-systemic**
while preserving total cardiac output. Relative to Stage 1 defaults, the
splanchnic and lower-limb arterial resistances are doubled
(2.204081632653061 → 4.408163265306122 mmHg·s/mL) and the new
`other_systemic_arterial_resistance` takes the former value
(2.204081632653061); venous resistances follow the same pattern
(0.12244897959183673 → 0.24489795918367346 doubled, other = former value).
The same transformation was applied to every phenotype that explicitly
overrode these resistances (POTS hyperadrenergic, hypovolemic, mixed): both
explicit values were doubled and `other_systemic_*_resistance` was set to the
original value. Phenotypes that use defaults received no new override. This
is a re-partition of the same total conductance, not a change in total
peripheral resistance at the baseline operating point.

## Hydrostatic posture geometry

Fixed mmHg gravity offsets are replaced by heights in centimetres,
converted with `HYDROSTATIC_MMHG_PER_CM = 0.7356` and scaled by the sine of
the resolved tilt angle:

```text
hydrostatic_pressure = 0.7356 × height_cm × sin(tilt_angle)
```

- `splanchnic_hydrostatic_height_cm` (default 5.43773790103317 = 4.0/0.7356),
- `lower_limb_hydrostatic_height_cm` (default 10.87547580206634 = 8.0/0.7356),
- `other_systemic_hydrostatic_height_cm` (default 0.0),
- `aortic_baroreceptor_height_cm` (default 0.0, heart level),
- `carotid_baroreceptor_height_cm` (default 25.0),
- `brain_hydrostatic_height_cm` (default 27.0, replacing the fixed 20 mmHg
  head offset; 27 cm corresponds to ≈19.9 mmHg at 90 degrees).

Phenotype YAML overrides were migrated with full-precision division
(`height = offset / 0.7356`). The heights are lumped per-region geometry,
not measured hydrostatic columns; at 0 degrees every hydrostatic term is
exactly zero.

## Separate aortic/carotid sensors and the integrated weighted baroreflex

Stage 1 used a single head-level pressure proxy for the baroreflex. Stage
1.1 separates the two sensor sites from each other and from brain pressure:

```text
P_aortic  = max(0, Pa - 0.7356 × aortic_baroreceptor_height_cm  × sin(θ))
P_carotid = max(0, Pa - 0.7356 × carotid_baroreceptor_height_cm × sin(θ))
aortic_error  = (aortic_setpoint  - P_aortic)  / aortic_scale
carotid_error = (carotid_setpoint - P_carotid) / carotid_scale
integrated    = 0.25 × aortic_error + 0.75 × carotid_error   (defaults)
baroreflex_target = sigmoid(clip(integrated, ±40))
```

- Aortic and carotid pathways have **independent setpoints and scales**
  (`aortic_/carotid_baroreflex_pressure_setpoint`,
  `aortic_/carotid_baroreflex_pressure_scale`). Phenotype overrides of the
  former single setpoint/scale were duplicated onto both pathways with
  unchanged values.
- The integration weights (`aortic_baroreflex_weight = 0.25`,
  `carotid_baroreflex_weight = 0.75`) are computational assumptions, are
  validated to sum to 1 within 1e-6, and are not measurements of relative
  afferent contributions.
- Brain-level pressure (`brain_hydrostatic_height_cm = 27 cm`) feeds only
  the cerebral perfusion path; it is **not** a baroreflex sensor. The
  carotid sinus (25 cm) and brain (27 cm) heights are deliberately distinct
  parameters.

## Protocol posture and transitions

`ProtocolSegment` now accepts an explicit `tilt_angle_deg` in [0, 90]. The
legacy normalized `upright` fraction remains accepted and is migrated
through `tilt_angle_deg = degrees(arcsin(upright))` (so `upright = 1.0` is
90 degrees); specifying both fields in one segment is an error. During
`transition_duration` the **angle only** is linearly interpolated from the
previous segment's angle; all other inputs (exertion, muscle inputs, ETCO2)
remain piecewise constant. This supports, as registered protocol YAMLs:

- **passive graded tilt**: `passive-tilt-30/45/60/70` and `head-up-tilt`
  (120 s supine, 30 s passive transition, 480 s at angle);
- **active standing**: `active-standing` (3 s transition to 90 degrees with
  ten seconds of declared low-level rhythmic and sustained muscle activity,
  followed by **sustained quiet standing** to 600 s; activity magnitudes are
  protocol assumptions, not a calibrated gait model);
- **tilt-back**: `tilt-recovery` now includes a 30 s linear tilt-back to
  supine and a 600 s supine recovery window;
- **cerebral CO2 isolation protocols**: `pressure-reduction`,
  `co2-reduction`, `combined-pressure-co2-reduction`,
  `pressure-recovery-persistent-hypocapnia`, and
  `co2-recovery-persistent-pressure-reduction` under `simulations/cerebral/`.

## Segment end-tidal CO2 and cerebral CO2 reactivity

Each segment may declare `end_tidal_co2_mmHg`; `None` selects the model
reference `end_tidal_co2_reference_mmHg = 40.0`. The cerebral-flow target is
multiplied by

```text
cerebral_co2_factor = exp(0.035 × clip(ETCO2 - 40, -15, +15))
```

where 0.035/mmHg is `cerebral_co2_reactivity_per_mmHg` and ±15 mmHg is
`cerebral_co2_extrapolation_limit_mmHg`. Consequences, stated deliberately:

- **No posture-inferred hypocapnia.** Tilt does not change ETCO2;
  orthostatic hypocapnia exists in a run only when a protocol segment
  declares it. Upright segments that omit ETCO2 stay at the 40 mmHg
  reference.
- **ETCO2 is not exact PaCO2.** End-tidal CO2 is an approximate, biased
  surrogate of arterial PCO2 (including under orthostasis); the model
  consumes the declared end-tidal value directly and makes no
  ETCO2→PaCO2 correction.
- The ±15 mmHg clip bounds extrapolation of the exponential reactivity
  outside the evidence-supported range; the clip also enters the declared
  cerebral-flow-index upper bound used by the runtime guards.

## Fixed effective cerebral outflow pressure

Cerebral perfusion pressure is now

```text
CPP = max(0, brain_arterial_pressure - 5.0 mmHg)
```

with `cerebral_outflow_pressure_mmHg = 5.0` a **fixed effective downstream
pressure**. It is explicitly **neither thoracic central venous pressure nor
a separately resolved intracranial pressure**: the Stage 1 subtraction of
the central-venous compartment pressure is removed, and no ICP state is
introduced. The bounded pressure-autoregulation curve
(`ratio / (slope + (1 - slope) × ratio)` about
`cerebral_reference_perfusion_pressure = 95 mmHg`,
`cerebral_autoregulation_residual_slope = 0.2`) and the asymmetric
decline/recovery first-order cerebral-flow-index dynamics are **retained
unchanged**. The cerebral-flow index (CFI) remains a **normalized research
proxy**—not measured CBF, MCA velocity, or a Doppler reconstruction.

## Retained equations (unchanged by Stage 1.1)

- Preload/contractility stroke volume:
  `SV = stroke_volume_max × contractility × Vc / (Vc + stroke_volume_half_volume)`
  with the sympathetic contractility term and its lower bound.
- Bounded cerebral pressure-autoregulation curve (above).
- Chronotropic HR assembly (rest + cardiac-sympathetic + vagal + exertion,
  clipped to [30, 220] bpm), including the unidentified
  cardiac-sympathetic/vagal gain split at fixed total gain.
- Muscle-pump transfer and sustained-contraction venous impediment.
- Metabolic capacity, oxygen extraction, and functional-capacity constructs.
- Phenomenological exertional-load / delayed-stress / PEM cascade.

## Parameter classification

Stage 1.1 adds parameters in both registry provenance classes, and the
distinction is part of the design:

- **Literature-anchored (group-level, scenario-grade):** the 40 mmHg ETCO2
  reference and the approximately 0.035/mmHg cerebral CO2-reactivity
  magnitude are consistent with published cerebral vasomotor CO2-reactivity
  ranges; the 25/25/50 regional flow partition is consistent with published
  group-level regional flow distributions. These anchor *scenarios*, not
  patients.
- **Computational operating points / calibration assumptions:** the 0.25/0.75
  aortic/carotid weights, the 0 and 25 cm sensor heights, the 27 cm brain
  height, the fixed 5 mmHg effective cerebral outflow pressure, the ±15 mmHg
  CO2 extrapolation limit, the 0 cm other-systemic hydrostatic height, and
  all doubled/halved resistance re-partitions. None of these is a direct
  clinical measurement.

Supported ranges remain deterministic sensitivity/scenario ranges, not
confidence intervals or population distributions.

## Explicit non-scope

Stage 1.1 contains **no synthetic wearable dataset, no synthetic patient
cohort, no TSFM or other machine-learning component, and no Stage 2 or
Stage 3 work**. The deterministic seed remains metadata; no random numbers
are consumed. Registry, declarative-package, and validation-record
synchronization for the 0.3.0 revision is **complete** (strict traceability
audit 0 errors/0 warnings/0 infos; strict OCPE validation 0 errors/0
warnings); readiness is assessed in `readiness-assessment.md`.
