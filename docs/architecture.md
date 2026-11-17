# Computational architecture

## Design decision and upstream boundary

The assignment calls for OCPE-backed simulation, but inspection of the pinned OCPE 0.1 revision shows that it is a specification and semantic-interoperability engine, not a numerical simulator. Its historical solver was archived during commit `64ef9e296b12e21b1f4909f2c46dc0d5e25169e7`. This repository therefore uses a deliberate split rather than claiming a nonexistent upstream numerical capability:

| Responsibility | Owner |
|---|---|
| CURIEs, quantities, concepts, functional forms, model specifications, units, evidence/reference integrity, observation schemas, strict package validation | Pinned upstream OCPE |
| Executable ODEs, initial conditions, solver settings, phenotype composition, protocols, compact simulation traces | `ocpe-disease-models` |
| Disease evidence, equations, parameters, implementations, validation and simulation provenance | `ocpe-disease-models` registries |
| Observation unit/name adaptation and strict OCPE record validation | Adapter and observation-mapping interfaces |

OCPE is pinned at `3f04b6f85566fbd4faa2fd8c0e8bdfe52750235d`. Upstream is not modified or vendored. The local `ocpe/packages/disease-models` directory is a domain package, not a copy of the engine.

## Five modeling layers

```text
Protocols: rest | graded passive tilt (30/45/60/70 deg) | tilt recovery
           with tilt-back | active standing + sustained quiet standing |
           inactive standing | light rhythmic activity | walking |
           sustained contraction | cerebral CO2 isolation protocols |
           single exertion | seven-day repeated exertion/recovery
                         │
                         ▼
Layer 4: dynamic stress and recovery states
                         │
Layer 1: shared cardiovascular/autonomic core ◄── Layer 2: mechanism parameters
                         │                              │
                         │                    Layer 3: phenotype YAML composition
                         ▼
Latent states and derived physiological outputs
                         │
                         ▼
Layer 5: explicit observation mapping ──► strict OCPE observation records
                         │
                         ▼
Small validation traces + provenance + independently reported validation
```

1. **Core physiology (Stage 1.1 revision, model version 0.3.0).** Five conserved stressed-volume compartments (arterial, central venous, splanchnic venous, lower-limb venous, and one residual other-systemic venous compartment) with a 25/25/50 baseline flow partition and 2550 mL healthy total stressed volume; regional resistance-driven flows; preload/contractility stroke volume; separate aortic and carotid baroreceptor sensors feeding one integrated weighted baroreflex; explicit `tilt_angle_deg` posture geometry with sin-scaled hydrostatic heights; a declared per-segment end-tidal CO2 input acting on the cerebral target; and three differentiated autonomic effector states. The Stage 1.1 design record, decision log, validation matrix, and readiness assessment are in `docs/stage1-1/`; the Stage 1 design gate and migration record are in `docs/stage1/revised-physiological-architecture.md`; the audited original architecture is preserved in `docs/stage1/baseline-scientific-report.md`. A deterministic 0.3.0 scientific scenario comparison matrix has been executed (`validation/stage1-1/scientific-comparison-matrix.md`), including preserved negative results (eight Zaidi CO/SV MISSes; five sustained-HR criterion FAILs); release validation (full test suite, strict traceability, strict OCPE package validation, fixtures) is executed at tested commit `942713ef720ad0e801e71bf9bc78405cd844a739` — full suite 327 passed, 1 skipped, 6 xfailed, 2 warnings in 341.60s, with all seven layer execution statuses PASS and the overall seven-layer scientific status **FAIL** from the six preserved strict phenotype xfails. Validation-suite results quoted for Stage 1 remain bound to the 0.2.0 tested commit as history.
2. **Disease mechanisms.** Parameterized reductions in volume or vascular compensation, altered chronotropic feedback, exploratory venous compliance, cerebral impairment, oxygen extraction, and PEM recovery.
3. **Phenotypes.** YAML records combine coherent mechanisms, evidence links, parameter overrides, maturity, and limitations. Conflicting ad hoc composition raises an error; it never depends on override order.
4. **Stress and recovery.** Declared posture (explicit tilt angle, or the legacy normalized upright fraction via `arcsin` migration), exertion, rhythmic-muscle-activity, sustained-contraction, and end-tidal CO2 inputs drive ordinary differential equations; the rhythmic and sustained muscle inputs are independent of metabolic exertion and of each other, and ETCO2 is independent of posture. PEM uses an explicit delayed-state approximation rather than an immediate fatigue multiplier.
5. **Observations.** Latent/derived values remain distinct from observation records. The mapper resolves native output names and units before strict OCPE validation.

## State and input model

Time is seconds, volumes are mL, pressures are mmHg, and internal flows are mL/s. Heart rate is beats/min and exported cardiac output is L/min.

| State | Meaning | Initial condition |
|---|---|---|
| `arterial_volume` | Arterial stressed volume | `arterial_volume_initial × blood_volume_factor` |
| `central_venous_volume` | Central venous stressed volume/preload surrogate | `central_venous_volume_initial × blood_volume_factor` |
| `splanchnic_venous_volume` | Splanchnic venous stressed volume | `splanchnic_venous_pressure_initial × splanchnic_venous_compliance × blood_volume_factor` |
| `lower_limb_venous_volume` | Lower-limb venous stressed volume | `lower_limb_venous_pressure_initial × lower_limb_venous_compliance × blood_volume_factor` |
| `other_systemic_venous_volume` | Residual other-systemic venous stressed volume (Stage 1.1) | `other_systemic_venous_pressure_initial × other_systemic_venous_compliance × blood_volume_factor` |
| `cardiac_sympathetic_state` | Cardiac sympathetic effector state | 0.5 |
| `vascular_sympathetic_state` | Vascular sympathetic effector state | 0.5 |
| `vagal_state` | Vagal cardiac effector state | 0.5 |
| `exertional_load` | Capacity-normalized exertional load | 0 |
| `delayed_stress` | Delayed exertional stress | 0 |
| `pem_severity` | Normalized phenomenological PEM severity | 0 |
| `cerebral_flow_index` | Normalized cerebral-flow approximation | Computed from the CPP pressure curve at the configured initial pressures |

The former single `sympathetic_state` is no longer a state or control input; a value with that name is exported only as a labeled compatibility summary equal to the arithmetic mean of the cardiac and vascular sympathetic states.

`ProtocolSegment` supplies posture plus four further declared inputs—`exertion`, `rhythmic_muscle_activity`, `sustained_muscle_contraction`, and `end_tidal_co2_mmHg`—over ordered, non-overlapping intervals. Posture is declared either as an explicit `tilt_angle_deg` in [0, 90] or as the legacy normalized `upright` fraction, which is migrated through `degrees(arcsin(upright))`; specifying both is an error. During `transition_duration` only the angle is linearly interpolated from the previous segment's angle; every other input remains piecewise constant. Hydrostatic terms use heights in centimetres converted at 0.7356 mmHg/cm and scaled by sin(tilt angle), so the supine limit is exactly zero. The rhythmic and sustained muscle inputs are declared independently of metabolic exertion, so supine rest, graded passive tilt, active standing, sustained quiet standing, inactive standing, light rhythmic activity, walking, and sustained contraction are distinct protocol conditions. A declared ETCO2 segment value is required for any hypocapnia scenario—posture never infers hypocapnia—and the exertion input is normalized, not a measured watt or VO2 value.

## Conservative hemodynamics

The implementation follows `EQ-CV-001` through `EQ-CV-005`, `EQ-ORT-001`, and `EQ-MP-001`/`EQ-MP-002`:

```text
Pa = Va/Ca   Pc = Vc/Cc   Ps = Vs/Cs   Pl = Vl/Cl   Po = Vo/Co
hydro(h) = 0.7356 × h × sin(tilt_angle)
Qs,a = max(0, (Pa-Ps)/Rs,a_eff)   Ql,a = max(0, (Pa-Pl)/Rl,a_eff)   Qo,a = max(0, (Pa-Po)/Ro,a_eff)
Qs,v = max(0, (Ps-Pc-hydro(Hs))/Rs,v)
Qpump = f_pump × SV_pump × η_pump × rhythmic × Vl/(Vl+K_pump)
Ql,v = max(0, (Pl-Pc-hydro(Hl))/Rl,v_eff) + Qpump
Qo,v = max(0, (Po-Pc-hydro(Ho))/Ro,v)
Qco  = HR/60 × SV

dVa/dt = Qco-Qs,a-Ql,a-Qo,a
dVc/dt = Qs,v+Ql,v+Qo,v-Qco
dVs/dt = Qs,a-Qs,v
dVl/dt = Ql,a-Ql,v
dVo/dt = Qo,a-Qo,v
```

Consequently `d(Va+Vc+Vs+Vl+Vo)/dt = 0` analytically; the five volume derivatives telescope exactly. The healthy baseline partitions systemic flow 25% splanchnic / 25% lower-limb / 50% other-systemic at a 2550 mL total stressed volume, with total conductance preserved from Stage 1 by doubling the splanchnic/lower-limb resistances and assigning the former values to the other-systemic path. The muscle pump transfers volume from the lower-limb to the central venous compartment—it does not create blood—and the pump flow is added outside the nonnegative passive-gradient floor so a negative passive gradient cannot cancel a declared contraction. Sustained contraction instead raises lower-limb venous resistance. Nonnegative flow clamps are constitutive boundary choices, not evidence of venous valve or collapsible-vessel behavior.

`blood_volume_factor` scales all five initial volumes, but uniform volume scaling alone does not preserve the exact supine fixed point; each phenotype derives its regional resistances and baroreflex pressure setpoints so that its complete initial state is a fixed point (the Stage 1 record tested all ten configurations with maximum absolute RHS component below 1e-9; the equivalent 0.3.0 check is executed in the mathematical layer — 45 passed, including exact five-volume telescoping and exact supine fixed points of all registered configurations).

## Autonomic, cerebral, metabolic, and recovery subsystems

- `EQ-AUT-001..003`: a sigmoidal baroreflex target driven by an integrated weighted error from two separate sensors—aortic (heart level, default height 0 cm) and carotid sinus (default 25 cm)—each with its own pressure setpoint and scale, integrated with default weights 0.25 aortic / 0.75 carotid (validated to sum to 1); first-order cardiac-sympathetic, vascular-sympathetic, and vagal lags (distinct time constants, fast vagal versus slower sympathetic); and HR from resting, cardiac-sympathetic, vagal, and exertion terms. The cardiac-sympathetic/vagal chronotropic gain split at fixed total gain is unidentified by current evidence and is sensitivity-tested explicitly. Brain-level pressure (default 27 cm height) is a separate parameter used only by the cerebral path; it is not a baroreflex sensor.
- `EQ-VASC-001`: regional splanchnic, lower-limb, and other-systemic arterial resistances modulated by the vascular sympathetic state; exertional vasodilation applies to the lower-limb arterial path only.
- `EQ-CBF-001..002`: cerebral perfusion pressure (brain-level arterial pressure minus a fixed effective cerebral outflow pressure of 5 mmHg—explicitly neither thoracic central venous pressure nor a resolved intracranial pressure) feeding the retained bounded autoregulation proxy and an asymmetric decline/recovery cerebral-flow index. A declared segment end-tidal CO2 value modulates the cerebral target by exp(0.035 × clip(ETCO2 − 40 mmHg, ±15 mmHg)); ETCO2 defaults to the 40 mmHg reference, is not exact PaCO2, and posture never infers hypocapnia. The index is not a Doppler reconstruction and lacks vascular territories.
- `EQ-MET-001..002`: normalized metabolic and functional capacity with oxygen extraction. These are not direct mitochondrial or VO2 states.
- `EQ-RCV-001..004`: exertional load, delayed stress, thresholded PEM target, and asymmetric onset/recovery. The equations are phenomenological; they do not assert a molecular cause.

Registry synchronization to the 0.3.0 state, equation, and parameter names and counts is complete and verified by the strict traceability audit (0 errors/0 warnings/0 infos; see `docs/stage1-1/readiness-assessment.md`); the current record is 22 equation records and 68 parameter fields, while the Stage 1 record of 20 equation records and 52 parameter fields describes the 0.2.0 tested commit as history.

## Numerical execution

`ComputationalPatient.simulate()` uses SciPy `solve_ivp` with DOP853, protocol-specific output sampling, maximum step, relative tolerance, and absolute tolerance. It rejects empty/overlapping protocols, invalid parameter domains, failed solver returns, non-finite states, negative stressed volumes, autonomic states outside [0, 1], and cerebral-flow-index values outside their declared bounds. Convergence tests independently tighten tolerances and step size. The current model is deterministic; the recorded seed is metadata for forward compatibility and no random numbers are consumed.

Each `SimulationResult` stores arrays plus parameters, protocol, configuration SHA-256, model/OCPE versions, Python/NumPy/SciPy versions, solver settings, and scientific status. This makes an output trace auditable without turning it into a large dataset.

## Validation architecture

Seven validation layers are separate from the five modeling layers. Software, mathematical, physiological, disease-phenotype, empirical, sensitivity/uncertainty, and scientific-traceability results cannot substitute for each other. Registry IDs connect tests to mechanisms and outputs; `scripts/run_validation.py` fails on an empty required test selection. Maturity M0–M4 is assigned per mechanism/phenotype, not inferred from suite success. Under the Stage 1 (0.2.0) record, the mathematical layer tested the exact supine fixed point of every one of the ten registered configurations and exact four-volume conservation including walking and sustained-contraction protocols; the disease-phenotype layer applied the **sustained** orthostatic criterion (mean HR over the final 120 s of the upright window minus the supine baseline), with the peak first-300-s rise reported separately as a secondary metric. The Stage 1.1 (0.3.0) execution is complete at tested commit `942713ef720ad0e801e71bf9bc78405cd844a739`: the mathematical layer demonstrates exact **five-volume** conservation and twelve-state fixed points across the graded-tilt, active-standing, tilt-back, and cerebral CO2 protocol families (45 passed), using the predefined reporting windows in `docs/stage1-1/validation-matrix.md`; all seven layer execution statuses are PASS, while the disease-phenotype layer's six strict expected failures keep the overall seven-layer scientific status **FAIL**. The deterministic scientific scenario matrix reports its results—including preserved misses and criterion failures—in `validation/stage1-1/`.

## Source-layout and packaging limits

The wheel contains Python code, while phenotype/protocol/domain-package discovery currently expects a source checkout or explicit root/package path. `OCPE_DM_ROOT` resolves simulation configuration discovery; OCPE adapter callers may need an explicit `package_dir` in a wheel-only deployment. This is an unresolved packaging limitation, not silent portable data packaging.
