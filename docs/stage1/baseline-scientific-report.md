# Stage 1 baseline scientific report

## Scope and reproducibility

This report describes the unmodified implementation at commit `47923223d4cf2e8a9c6a1ae8cff485b9d4327dc9` on `research/initial-disease-modeling-framework`. The numerical core is `src/ocpe_disease_models/models/shared/model.py`; OCPE supplies semantic validation, not a numerical solver. The pinned OCPE commit is `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`.

The archived baseline is under `validation/baseline/stage0/`. It contains the original regression fixture, original validation snapshot, dependency versions, and a fresh test log. The fresh source-checkout run gave **230 passed, 1 skipped in 103.99 s**. The skip is the optional upstream-checkout comparison because the test expects `/mnt/agents/open-computational-physiology-engine`; it is not a physiological pass. The previously committed report instead records 231 passes under its earlier environment. Strict traceability and strict OCPE package validation each completed with zero errors and zero warnings.

Installation with `pip install -e '.[dev]'` failed before model execution because Hatch rejects the pinned direct reference unless `tool.hatch.metadata.allow-direct-references` is enabled. This packaging defect is independent of the physiological audit and is corrected separately in Stage 1.

## Computational domain

The model is deterministic and beat-averaged. Time is seconds, volumes mL, pressures mmHg, flows mL/s, resistances mmHg·s/mL, compliances mL/mmHg, and heart rate beats/min. DOP853 integrates the equations. All blood volumes below are **stressed-volume computational compartments**, not measured total regional blood volumes.

### Original states

| Index | State | Unit | Meaning |
|---:|---|---|---|
| 0 | `arterial_volume` ($V_a$) | mL | Arterial stressed volume |
| 1 | `central_venous_volume` ($V_c$) | mL | Central venous stressed volume and cardiac-preload proxy |
| 2 | `peripheral_venous_volume` ($V_p$) | mL | Single aggregated peripheral venous stressed volume |
| 3 | `sympathetic_state` ($S$) | 1 | Shared baroreflex effector state |
| 4 | `exertional_load` ($L$) | 1 | Phenomenological exertional stress dose |
| 5 | `delayed_stress` ($D$) | 1 | Delayed exertional stress |
| 6 | `pem_severity` ($PEM$) | 1 | Normalized post-exertional malaise severity |
| 7 | `cerebral_flow_index` ($CFI$) | 1 | Normalized cerebral-flow proxy, not a measured flow |

### Original equations

Pressure–volume relations (EQ-CV-001):

$$P_a=V_a/C_a,\qquad P_c=V_c/C_c,\qquad P_p=V_p/C_p.$$

Systemic and venous flows (EQ-CV-002 and EQ-ORT-001):

$$Q_{sys}=\max\left(0,\frac{P_a-P_p}{R_{sys,eff}}\right),$$
$$Q_{vr}=\max\left(0,\frac{P_p-P_c-G u}{R_{vr}}\right).$$

Here $u\in[0,1]$ is normalized upright input. The gravity term is a pressure opposition, not an angle-specific hydrostatic solution or an explicit pooling flux.

Conservative volume balances (EQ-CV-003):

$$\dot V_a=Q_{co}-Q_{sys},\qquad \dot V_c=Q_{vr}-Q_{co},\qquad \dot V_p=Q_{sys}-Q_{vr}.$$

Thus $\dot V_a+\dot V_c+\dot V_p=0$ exactly at the RHS level.

Cardiac approximation (EQ-CV-004/005):

$$E=\max[0.2,1+k_E(S-0.5)],$$
$$SV=SV_{max}E\frac{V_c}{V_c+K_{SV}},\qquad Q_{co}=\frac{HR}{60}SV.$$

Baroreflex and chronotropy (EQ-AUT-001/002/003):

$$S_{target}=\sigma\left(\frac{P_{set}-P_a}{\sigma_P}\right),\qquad \dot S=\frac{S_{target}-S}{\tau_S},$$
$$HR=\operatorname{clip}(HR_0+g_{HR}S+g_{ex}eC,30,220).$$

The sigmoid argument is clipped to $[-40,40]$. The same $S$ controls heart rate, contractility, and systemic resistance.

Vascular regulation (EQ-VASC-001):

$$R_{sys,eff}=\max\left[0.1,R_{sys}\{1+g_R(S-0.5)\}\{1-k_{ex}e\}\right].$$

Cerebral proxy (EQ-CBF-001/002):

$$CFI_{target}=\left[\max(0,P_a/P_{set})\right]^\alpha(1-\beta u),$$
$$\dot{CFI}=\frac{CFI_{target}-CFI}{\tau_{CBF}},$$

with separate decline and recovery time constants. There is no cerebral perfusion pressure, hydrostatic heart–brain correction, CO₂ state, or explicit cerebrovascular resistance.

Exertion and recovery (EQ-MET-001/002 and EQ-RCV-001–004) remain outside the cardiovascular redesign:

$$C=\max[0.05,C_0(1-k_C PEM)],$$
$$\dot L=(e/C-L)/\tau_L,\qquad \dot D=(L-D)/\tau_D,$$
$$PEM_{target}=\min\left[1,g_{PEM}\max\left(0,\frac{D-D_{threshold}}{1-D_{threshold}}\right)\right],$$
$$\dot{PEM}=(PEM_{target}-PEM)/\tau_{PEM}.$$

Onset and recovery constants differ. These are phenomenological temporal constructs, not molecular mechanisms.

## Original parameter audit

Every nominal value is an executable research assumption unless the registry says otherwise. Ranges are deterministic sensitivity ranges, not population intervals or probability distributions.

| Model field | Healthy value | Unit | Classification / principal limitation |
|---|---:|---|---|
| `arterial_compliance` | 1.5 | mL/mmHg | Assumed operating point |
| `central_venous_compliance` | 140 | mL/mmHg | Assumed operating point |
| `peripheral_venous_compliance` | 120 | mL/mmHg | Assumed; hEDS scenario 140 is exploratory |
| `systemic_resistance` | 1.1020408163 | mmHg·s/mL | Assumed aggregate resistance |
| `venous_return_resistance` | 0.0612244898 | mmHg·s/mL | Assumed aggregate resistance |
| `resistance_sympathetic_gain` | 0.8 | 1 | Assumed/calibrated; disease overrides |
| `gravity_pressure_offset` | 8 | mmHg | Phenomenological orthostatic opposition |
| `arterial_volume_initial` | 150 | mL | Assumed stressed volume |
| `central_venous_volume_initial` | 700 | mL | Assumed stressed volume/preload proxy |
| `peripheral_venous_volume_initial` | 1200 | mL | Assumed stressed volume |
| `blood_volume_factor` | 1 | 1 | Scenario multiplier, not measured blood volume |
| `stroke_volume_max` | 100 | mL/beat | Assumed saturation scale |
| `stroke_volume_half_volume` | 300 | mL | Assumed preload-proxy half-saturation |
| `contractility_sympathetic_gain` | 0.25 | 1 | Assumed gain |
| `heart_rate_base` | 50 | bpm | Intercept, not measured intrinsic HR |
| `heart_rate_sympathetic_gain` | 40 | bpm | Calibrated chronotropic gain |
| `baroreflex_pressure_setpoint` | 100 | mmHg | Assumed operating point |
| `baroreflex_pressure_scale` | 2 | mmHg | Calibrated sigmoid scale |
| `sympathetic_time_constant` | 4 | s | Assumed shared effector lag |
| `exercise_heart_rate_gain` | 70 | bpm | Assumed exertional chronotropy |
| `exercise_resistance_reduction` | 0.30 | 1 | Assumed aggregate exercise vasodilation |
| `cerebral_pressure_exponent` | 0.8 | 1 | Phenomenological pressure dependence |
| `cerebral_orthostatic_impairment` | 0 | 1 | Disease-scenario multiplier |
| `cerebral_decline_time_constant` | 5 | s | Assumed lag |
| `cerebral_recovery_time_constant` | 12 | s | Assumed lag; ME/CFS override 240 s |
| `baseline_metabolic_capacity` | 1 | 1 | Normalized construct |
| `oxygen_extraction_fraction` | 0.78 | 1 | Normalized/assumed extraction |
| `pem_capacity_penalty` | 0.5 | 1 | Calibrated phenomenological penalty |
| `pem_extraction_penalty` | 0.10 | 1 | Calibrated phenomenological penalty |
| `exertional_load_time_constant` | 1800 | s | Phenomenological |
| `delayed_stress_time_constant` | 21600 | s | Phenomenological |
| `pem_onset_time_constant` | 86400 | s | Phenomenological |
| `pem_recovery_time_constant` | 172800 | s | Phenomenological |
| `pem_trigger_threshold` | 99 | 1 | Healthy value disables PEM by construction |
| `pem_response_gain` | 0 | 1 | Healthy value disables PEM by construction |

The complete machine-readable provenance, dependencies, phenotype values, range exceptions, calibration status, and uncertainty statements are in `literature/parameter_registry.yaml`.

## Evidence supporting the original structure

- Closed-loop conservative compartments, resistance-driven flow, preload-dependent stroke volume, and pressure-feedback control are established reduced-order modeling devices (REF-GEDDES-2022; REF-FU-2018).
- Orthostatic venous pooling and impaired vascular compensation are supported human physiological mechanisms, but the original single gravity offset is phenomenological (CLM-POTS-POOLING evidence chain; REF-STEWART-2003; REF-LOW-2009).
- The disease configurations are scenario calibrations. Threshold agreement is not independent validation and does not identify patient subtypes.
- The PEM cascade reproduces selected temporal features only; it does not assert inflammatory, metabolic, or mitochondrial causality.

## Baseline limitations requiring remediation

1. **Regional pooling is not identifiable.** Splanchnic and lower-limb stressed volumes, compliances, arterial supplies, and venous returns are aggregated. Human tilt evidence shows that these regions do not behave identically.
2. **Autonomic pathways are conflated.** One state drives chronotropy, contractility, and vasoconstriction. Fast vagal and slower cardiac/vascular sympathetic effects cannot be represented independently.
3. **No explicit muscle pump exists.** Exertion changes HR and resistance but does not represent rhythmic muscle-emptying flow or sustained-contraction impediment. Supine exertion and upright walking therefore lack an important distinction.
4. **The cerebral target is systemic-pressure-only.** It omits central venous/back pressure and the orthostatic heart–brain hydrostatic correction. Its exponent is not a validated autoregulation model.
5. **Preload remains a proxy.** Central venous stressed volume is not ventricular end-diastolic volume. A pressure–volume cardiac model is not justified merely to make the diagram more complete.
6. **Blood-volume regulation is static.** `blood_volume_factor` scales initial stressed volumes; renal, endocrine, unstressed-volume, and interstitial-fluid dynamics are absent.
7. **Flow clipping can hide regime failure.** Nonnegative flow constraints prevent reverse flow but can produce collapse-like solutions. Conservation and numerical convergence do not establish that those solutions are physiological.
8. **Exercise vasodilation is aggregate.** Applying one resistance reduction to all beds cannot distinguish exercising muscle from splanchnic vascular control.

## Existing validation interpretation

The original seven-layer snapshot reports all layers passing. The fresh baseline confirms software execution, volume conservation, local numerical convergence, declared physiological directionality, phenotype scenarios, empirical plausibility anchors, deterministic sensitivity checks, and traceability. These checks do not independently validate the anatomical aggregation, parameter magnitudes, disease mechanisms, or clinical use. Stage 1 therefore treats them as regression and internal-consistency evidence, not proof of physiological truth.
